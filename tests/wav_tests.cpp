#include "wav.hpp"
#include <filesystem>
#include <fcntl.h>
#include <fstream>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <unistd.h>

void check(bool yes,const char* text){if(!yes)throw std::runtime_error(text);}
int main(int argc,char** argv){
    char root[]="/tmp/dialogue-wav-test-XXXXXX";
    if(!mkdtemp(root))return 1;
    auto dir=std::filesystem::path(root);
    try{
        std::vector<float> samples{0,.25f,-.5f,1,-0.f};
        auto path=dir/"test.wav";
        ds::write_wav_exclusive(path,samples.data(),samples.size(),48000,2,1234567890123ULL);
        if(argc>1&&std::string(argv[1])=="--deny-dev-fd-expected"){
            int fd=::open(path.c_str(),O_RDONLY|O_CLOEXEC);check(fd>=0,"control WAV could not be opened");
            int duplicate=::open(("/dev/fd/"+std::to_string(fd)).c_str(),O_RDONLY|O_CLOEXEC);
            const int denied_errno=errno;
            if(duplicate>=0)::close(duplicate);::close(fd);
            check(duplicate<0&&(denied_errno==EPERM||denied_errno==EACCES),"/dev/fd denial was not active");
        }
        auto info=ds::inspect_wav(path);
        check(info.frames==5&&info.channels==2&&info.rate==48000&&info.bits==32,"header changed");
        check(info.time_reference&&*info.time_reference==1234567890123ULL,"BWF reference lost");
        auto loaded=ds::read_wav(path);
        for(size_t i=0;i<samples.size();++i)for(int c=0;c<2;++c)
            check(loaded.samples->data()[c*5+i]==samples[i],"audio changed");
        bool refused=false;
        try{ds::write_wav_exclusive(path,samples.data(),5,48000,1,{});}catch(...){refused=true;}
        check(refused,"overwrote existing WAV");
        auto malformed=dir/"bad.wav";
        {std::ofstream out(malformed);out<<"RIFF\xff\xff\xff\xffWAVEfmt ";}
        refused=false;try{ds::inspect_wav(malformed);}catch(...){refused=true;}
        check(refused,"accepted truncated RIFF");
        samples[2]=std::numeric_limits<float>::infinity();
        refused=false;try{ds::write_wav_exclusive(dir/"inf.wav",samples.data(),5,48000,1,{});}catch(...){refused=true;}
        check(refused&&!std::filesystem::exists(dir/"inf.wav"),"left invalid WAV");
        auto changing=dir/"changing.wav";float original[]{.25f,-.5f,.75f};
        ds::write_wav_exclusive(changing,original,3,16000,1,{});
        struct TestStorage final:ds::Storage{
            std::vector<float> v;explicit TestStorage(size_t n):v(n){}
            float* data()override{return v.data();}size_t size()const override{return v.size();}
        };
        auto snapshot=ds::read_wav(changing,[&](size_t n)->ds::Buffer{
            std::filesystem::rename(changing,dir/"prior.wav");float replacement[]{0};
            ds::write_wav_exclusive(changing,replacement,1,16000,1,{});
            return std::make_shared<TestStorage>(n);
        });
        check(snapshot.info.frames==3&&snapshot.samples->data()[2]==.75f,"reader reopened a replaced path instead of the same file");
        // Independently encoded PCM24 extrema and signed one-LSB samples.
        std::vector<unsigned char> pcm;
        auto text=[&](const char* s){pcm.insert(pcm.end(),s,s+4);};
        auto word=[&](uint32_t value,int bytes){for(int i=0;i<bytes;++i)pcm.push_back((value>>(8*i))&255);};
        text("RIFF");word(52,4);text("WAVE");text("fmt ");word(16,4);word(1,2);word(1,2);
        word(48000,4);word(144000,4);word(3,2);word(24,2);text("data");word(15,4);
        for(uint32_t raw:{0x800000u,0xffffffu,0u,1u,0x7fffffu})word(raw,3);pcm.push_back(0);
        auto pcm_path=dir/"pcm24.wav";
        {std::ofstream out(pcm_path,std::ios::binary);out.write(reinterpret_cast<char*>(pcm.data()),pcm.size());}
        auto decoded=ds::read_wav(pcm_path);
        const float extrema[]{-1.f,-0x1p-23f,0,0x1p-23f,1.f-0x1p-23f};
        for(size_t i=0;i<5;++i)check(decoded.samples->data()[i]==extrema[i],"PCM24 sign or scaling changed");
        pcm.clear();
        text("RIFF");word(46,4);text("WAVE");text("fmt ");word(16,4);word(1,2);word(1,2);
        word(44100,4);word(88200,4);word(2,2);word(16,2);text("data");word(10,4);
        for(uint32_t raw:{0x8000u,0xffffu,0u,1u,0x7fffu})word(raw,2);
        auto pcm16_path=dir/"pcm16.wav";
        {std::ofstream out(pcm16_path,std::ios::binary);out.write(reinterpret_cast<char*>(pcm.data()),pcm.size());}
        auto pcm16=ds::read_wav(pcm16_path);
        const float pcm16_values[]{-1.f,-0x1p-15f,0,0x1p-15f,1.f-0x1p-15f};
        check(pcm16.info.rate==44100,"PCM16 rate changed");
        for(size_t i=0;i<5;++i)check(pcm16.samples->data()[i]==pcm16_values[i],"PCM16 sign or scaling changed");
        auto truncated=dir/"truncated-after-header.wav";
        ds::write_wav_exclusive(truncated,original,3,16000,1,{});
        refused=false;
        try{ds::read_wav(truncated,[&](size_t n)->ds::Buffer{
            std::filesystem::resize_file(truncated,12);
            return std::make_shared<TestStorage>(n);
        });}catch(...){refused=true;}
        check(refused,"accepted file truncated after header parsing");
        auto descriptor_count=[](){int count=0;for(int fd=0;fd<256;++fd)if(fcntl(fd,F_GETFD)!=-1)++count;return count;};
        const int before_fds=descriptor_count();
        for(int i=0;i<100;++i){try{ds::read_wav(malformed);}catch(...){} }
        check(descriptor_count()==before_fds,"WAV errors leaked descriptors");
        check(!std::filesystem::exists(dir/"none.wav"),"unexpected file");
        std::filesystem::remove_all(dir);
        std::cout<<"WAV safety contracts passed\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';std::filesystem::remove_all(dir);return 1;}
}
