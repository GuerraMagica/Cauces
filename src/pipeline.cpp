#include "pipeline.hpp"
#include "dsp.hpp"
#include <algorithm>
#include <cmath>
#include <stdexcept>

namespace ds {
namespace {
class HeapStorage final : public Storage {
    std::vector<float> values;
public:
    explicit HeapStorage(size_t count) : values(count,0) {}
    float* data() override { return values.data(); }
    size_t size() const override { return values.size(); }
};
}
Pipeline::Pipeline(Models* m,BufferFactory f,Progress p): models(m),factory(std::move(f)),progress(std::move(p)) {}
Buffer Pipeline::allocate(size_t count) {
    auto result=factory?factory(count):std::make_shared<HeapStorage>(count);
    if(!result||result->size()!=count||!result->data())throw std::runtime_error("Working memory could not be allocated.");
    std::fill_n(result->data(),count,0.f);
    return result;
}
void Pipeline::report(double value,const std::string& stage) {
    if(progress&&!progress(value,stage))throw std::runtime_error("Operation cancelled.");
}
Result Pipeline::separate(const float* input,size_t count,int channels,int rate) {
    if(rate<8000||rate>48000)throw std::invalid_argument("Sample rates from 8 to 48 kHz are supported.");
    if(channels!=1&&channels!=2)throw std::invalid_argument("Choose mono or identical dual-mono audio.");
    if(!count||count>size_t(rate)*1800)throw std::invalid_argument("The WAV file is empty or exceeds the 30-minute limit.");
    if(!input)throw std::invalid_argument("The input audio samples are missing.");
    bool nonzero=false;
    for(size_t i=0;i<count;++i) {
        if(!std::isfinite(input[i]))throw std::invalid_argument("The audio contains NaN or infinite values.");
        if(channels==2&&input[i]!=input[count+i])throw std::invalid_argument("True stereo separation is not supported. Use mono or identical dual mono.");
        nonzero=nonzero||input[i]!=0;
    }
    report(0,"Preparing audio…");
    if(!nonzero) {
        Result result{{allocate(count),allocate(count)},allocate(count),count,channels,rate};
        std::copy_n(input,count,result.residual->data());
        report(1,"Separation complete");return result;
    }
    if(!models)throw std::runtime_error("The separation models are missing.");
    auto low=allocate(resampled_length(count,rate,16000));
    resample(input,count,rate,16000,low->data(),low->size());
    auto voices16=low_band(low->data(),low->size());
    low.reset();
    auto mix=allocate(resampled_length(count,rate,48000));
    resample(input,count,rate,48000,mix->data(),mix->size());
    std::array<Buffer,2> guides;
    for(int v=0;v<2;++v) {
        auto source=allocate(count);guides[v]=allocate(mix->size());
        resample(voices16[v]->data(),voices16[v]->size(),16000,rate,source->data(),count);
        resample(source->data(),count,rate,48000,guides[v]->data(),mix->size());
        voices16[v].reset();
    }
    auto refined=refine(mix->data(),guides,mix->size());
    guides={};mix.reset();
    Result result{{allocate(count),allocate(count)},allocate(count),count,channels,rate};
    for(int v=0;v<2;++v) {
        resample(refined[v]->data(),refined[v]->size(),48000,rate,result.voices[v]->data(),count);
        refined[v].reset();
    }
    for(size_t i=0;i<count;++i) {
        float a=result.voices[0]->data()[i],b=result.voices[1]->data()[i];
        float residual=input[i]-(a+b);
        if(!std::isfinite(a)||!std::isfinite(b)||!std::isfinite(residual))throw std::runtime_error("Separation produced nonfinite audio.");
        result.residual->data()[i]=residual;
    }
    report(1,"Separation complete");return result;
}
std::array<Buffer,2> Pipeline::low_band(const float* audio,size_t total) {
    std::array<Buffer,2> accum{allocate(total),allocate(total)};
    auto weights=allocate(total);
    for(size_t start=0;start<total;start+=96000) {
        size_t count=std::min(size_t(128000),total-start),length=std::max(size_t(512),count),valid=length/8*8;
        report(.02+.43*double(start)/total,"Separating voices…");
        std::vector<float> block(length,0);std::copy_n(audio+start,count,block.data());
        auto out=models->separate(block);
        std::array<std::vector<float>,2> current{std::vector<float>(count),std::vector<float>(count)};
        for(int v=0;v<2;++v)std::copy_n(out.data()+v*valid,std::min(valid,count),current[v].data());
        size_t overlap=std::min(size_t(32000),count);
        if(start) {
            std::vector<float> prev1(overlap),prev2(overlap);
            for(size_t i=0;i<overlap;++i) {
                if(weights->data()[start+i]<=0)throw std::runtime_error("The voice overlap is not valid.");
                prev1[i]=accum[0]->data()[start+i]/weights->data()[start+i];
                prev2[i]=accum[1]->data()[start+i]/weights->data()[start+i];
            }
            if(should_swap(prev1.data(),prev2.data(),current[0].data(),current[1].data(),overlap))std::swap(current[0],current[1]);
        }
        for(size_t i=0;i<count;++i) {
            float w=fade(i,count,start,total,32000);
            for(int v=0;v<2;++v)accum[v]->data()[start+i]=std::fma(current[v][i],w,accum[v]->data()[start+i]);
            weights->data()[start+i]+=w;
        }
        if(start+count==total)break;
    }
    double numerator=0,denominator=0;
    for(size_t i=0;i<total;++i) {
        if(weights->data()[i]<=0)throw std::runtime_error("The overlap weight is not valid.");
        for(int v=0;v<2;++v)accum[v]->data()[i]/=weights->data()[i];
        double sum=double(accum[0]->data()[i])+accum[1]->data()[i];
        numerator+=double(audio[i])*sum;denominator+=sum*sum;
    }
    float gain=denominator>1e-20?float(numerator/denominator):0;
    for(int v=0;v<2;++v)for(size_t i=0;i<total;++i)accum[v]->data()[i]*=gain;
    return accum;
}
std::array<Buffer,2> Pipeline::refine(const float* mix,const std::array<Buffer,2>& guides,size_t total) {
    std::array<Buffer,2> accum{allocate(total),allocate(total)};
    auto weights=allocate(total);
    for(size_t start=0;start<total;start+=120000) {
        report(.48+.47*double(start)/total,"Refining detail…");
        size_t count=std::min(size_t(144000),total-start);
        auto mixed=spectrum(mix+start,count),a=spectrum(guides[0]->data()+start,count),b=spectrum(guides[1]->data()+start,count);
        size_t width=mixed.values.size();
        std::vector<float> input(width*3);
        std::copy(a.values.begin(),a.values.end(),input.begin());std::copy(b.values.begin(),b.values.end(),input.begin()+width);
        for(size_t i=0;i<width;++i)input[2*width+i]=mixed.values[i]-(a.values[i]+b.values[i]);
        auto refined=models->refine(mixed.values,input,mixed.frames);
        for(int v=0;v<2;++v) {
            auto chunk=inverse_spectrum(refined.data()+v*width,mixed.frames,count);
            for(size_t i=0;i<count;++i)accum[v]->data()[start+i]=std::fma(chunk[i],fade(i,count,start,total,24000),accum[v]->data()[start+i]);
        }
        for(size_t i=0;i<count;++i)weights->data()[start+i]+=fade(i,count,start,total,24000);
        if(start+count==total)break;
    }
    for(size_t i=0;i<total;++i) {
        if(weights->data()[i]<=0)throw std::runtime_error("The spectral weight is not valid.");
        for(int v=0;v<2;++v)accum[v]->data()[i]/=weights->data()[i];
    }
    return accum;
}
}
