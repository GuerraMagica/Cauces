#include "pipeline.hpp"
#include "wav.hpp"
#include <chrono>
#include <iostream>
int main(int argc,char** argv){
    try{
        if(argc<4)throw std::runtime_error("usage: pipeline_cli models source destination [threads]");
        auto audio=ds::read_wav(argv[2]);
        auto start=std::chrono::steady_clock::now();
        ds::Models models(argv[1],argc>4?std::stoi(argv[4]):4);
        auto loaded=std::chrono::steady_clock::now();
        ds::Pipeline pipeline(&models);
        auto result=pipeline.separate(audio.samples->data(),audio.info.frames,audio.info.channels,audio.info.rate);
        auto processed=std::chrono::steady_clock::now();
        std::filesystem::create_directories(argv[3]);
        const char* names[]{"speaker_1.wav","speaker_2.wav","noise.wav"};
        const float* values[]{result.voices[0]->data(),result.voices[1]->data(),result.residual->data()};
        for(int v=0;v<3;++v)ds::write_wav_exclusive(std::filesystem::path(argv[3])/names[v],values[v],result.count,result.sample_rate,result.channels,audio.info.time_reference);
        std::cout<<"load_seconds="<<std::chrono::duration<double>(loaded-start).count()<<" process_seconds="<<std::chrono::duration<double>(processed-loaded).count()<<'\n';
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
