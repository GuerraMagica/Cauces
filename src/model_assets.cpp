#include "model_assets.hpp"
#include <CommonCrypto/CommonDigest.h>
#include <array>
#include <fcntl.h>
#include <iomanip>
#include <sstream>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>
namespace ds {
namespace {
struct FD{int value;explicit FD(int v):value(v){}~FD(){if(value>=0)::close(value);}};
std::vector<char> read_verified(int root,const char* name,size_t maximum,const char* expected){
 FD file(::openat(root,name,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC));struct stat st{};
 if(file.value<0||::fstat(file.value,&st)||!S_ISREG(st.st_mode)||st.st_size<=0||uint64_t(st.st_size)>maximum)throw std::runtime_error("Fallo de integridad: archivo de modelo ausente o inválido.");
 std::vector<char> bytes(size_t(st.st_size));size_t done=0;
 while(done<bytes.size()){auto n=::read(file.value,bytes.data()+done,bytes.size()-done);if(n<0&&errno==EINTR)continue;if(n<=0)throw std::runtime_error("Fallo de integridad durante lectura del modelo.");done+=size_t(n);}
 char extra; if(::read(file.value,&extra,1)!=0)throw std::runtime_error("Fallo de integridad: modelo cambiado.");
 unsigned char hash[32];CC_SHA256(bytes.data(),CC_LONG(bytes.size()),hash);std::ostringstream hex;hex<<std::hex<<std::setfill('0');for(auto value:hash)hex<<std::setw(2)<<int(value);
 if(hex.str()!=expected)throw std::runtime_error("Fallo de integridad: la copia local del modelo no coincide con esta versión de Cauces.");
 return bytes;
}
}
ModelAssets::ModelAssets(const std::string& directory){
 FD root(::open(directory.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));if(root.value<0)throw std::runtime_error("Fallo de integridad: no se puede abrir la carpeta de modelos.");
 separator=read_verified(root.value,"separator.onnx",16*1024*1024,"ac763dcb1010ea8a23103ee799ceb61f394e91bd7a8280e1ef34d3f710ea5a82");
 refiner=read_verified(root.value,"refiner.onnx",1024*1024,"4d4d38f4ca538924118b79daf5e24f293fec6f04e5a6eca2aa36e04c8f23f9cb");
 weights=read_verified(root.value,"weights.bin",256*1024*1024,"b1491a04c97baaa30ebecfc7290fc70daa9404774ace4495065f5243b4188889");
}
}
