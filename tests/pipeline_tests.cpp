#include "pipeline.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
int main() {
    try {
        ds::Pipeline pipeline(nullptr);
        std::vector<float> silence{0,-0.f,0};
        auto result=pipeline.separate(silence.data(),silence.size(),1,48000);
        for(size_t i=0;i<3;++i) {
            if(result.voices[0]->data()[i]!=0||result.voices[1]->data()[i]!=0)throw std::runtime_error("silence leaked");
            if(std::signbit(result.residual->data()[i])!=std::signbit(silence[i]))throw std::runtime_error("signed zero changed");
        }
        auto rejects=[&](const std::vector<float>& x,size_t n,int ch,int rate) {
            try{pipeline.separate(x.data(),n,ch,rate);}catch(const std::exception&){return;}
            throw std::runtime_error("invalid input accepted");
        };
        rejects({},0,1,48000);rejects(silence,3,1,96000);rejects(silence,1,3,16000);
        rejects({1,0},1,2,16000);rejects({std::numeric_limits<float>::quiet_NaN()},1,1,16000);
        rejects({.2f},1,1,16000);
        std::cout<<"Pipeline boundary contracts passed\n";
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}
