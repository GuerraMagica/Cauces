#include "dsp.hpp"
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

void require(bool value, const char* message) { if (!value) throw std::runtime_error(message); }
int main() {
    try {
        using namespace ds;
        std::vector<float> a{.25f, -.5f, 1.f}, copy(5);
        resample(a.data(), a.size(), 24000, 24000, copy.data(), copy.size());
        require(copy == std::vector<float>({.25f,-.5f,1,0,0}), "identity and zero padding");
        std::vector<float> impulse(5); impulse[0]=1;
        std::vector<float> output(10);
        resample(impulse.data(), 5, 1, 2, output.data(), 10);
        const double expected[]{1.00000381211256,.6302183124636604,0,-.19366765185155138,0,.09852739247496792,0,-.05460433668921598,0,.029891656227379826};
        for(size_t i=0;i<10;++i) require(std::abs(output[i]-expected[i])<8e-8,"Kaiser impulse");
        std::vector<float> rational{.25f,-.75f,1,.125f,-.25f,.75f,-.125f}, r(9,99);
        resample(rational.data(),7,3,2,r.data(),9);
        // True float32 FMA (independently checked through libSystem fmaf).
        // The previous NumPy float64 approximation double-rounds sample 1 by 2 ULP.
        const float er[]{-.2035650610923767f,0x1.ac3ec8p-3f,.28639909625053406f,.1286790817975998f,.22930529713630676f};
        for(size_t i=0;i<5;++i) {
            if(r[i]!=er[i]) std::cerr << "resample["<<i<<"] "<<std::hexfloat<<r[i]<<" expected "<<er[i]<<'\n';
            require(r[i]==er[i],"ascending FMA resampling");
        }
        require(r[5]==0 && r[8]==0,"explicit length has zero tail");
        for(size_t count: {size_t(1),size_t(479),size_t(480),size_t(481),size_t(5001)}) {
            std::vector<float> signal(count);
            for(size_t i=0;i<count;++i) signal[i]=float(.2*std::sin(i*.123)+.1*std::cos(i*.789));
            auto spec=spectrum(signal.data(),count);
            require(spec.frames==count/480+1,"centered frame count");
            auto back=inverse_spectrum(spec.values.data(),spec.frames,count);
            for(size_t i=0;i<count;++i) require(std::abs(back[i]-signal[i])<2e-7,"STFT round trip");
        }
        std::vector<float> pulse(479);pulse[0]=1;
        auto spec=spectrum(pulse.data(),pulse.size());
        for(size_t bin=0;bin<1025;++bin) {
            require(std::abs(spec.values[bin]-(bin%2?-1:1))<1e-6,"centered FFT impulse");
            require(std::abs(spec.values[1025+bin])<1e-6,"centered FFT imaginary");
        }
        require(fade(0,10,5,20,4)==0 && fade(3,10,5,20,4)==.75f,"fade in");
        require(fade(9,10,0,20,4)==.25f && fade(9,10,10,20,4)==1,"outside fade omission");
        std::vector<float> p1{1,2,3},p2{-2,1,0};
        require(should_swap(p1.data(),p2.data(),p2.data(),p1.data(),3),"speaker permutation");
        require(!should_swap(p1.data(),p2.data(),p1.data(),p2.data(),3),"speaker identity");
        std::cout<<"DSP contracts passed\n";
    } catch(const std::exception& e){ std::cerr<<e.what()<<'\n';return 1; }
}
