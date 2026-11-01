#include "wav.hpp"
#include <algorithm>
#include <array>
#include <cerrno>
#include <cmath>
#include <cstring>
#include <fcntl.h>
#include <limits>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>

namespace ds {
namespace {
uint16_t u16(const unsigned char* p){return uint16_t(p[0])|uint16_t(p[1])<<8;}
uint32_t u32(const unsigned char* p){return uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16|uint32_t(p[3])<<24;}
void put16(std::vector<unsigned char>& out,uint16_t v){out.push_back(v&255);out.push_back(v>>8);}
void put32(std::vector<unsigned char>& out,uint32_t v){for(int i=0;i<4;++i)out.push_back((v>>(8*i))&255);}
void tag(std::vector<unsigned char>& out,const char* text){out.insert(out.end(),text,text+4);}
// Keep one verified descriptor for both the header and the sample data.
// In particular, do not reopen it through /dev/fd: that is separately sandboxed.
class RegularWavFile final {
    int fd_=-1;
    uint64_t length_=0,position_=0;
public:
    explicit RegularWavFile(const std::filesystem::path& path){
        fd_=::open(path.c_str(),O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC);
        if(fd_<0){const int error=errno;throw std::runtime_error("The WAV file could not be opened (OS error "+std::to_string(error)+"). Choose an accessible local file.");}
        struct stat st{};
        if(::fstat(fd_,&st)){
            const int error=errno;::close(fd_);fd_=-1;
            throw std::runtime_error("The WAV file could not be inspected (OS error "+std::to_string(error)+").");
        }
        if(!S_ISREG(st.st_mode)||st.st_size<0){::close(fd_);fd_=-1;throw std::runtime_error("The source is not a readable regular WAV file.");}
        length_=uint64_t(st.st_size);
    }
    ~RegularWavFile(){if(fd_>=0)::close(fd_);}
    RegularWavFile(const RegularWavFile&)=delete;
    RegularWavFile& operator=(const RegularWavFile&)=delete;
    uint64_t size()const{return length_;}
    void seek(uint64_t position){
        if(position>length_)throw std::runtime_error("The WAV file is truncated or could not be read.");
        position_=position;
    }
    void read(unsigned char* dest,size_t count){
        if(uint64_t(count)>length_-position_)throw std::runtime_error("The WAV file is truncated or could not be read.");
        while(count){
            const size_t chunk=std::min(count,size_t(std::numeric_limits<ssize_t>::max()));
            const ssize_t n=::pread(fd_,dest,chunk,static_cast<off_t>(position_));
            if(n<0&&errno==EINTR)continue;
            if(n<0){const int error=errno;throw std::runtime_error("The WAV file could not be read (OS error "+std::to_string(error)+").");}
            if(n==0)throw std::runtime_error("The WAV file is truncated or could not be read.");
            position_+=uint64_t(n);dest+=size_t(n);count-=size_t(n);
        }
    }
};
RegularWavFile open_regular(const std::filesystem::path& path){return RegularWavFile(path);}
void read_exact(RegularWavFile& file,unsigned char* dest,size_t count){file.read(dest,count);}
class Heap final:public Storage{
    std::vector<float> samples;
public:
    explicit Heap(size_t n):samples(n){}
    float* data()override{return samples.data();} size_t size()const override{return samples.size();}
};
void write_all(int fd,const void* buffer,size_t bytes){
    auto p=static_cast<const char*>(buffer);
    while(bytes){ssize_t n=::write(fd,p,bytes);if(n<0&&errno==EINTR)continue;
        if(n<=0)throw std::runtime_error("The WAV file could not be written. Check available disk space and file permissions.");
        bytes-=size_t(n);p+=n;
    }
}
}
static WavInfo parse_header(RegularWavFile& file){
    const auto end=file.size();file.seek(0);
    if(end<12)throw std::runtime_error("The file is not a valid RIFF WAV.");
    std::array<unsigned char,12> header{};read_exact(file,header.data(),12);
    if(std::memcmp(header.data(),"RIFF",4)||std::memcmp(header.data()+8,"WAVE",4))
        throw std::runtime_error("Only RIFF WAV is supported. RF64 and other containers are not supported in this version.");
    uint64_t limit=uint64_t(u32(header.data()+4))+8;
    if(limit<12||limit>uint64_t(end))throw std::runtime_error("The RIFF size does not match the file.");
    WavInfo info;bool have_fmt=false,have_data=false,have_bext=false;
    for(uint64_t pos=12;pos<limit;){
        if(limit-pos<8)throw std::runtime_error("A WAV chunk header is incomplete.");
        file.seek(pos);std::array<unsigned char,8> ch{};read_exact(file,ch.data(),8);
        uint64_t size=u32(ch.data()+4),next=pos+8+size+(size&1);
        if(next>limit)throw std::runtime_error("A WAV chunk extends beyond the file.");
        if(!std::memcmp(ch.data(),"fmt ",4)){
            if(have_fmt||size<16)throw std::runtime_error("The WAV format chunk is duplicated or incomplete.");
            std::array<unsigned char,40> fmt{};read_exact(file,fmt.data(),std::min(size,uint64_t(40)));
            info.format=u16(fmt.data());info.channels=u16(fmt.data()+2);info.rate=int(u32(fmt.data()+4));info.bits=u16(fmt.data()+14);
            if(info.format==0xfffe){
                const unsigned char guid_tail[]{0,0,0,0,0x10,0,0x80,0,0,0xaa,0,0x38,0x9b,0x71};
                if(size<40||u16(fmt.data()+16)<22||u16(fmt.data()+18)!=info.bits||std::memcmp(fmt.data()+26,guid_tail,14))
                    throw std::runtime_error("The extensible WAV format is not supported.");
                info.format=u16(fmt.data()+24);
            }
            if(!((info.format==1&&(info.bits==16||info.bits==24))||(info.format==3&&info.bits==32)))
                throw std::runtime_error("Use a PCM16, PCM24 or float32 WAV file.");
            if(info.channels!=1&&info.channels!=2)throw std::runtime_error("Use mono or identical dual-mono audio.");
            if(info.rate<8000||info.rate>48000)throw std::runtime_error("Sample rates from 8 to 48 kHz are supported.");
            if(u16(fmt.data()+12)!=info.channels*(info.bits/8)||u32(fmt.data()+8)!=uint32_t(info.rate*info.channels*(info.bits/8)))
                throw std::runtime_error("The WAV block alignment or byte rate is not valid.");
            have_fmt=true;
        }else if(!std::memcmp(ch.data(),"data",4)){
            if(have_data)throw std::runtime_error("The WAV file contains multiple audio chunks.");
            info.data_offset=pos+8;info.data_bytes=size;have_data=true;
        }else if(!std::memcmp(ch.data(),"bext",4)){
            if(have_bext||size<602)throw std::runtime_error("BWF metadata is incomplete or duplicated.");
            std::array<unsigned char,602> bext{};read_exact(file,bext.data(),602);
            info.time_reference=uint64_t(u32(bext.data()+338))|(uint64_t(u32(bext.data()+342))<<32);have_bext=true;
        }
        pos=next;
    }
    if(!have_fmt||!have_data)throw std::runtime_error("The WAV file is missing format information or audio samples.");
    size_t align=size_t(info.channels)*(info.bits/8);
    if(info.data_bytes%align)throw std::runtime_error("The audio data contains an incomplete sample.");
    info.frames=size_t(info.data_bytes/align);
    if(!info.frames||info.frames>size_t(info.rate)*1800)throw std::runtime_error("The WAV file is empty or exceeds 30 minutes.");
    return info;
}
WavInfo inspect_wav(const std::filesystem::path& path){
    auto file=open_regular(path);
    return parse_header(file);
}
Audio read_wav(const std::filesystem::path& path,BufferFactory factory){
    auto file=open_regular(path);
    auto info=parse_header(file);size_t size=info.frames*info.channels;
    auto buffer=factory?factory(size):std::make_shared<Heap>(size);
    if(!buffer||buffer->size()!=size||!buffer->data())throw std::runtime_error("There is not enough memory to read the WAV file.");
    file.seek(info.data_offset);size_t bytes=size_t(info.bits/8),align=bytes*info.channels;
    std::vector<unsigned char> block(4096*align);
    for(size_t start=0;start<info.frames;start+=4096){
        size_t n=std::min(size_t(4096),info.frames-start);read_exact(file,block.data(),n*align);
        for(size_t i=0;i<n;++i)for(int c=0;c<info.channels;++c){
            const auto p=block.data()+i*align+c*bytes;float sample;
            if(info.format==3){uint32_t bits=u32(p);std::memcpy(&sample,&bits,4);}
            else if(info.bits==16){sample=float(int16_t(u16(p)))/32768.f;}
            else{uint32_t raw=uint32_t(p[0])|uint32_t(p[1])<<8|uint32_t(p[2])<<16;int32_t signed_value=int32_t(raw<<8)/256;sample=float(signed_value)/8388608.f;}
            buffer->data()[size_t(c)*info.frames+start+i]=sample;
        }
        for(size_t i=0;i<n;++i){
            float left=buffer->data()[start+i];
            if(!std::isfinite(left))throw std::runtime_error("The audio contains NaN or infinite values.");
            if(info.channels==2&&left!=buffer->data()[info.frames+start+i])throw std::runtime_error("True stereo separation is not supported. Use mono or identical dual mono.");
        }
    }
    return {info,buffer};
}
void write_wav_exclusive(const std::filesystem::path& path,const float* mono,size_t frames,int rate,int channels,std::optional<uint64_t> time_reference){
    if((channels!=1&&channels!=2)||rate<8000||rate>48000||!frames||frames>size_t(rate)*1800||!mono)throw std::invalid_argument("The WAV output parameters are not valid.");
    for(size_t i=0;i<frames;++i)if(!std::isfinite(mono[i]))throw std::runtime_error("Nonfinite audio cannot be exported.");
    uint64_t audio_bytes=uint64_t(frames)*channels*4;
    uint64_t riff_size=4+24+12+8+audio_bytes+(time_reference?610:0);
    if(riff_size>UINT32_MAX)throw std::runtime_error("The output exceeds the RIFF size limit.");
    std::vector<unsigned char> header;tag(header,"RIFF");put32(header,uint32_t(riff_size));tag(header,"WAVE");
    tag(header,"fmt ");put32(header,16);put16(header,3);put16(header,uint16_t(channels));put32(header,uint32_t(rate));put32(header,uint32_t(rate*channels*4));put16(header,uint16_t(channels*4));put16(header,32);
    tag(header,"fact");put32(header,4);put32(header,uint32_t(frames));
    if(time_reference){
        tag(header,"bext");put32(header,602);size_t offset=header.size();header.resize(offset+602,0);
        const char description[]="Local dialogue separation";std::memcpy(header.data()+offset,description,sizeof(description)-1);
        const char originator[]="Dialogue Separator";std::memcpy(header.data()+offset+256,originator,sizeof(originator)-1);
        for(int i=0;i<8;++i)header[offset+338+i]=(*time_reference>>(i*8))&255;
    }
    tag(header,"data");put32(header,uint32_t(audio_bytes));
    int fd=::open(path.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW,0600);
    if(fd<0)throw std::runtime_error("The output could not be created. It may already exist or file permission is denied.");
    try{
        write_all(fd,header.data(),header.size());std::vector<float> block(4096*channels);
        for(size_t start=0;start<frames;start+=4096){
            size_t n=std::min(size_t(4096),frames-start);
            for(size_t i=0;i<n;++i)for(int c=0;c<channels;++c)block[i*channels+c]=mono[start+i];
            write_all(fd,block.data(),n*channels*4);
        }
        if(::fsync(fd))throw std::runtime_error("Writing the WAV file could not be completed.");
        if(::close(fd)){fd=-1;throw std::runtime_error("The output WAV file could not be closed.");}fd=-1;
        auto verify=inspect_wav(path);
        if(verify.frames!=frames||verify.channels!=channels||verify.rate!=rate||verify.time_reference!=time_reference)throw std::runtime_error("The exported WAV file failed verification.");
    }catch(...){if(fd>=0)::close(fd);::unlink(path.c_str());throw;}
}
}
