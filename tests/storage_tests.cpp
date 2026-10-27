#include "scratch.hpp"
#include "wav.hpp"
#include <iostream>
#include <stdexcept>
int main(){
    ds::WavInfo info;info.frames=14400000;info.rate=8000;info.channels=1;
    // 8 kHz -> 48 kHz: input + mix + two guides + two accumulators + weights.
    // At least 37*N float32 samples can coexist, plus a 512 MiB reserve.
    uint64_t needed=ds::required_working_space(info);
    if(needed<2131200000ULL+512ULL*1024*1024)throw std::runtime_error("8kHz preflight underestimates live mappings");
    info.frames=86400000;info.rate=48000;
    auto high=ds::required_working_space(info);
    if(high<2419200000ULL+512ULL*1024*1024||high>4ULL*1024*1024*1024)throw std::runtime_error("48kHz preflight is not bounded by real lifetimes");
    std::cout<<"Storage resource bounds passed\n";
}
