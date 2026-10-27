#include "pipeline.hpp"
#include "scratch.hpp"
#include "wav.hpp"
#include "security.h"
#include <nlohmann/json.hpp>
#include <CommonCrypto/CommonDigest.h>
#include <array>
#include <chrono>
#include <cstdio>
#include <fcntl.h>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <sys/stat.h>
#include <unistd.h>
namespace fs=std::filesystem;
using json=nlohmann::json;
namespace {
void emit(const json& event){std::cout<<event.dump()<<'\n'<<std::flush;}
std::string digest(const fs::path& path){
    int fd=::open(path.c_str(),O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);struct stat st{};
    if(fd<0||::fstat(fd,&st)||!S_ISREG(st.st_mode)||st.st_size<0||st.st_size>1024LL*1024*1024){if(fd>=0)::close(fd);throw std::runtime_error("No se puede verificar un archivo regular de hasta 1 GiB.");}
    CC_SHA256_CTX ctx;CC_SHA256_Init(&ctx);std::array<char,65536> block{};off_t total=0;
    for(;;){auto n=::read(fd,block.data(),block.size());if(n<0&&errno==EINTR)continue;if(n<0||n>st.st_size-total){::close(fd);throw std::runtime_error("Fallo de lectura o archivo cambiado durante verificación.");}if(!n)break;total+=n;CC_SHA256_Update(&ctx,block.data(),CC_LONG(n));}
    ::close(fd);if(total!=st.st_size)throw std::runtime_error("Archivo cambiado durante verificación.");
    unsigned char bytes[CC_SHA256_DIGEST_LENGTH];CC_SHA256_Final(bytes,&ctx);
    std::ostringstream out;out<<std::hex<<std::setfill('0');for(auto b:bytes)out<<std::setw(2)<<int(b);return out.str();
}
json info_json(const ds::WavInfo& info){
    json out{{"rate",info.rate},{"channels",info.channels},{"frames",info.frames},{"bits",info.bits},{"duration",double(info.frames)/info.rate}};
    if(info.time_reference)out["time_reference"]=std::to_string(*info.time_reference);return out;
}
struct SourceIdentity {
    struct stat stat{};std::string sha;
    explicit SourceIdentity(const fs::path& path){if(::stat(path.c_str(),&stat))throw std::runtime_error("No se puede leer el original.");sha=digest(path);}
    bool matches(const fs::path& path)const{
        struct stat after{};
        return !::stat(path.c_str(),&after)&&stat.st_dev==after.st_dev&&stat.st_ino==after.st_ino&&stat.st_size==after.st_size&&stat.st_mtimespec.tv_sec==after.st_mtimespec.tv_sec&&stat.st_mtimespec.tv_nsec==after.st_mtimespec.tv_nsec&&sha==digest(path);
    }
};
fs::path export_result(const std::array<fs::path,3>& stems,const fs::path& destination,const std::string& name,const fs::path& staging){
    if(!fs::is_directory(destination))throw std::runtime_error("El destino no es una carpeta accesible.");
    auto status=fs::symlink_status(staging);struct stat st{};
    if(!fs::is_directory(status)||fs::is_symlink(status)||staging.filename().string().rfind(".export-",0)!=0||
       fs::canonical(staging.parent_path())!=fs::canonical(destination)||!fs::is_empty(staging)||
       ::lstat(staging.c_str(),&st)||st.st_uid!=::getuid()||(st.st_mode&077)!=0)
        throw std::runtime_error("El temporal de exportación no es una carpeta privada válida.");
    char diagnostic[512]{};
    std::unique_ptr<cauces_directory,decltype(&cauces_directory_destroy)> owned(cauces_directory_adopt(staging.c_str(),diagnostic,sizeof(diagnostic)),cauces_directory_destroy);
    if(!owned)throw std::runtime_error(diagnostic);
    {
        auto target=destination/(name+"_separado");
        if(fs::exists(fs::symlink_status(target)))throw std::runtime_error("Ya existe una exportación con ese nombre. Elige otra carpeta.");
        uint64_t required=16*1024*1024;
        for(const auto& source:stems)required+=fs::file_size(source);
        if(fs::space(destination).available<required)throw std::runtime_error("No hay espacio suficiente para exportar los tres stems.");
        const char* labels[]{"voz_1","voz_2","residual"};
        for(size_t i=0;i<3;++i){
            std::string filename=name+"_"+labels[i]+".wav";
            if(cauces_directory_copy(owned.get(),stems[i].c_str(),filename.c_str(),diagnostic,sizeof(diagnostic)))throw std::runtime_error(diagnostic);
        }
        if(cauces_directory_publish(owned.get(),(name+"_separado").c_str(),diagnostic,sizeof(diagnostic)))throw std::runtime_error(diagnostic);
        return target;
    }
}
}
// Read and discard oversized lines without ever buffering beyond the protocol cap.
bool read_command(std::istream& input,std::string& line,bool& oversized){
    line.clear();oversized=false;char c;bool any=false;
    while(input.get(c)){any=true;if(c=='\n')return true;if(line.size()<1048576)line+=c;else oversized=true;}
    return any;
}
int main(int argc,char** argv){
    std::string models;int threads=4;
    try {
        for(int i=1;i<argc;++i){
            std::string arg=argv[i];
            if(arg=="--models"&&i+1<argc)models=argv[++i];
            else if(arg=="--threads"&&i+1<argc){size_t used=0;std::string value=argv[++i];threads=std::stoi(value,&used);if(used!=value.size()||threads<1||threads>64)return 2;}
            else return 2;
        }
    }catch(const std::exception&){return 2;}
    if(models.empty())return 2;
    std::unique_ptr<ds::Models> engine;std::unique_ptr<ds::ScratchSpace> workspace;
    std::array<fs::path,3> stems;std::string source_name;
#if defined(__x86_64__)
    const char* architecture="x86_64";
#else
    const char* architecture="arm64";
#endif
    emit({{"type","ready"},{"runtime",ds::Models::version()},{"architecture",architecture}});std::string line;
    bool oversized=false;
    while(read_command(std::cin,line,oversized)){
        json id=nullptr;
        try{
            if(oversized)throw std::runtime_error("Comando demasiado largo.");
            auto command=json::parse(line,[](int depth,json::parse_event_t,json&){if(depth>16)throw std::runtime_error("JSON demasiado anidado.");return true;});
            if(!command.is_object()||!command.contains("id")||!command["id"].is_number_integer()||!command.contains("cmd")||!command["cmd"].is_string())throw std::runtime_error("Esquema de comando inválido.");
            if(command["id"].is_number_unsigned()&&command["id"].get<uint64_t>()>9007199254740991ULL)throw std::runtime_error("Identificador fuera de rango.");
            auto numeric_id=command["id"].get<int64_t>();
            if(numeric_id< -9007199254740991LL||numeric_id>9007199254740991LL)throw std::runtime_error("Identificador fuera de rango.");
            id=numeric_id;auto cmd=command["cmd"].get<std::string>();
            for(const char* key:{"source","workspace","destination","staging"})if(command.contains(key)){
                if(!command[key].is_string())throw std::runtime_error("Ruta inválida.");
                auto path=command[key].get<std::string>();if(path.empty()||path.size()>4096||path.find('\0')!=std::string::npos)throw std::runtime_error("Ruta inválida.");
            }
            if(cmd=="inspect"){
                auto result=info_json(ds::inspect_wav(command.at("source").get<std::string>()));result["type"]="info";result["id"]=id;emit(result);
            }else if(cmd=="separate"){
                stems={};source_name.clear();workspace.reset();fs::path source=command.at("source").get<std::string>();
                SourceIdentity before(source);
                auto info=ds::inspect_wav(source);auto space=fs::space(command.at("workspace").get<std::string>());
                uint64_t required=ds::required_working_space(info);
                if(space.available<required)throw std::runtime_error("No hay espacio suficiente para los temporales. Libera espacio antes de separar.");
                workspace=std::make_unique<ds::ScratchSpace>(command.at("workspace").get<std::string>());
                ds::BufferFactory factory=[&](size_t n){return workspace->allocate(n);};auto audio=ds::read_wav(source,factory);
                if(!before.matches(source))throw std::runtime_error("El archivo original cambió durante la lectura; vuelve a abrirlo.");
                info=audio.info; // Buffer dimensions always come from the same open file as its samples.
                auto started=std::chrono::steady_clock::now();
                if(!engine){emit({{"type","progress"},{"id",id},{"value",0},{"stage","Cargando y verificando modelos"}});engine=std::make_unique<ds::Models>(models,threads);}
                auto loaded=std::chrono::steady_clock::now();
                ds::Pipeline pipeline(engine.get(),factory,[&](double value,const std::string& stage){emit({{"type","progress"},{"id",id},{"value",value*.94},{"stage",stage}});return true;});
                auto output=pipeline.separate(audio.samples->data(),info.frames,info.channels,info.rate);
                if(!before.matches(source))throw std::runtime_error("El archivo original cambió durante la separación; se descartan los resultados.");
                const float* values[]{output.voices[0]->data(),output.voices[1]->data(),output.residual->data()};
                for(int i=0;i<3;++i){stems[i]=workspace->directory()/(std::string("stem-")+std::to_string(i)+".wav");ds::write_wav_exclusive(stems[i],values[i],info.frames,info.rate,info.channels,info.time_reference);}
                source_name=source.stem().string();auto result=info_json(info);result["type"]="result";result["id"]=id;result["stems"]=json::array();
                for(const auto& path:stems)result["stems"].push_back(path.string());
                result["load_seconds"]=std::chrono::duration<double>(loaded-started).count();result["process_seconds"]=std::chrono::duration<double>(std::chrono::steady_clock::now()-loaded).count();result["source_sha256"]=before.sha;emit(result);
            }else if(cmd=="export"){
                if(source_name.empty())throw std::runtime_error("Primero separa un archivo.");auto target=export_result(stems,command.at("destination").get<std::string>(),source_name,command.at("staging").get<std::string>());emit({{"type","exported"},{"id",id},{"directory",target.string()}});
            }else throw std::runtime_error("Comando no reconocido.");
        }catch(const std::exception& e){emit({{"type","error"},{"id",id},{"message",e.what()}});}
    }
}
