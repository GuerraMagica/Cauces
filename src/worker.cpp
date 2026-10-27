#include "pipeline.hpp"
#include "scratch.hpp"
#include "wav.hpp"
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
    std::ifstream file(path,std::ios::binary);if(!file)throw std::runtime_error("No se puede leer un archivo para verificar su integridad.");
    CC_SHA256_CTX ctx;CC_SHA256_Init(&ctx);std::array<char,65536> block{};
    while(file){file.read(block.data(),block.size());auto count=file.gcount();if(count>0)CC_SHA256_Update(&ctx,block.data(),CC_LONG(count));}
    if(!file.eof())throw std::runtime_error("Fallo de lectura al verificar integridad.");
    unsigned char bytes[CC_SHA256_DIGEST_LENGTH];CC_SHA256_Final(bytes,&ctx);
    std::ostringstream out;out<<std::hex<<std::setfill('0');for(auto b:bytes)out<<std::setw(2)<<int(b);return out.str();
}
void verify_models(const fs::path& root){
    const std::pair<const char*,const char*> expected[]{
        {"separator.onnx","ac763dcb1010ea8a23103ee799ceb61f394e91bd7a8280e1ef34d3f710ea5a82"},
        {"refiner.onnx","4d4d38f4ca538924118b79daf5e24f293fec6f04e5a6eca2aa36e04c8f23f9cb"},
        {"weights.bin","b1491a04c97baaa30ebecfc7290fc70daa9404774ace4495065f5243b4188889"}};
    for(const auto& item:expected)if(digest(root/item.first)!=item.second)throw std::runtime_error("La copia local del modelo está dañada; vuelve a copiar la app completa.");
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
    try{
        auto target=destination/(name+"_separado");
        if(fs::exists(fs::symlink_status(target)))throw std::runtime_error("Ya existe una exportación con ese nombre. Elige otra carpeta.");
        uint64_t required=16*1024*1024;
        for(const auto& source:stems)required+=fs::file_size(source);
        if(fs::space(destination).available<required)throw std::runtime_error("No hay espacio suficiente para exportar los tres stems.");
        const char* labels[]{"voz_1","voz_2","residual"};
        for(size_t i=0;i<3;++i){
            auto out=staging/(name+"_"+labels[i]+".wav");fs::copy_file(stems[i],out,fs::copy_options::none);
            int fd=::open(out.c_str(),O_RDONLY|O_NOFOLLOW);if(fd<0)throw std::runtime_error("No se puede verificar la exportación.");
            int synced=::fsync(fd);::close(fd);if(synced)throw std::runtime_error("No se puede finalizar la exportación.");
            ds::inspect_wav(out);if(digest(stems[i])!=digest(out))throw std::runtime_error("La copia de un stem no coincide con su origen.");
        }
        if(::renameatx_np(AT_FDCWD,staging.c_str(),AT_FDCWD,target.c_str(),RENAME_EXCL))throw std::runtime_error("No se puede publicar la exportación; el destino puede existir ya.");
        return target;
    }catch(...){std::error_code ec;fs::remove_all(staging,ec);throw;}
}
}
int main(int argc,char** argv){
    std::string models;int threads=4;
    for(int i=1;i<argc;++i){std::string arg=argv[i];if(arg=="--models"&&i+1<argc)models=argv[++i];else if(arg=="--threads"&&i+1<argc)threads=std::stoi(argv[++i]);else return 2;}
    if(models.empty())return 2;
    std::unique_ptr<ds::Models> engine;std::unique_ptr<ds::ScratchSpace> workspace;
    std::array<fs::path,3> stems;std::string source_name;
    emit({{"type","ready"},{"runtime",ds::Models::version()}});std::string line;
    while(std::getline(std::cin,line)){
        json id=nullptr;
        try{
            if(line.size()>1048576)throw std::runtime_error("Comando demasiado largo.");
            auto command=json::parse(line);id=command.value("id",json(nullptr));auto cmd=command.at("cmd").get<std::string>();
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
                if(!engine){emit({{"type","progress"},{"id",id},{"value",0},{"stage","Cargando y verificando modelos"}});verify_models(models);engine=std::make_unique<ds::Models>(models,threads);}
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
