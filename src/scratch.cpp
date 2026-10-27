#include "scratch.hpp"
#include "wav.hpp"
#include "dsp.hpp"
#include <algorithm>
#include <fcntl.h>
#include <stdexcept>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
namespace ds {
namespace {
class MappedStorage final : public Storage {
    float* samples=nullptr;size_t count=0;
public:
    MappedStorage(const std::filesystem::path& dir,size_t n):count(n){
        std::string pattern=(dir/"buffer-XXXXXX").string();
        int fd=::mkstemp(pattern.data());if(fd<0)throw std::runtime_error("No se puede crear un temporal de trabajo.");
        ::unlink(pattern.c_str());size_t bytes=n*sizeof(float);
        fstore_t allocation{};allocation.fst_flags=F_ALLOCATEALL;allocation.fst_posmode=F_PEOFPOSMODE;allocation.fst_length=off_t(bytes);
        if(!n||::fcntl(fd,F_PREALLOCATE,&allocation)<0||::ftruncate(fd,off_t(bytes))){::close(fd);throw std::runtime_error("No hay espacio disponible para los temporales de audio.");}
        auto mapping=::mmap(nullptr,bytes,PROT_READ|PROT_WRITE,MAP_SHARED,fd,0);::close(fd);
        if(mapping==MAP_FAILED)throw std::runtime_error("No se puede mapear el temporal de audio.");
        samples=static_cast<float*>(mapping);::madvise(samples,bytes,MADV_SEQUENTIAL);
    }
    ~MappedStorage() override{if(samples)::munmap(samples,count*sizeof(float));}
    float* data()override{return samples;}size_t size()const override{return count;}
};
}
ScratchSpace::ScratchSpace(const std::filesystem::path& parent){
    auto status=std::filesystem::symlink_status(parent);
    if(!std::filesystem::is_directory(status)||std::filesystem::is_symlink(status))throw std::runtime_error("La carpeta temporal no es válida.");
    char error[512]{};owned=cauces_directory_create(parent.c_str(),"job-",error,sizeof(error));
    if(!owned)throw std::runtime_error(error);root=cauces_directory_path(owned);
}
ScratchSpace::~ScratchSpace(){cauces_directory_destroy(owned);}
Buffer ScratchSpace::allocate(size_t n){return std::make_shared<MappedStorage>(root,n);}
uint64_t required_working_space(const WavInfo& info){
    uint64_t n=info.frames,c=info.channels,l=resampled_length(info.frames,info.rate,16000),h=resampled_length(info.frames,info.rate,48000);
    // Maxima from buffer lifetimes: low band, source-rate round trips,
    // refiner, conversion back to source, then three preview WAVs.
    uint64_t peak=std::max({c*n+4*l,c*n+2*l+2*h+n,c*n+l+3*h+n,
                            c*n+6*h,c*n+2*h+3*n,(4*c+3)*n});
    return peak*4+512ULL*1024*1024;
}
}
