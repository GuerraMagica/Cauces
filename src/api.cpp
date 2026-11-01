#include "separator.h"
#include "pipeline.hpp"
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <stdexcept>
struct ds_context{ds::Models models;ds_context(const char* path,int threads):models(path,threads){}};
namespace{
void diagnostic(char* out,size_t size,const char* text){if(out&&size){size_t n=std::min(size-1,std::strlen(text));std::memcpy(out,text,n);out[n]=0;}}
}
extern "C" ds_context* ds_create(const char* path,int threads,char* error,size_t capacity){
    diagnostic(error,capacity,"");
    try{if(!path)throw std::invalid_argument("The model folder is missing.");return new ds_context(path,threads);}
    catch(const std::exception& e){diagnostic(error,capacity,e.what());return nullptr;}
}
extern "C" void ds_destroy(ds_context* context){delete context;}
extern "C" int ds_separate(ds_context* context,const float* input,size_t frames,int channels,int rate,
                            float* a,float* b,float* residual,ds_progress progress,void* user,char* error,size_t capacity){
    diagnostic(error,capacity,"");
    try{
        if(!a||!b||!residual||rate<8000||rate>48000||(channels!=1&&channels!=2)||!frames||frames>size_t(rate)*1800)
            throw std::invalid_argument("The audio buffers or dimensions are not valid.");
        size_t bytes=frames*size_t(channels)*sizeof(float);
        const uintptr_t starts[]{reinterpret_cast<uintptr_t>(a),reinterpret_cast<uintptr_t>(b),reinterpret_cast<uintptr_t>(residual)};
        for(int i=0;i<3;++i)for(int j=i+1;j<3;++j)
            if((starts[i]<starts[j]?starts[j]-starts[i]:starts[i]-starts[j])<bytes)throw std::invalid_argument("The output buffers overlap.");
        ds::Pipeline pipeline(context?&context->models:nullptr,{},[&](double p,const std::string& stage){return !progress||progress(p,stage.c_str(),user)!=0;});
        auto result=pipeline.separate(input,frames,channels,rate);
        float* targets[]{a,b,residual};const float* values[]{result.voices[0]->data(),result.voices[1]->data(),result.residual->data()};
        for(int v=0;v<3;++v)for(int c=0;c<channels;++c)std::copy_n(values[v],frames,targets[v]+c*frames);
        return 0;
    }catch(const std::exception& e){diagnostic(error,capacity,e.what());return 1;}
}
