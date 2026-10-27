#include "dsp.hpp"
#include <algorithm>
#include <array>
#include <cmath>
#include <complex>
#include <limits>
#include <numeric>
#include <stdexcept>

namespace ds {
namespace {
constexpr double pi=3.141592653589793238462643383279502884;
double bessel(double square) {
    double term=1, sum=1;
    for(int k=1;k<=80;++k) { term*=square/(4*k*k);sum+=term;if(term<sum*1e-16)break; }
    return sum;
}
const std::array<float,fft_size>& hann() {
    static const auto window=[] {
        std::array<float,fft_size> result{};
        for(size_t n=0;n<fft_size;++n)result[n]=float(.5-.5*std::cos((n*2*pi)/fft_size));
        return result;
    }();
    return window;
}
// Double precision radix-2 FFT. The model boundary is float32; no vendor DSP dependency.
void fft(std::array<std::complex<double>,fft_size>& x, bool inverse) {
    for(size_t i=1,j=0;i<fft_size;++i) {
        size_t bit=fft_size>>1;
        for(;j&bit;bit>>=1)j^=bit;
        j^=bit;
        if(i<j)std::swap(x[i],x[j]);
    }
    for(size_t size=2;size<=fft_size;size*=2) {
        for(size_t j=0;j<size/2;++j) {
            double angle=(inverse?2:-2)*pi*j/size;
            std::complex<double> w{std::cos(angle),std::sin(angle)};
            for(size_t i=j;i<fft_size;i+=size) {
                auto u=x[i],v=x[i+size/2]*w;
                x[i]=u+v;x[i+size/2]=u-v;
            }
        }
    }
    if(inverse) for(auto& sample:x)sample/=fft_size;
}
}
size_t resampled_length(size_t count, int source_rate, int target_rate) {
    if(source_rate<=0||target_rate<=0||source_rate>48000||target_rate>48000)
        throw std::invalid_argument("Sample rate fuera de rango.");
    return (count*size_t(target_rate)+source_rate-1)/source_rate;
}
void resample(const float* input,size_t count,int source_rate,int target_rate,float* output,size_t output_count) {
    size_t natural=resampled_length(count,source_rate,target_rate);
    std::fill_n(output,output_count,0.f);
    if(source_rate==target_rate) {std::copy_n(input,std::min(count,output_count),output);return;}
    int divisor=std::gcd(source_rate,target_rate);
    int up=target_rate/divisor,down=source_rate/divisor,maximum=std::max(up,down),half=10*maximum;
    std::vector<double> coefficients(2*half+1);
    double denominator=bessel(73.96),sum=0;
    for(int offset=-half;offset<=half;++offset) {
        double angle=(double(offset)/maximum)*pi;
        double sinc=offset?std::sin(angle)/angle:1;
        double radial=std::sqrt(std::max(0.,1.-double(offset)*offset/(double(half)*half)))*8.6;
        double coefficient=((sinc/maximum)*bessel(radial*radial))/denominator;
        coefficients[offset+half]=coefficient;sum+=coefficient;
    }
    std::vector<float> filter(coefficients.size());
    for(size_t i=0;i<filter.size();++i)filter[i]=float(coefficients[i]/sum)*float(up);
    for(size_t j=0;j<std::min(natural,output_count);++j) {
        int64_t phase=half+int64_t(j)*down;
        int64_t first=std::max<int64_t>(0,(phase-2*half+up-1)/up);
        // C++ truncation differs from floor only for negative first; max(0,...) removes that difference.
        int64_t last=std::min<int64_t>(int64_t(count)-1,phase/up);
        float value=0;
        for(int64_t i=first;i<=last;++i)value=std::fma(input[i],filter[size_t(phase-i*up)],value);
        output[j]=value;
    }
}
Spectrum spectrum(const float* input,size_t count) {
    Spectrum result{count/hop_size+1,{}};
    result.values.resize(2*bins*result.frames);
    const auto& window=hann();
    std::array<std::complex<double>,fft_size> block{};
    for(size_t frame=0;frame<result.frames;++frame) {
        for(size_t i=0;i<fft_size;++i) {
            int64_t position=int64_t(frame*hop_size+i)-1024;
            float sample=position>=0&&size_t(position)<count?input[position]*window[i]:0;
            block[i]={sample,0};
        }
        fft(block,false);
        for(size_t k=0;k<bins;++k) {
            result.values[k*result.frames+frame]=float(block[k].real());
            result.values[(bins+k)*result.frames+frame]=float(block[k].imag());
        }
    }
    return result;
}
std::vector<float> inverse_spectrum(const float* values,size_t frames,size_t count) {
    if(!frames||1024+count>fft_size+(frames-1)*hop_size)throw std::invalid_argument("Solapamiento espectral inválido.");
    size_t total=fft_size+(frames-1)*hop_size;
    std::vector<float> result(total),weight(total);
    const auto& window=hann();
    std::array<std::complex<double>,fft_size> block{};
    for(size_t frame=0;frame<frames;++frame) {
        for(size_t k=0;k<bins;++k)block[k]={values[k*frames+frame],values[(bins+k)*frames+frame]};
        for(size_t k=bins;k<fft_size;++k)block[k]=std::conj(block[fft_size-k]);
        fft(block,true);
        for(size_t i=0;i<fft_size;++i) {
            size_t at=frame*hop_size+i;
            result[at]=std::fma(float(block[i].real()),window[i],result[at]);
            weight[at]=std::fma(window[i],window[i],weight[at]);
        }
    }
    std::vector<float> trimmed(count);
    for(size_t i=0;i<count;++i) {
        if(weight[1024+i]<=1e-12f)throw std::runtime_error("Solapamiento espectral inválido.");
        trimmed[i]=result[1024+i]/weight[1024+i];
    }
    return trimmed;
}
float fade(size_t index,size_t length,size_t start,size_t total,size_t overlap) {
    size_t width=std::min(length,overlap);
    float result=1;
    if(width&&start&&index<width)result=float(index)/float(width);
    if(width&&start+length<total&&index>=length-width)result*=1-float(index-(length-width))/float(width);
    return result;
}
bool should_swap(const float* old1,const float* old2,const float* new1,const float* new2,size_t count) {
    const float* a[]{old1,old2}; const float* b[]{new1,new2};
    double norm_a[2]{},norm_b[2]{},dot[2][2]{};
    for(size_t i=0;i<count;++i)for(int j=0;j<2;++j) {
        norm_a[j]+=double(a[j][i])*a[j][i];norm_b[j]+=double(b[j][i])*b[j][i];
        for(int k=0;k<2;++k)dot[j][k]+=double(a[j][i])*b[k][i];
    }
    for(int j=0;j<2;++j)for(int k=0;k<2;++k)dot[j][k]/=std::max(1e-12,std::sqrt(norm_a[j]*norm_b[k]));
    return dot[0][0]+dot[1][1]<dot[0][1]+dot[1][0];
}
}
