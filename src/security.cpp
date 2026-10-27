#include "security.h"
#include <CommonCrypto/CommonDigest.h>
#include <algorithm>
#include <array>
#include <atomic>
#include <cstring>
#include <dirent.h>
#include <filesystem>
#include <memory>
#include <fcntl.h>
#include <stdexcept>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
namespace fs=std::filesystem;
namespace {
struct FD {int value;explicit FD(int fd=-1):value(fd){}~FD(){if(value>=0)::close(value);}FD(const FD&)=delete;};
void check(bool ok,const char* message){if(!ok)throw std::runtime_error(message);}
void diagnostic(char* out,size_t capacity,const char* text){if(out&&capacity){size_t n=std::min(capacity-1,std::strlen(text));std::memcpy(out,text,n);out[n]=0;}}
bool component(const std::string& name){return !name.empty()&&name!="."&&name!=".."&&name.find('/')==name.npos&&name.size()<240;}
bool same(const struct stat& a,const struct stat& b){return a.st_dev==b.st_dev&&a.st_ino==b.st_ino;}
bool entry_is(int parent,const std::string& name,const struct stat& identity){struct stat st{};return !::fstatat(parent,name.c_str(),&st,AT_SYMLINK_NOFOLLOW)&&same(st,identity);}
// Traversal stays relative to pinned descriptors and rejects detected identity
// replacements. Name checks and unlink are not atomic against a same-UID writer.
void clear(int fd,unsigned depth=0){
 if(depth>16)return;
 DIR* stream=::fdopendir(::dup(fd));if(!stream)return;
 while(auto* entry=::readdir(stream)){
  std::string name=entry->d_name;if(name=="."||name=="..")continue;
  struct stat st{};if(::fstatat(fd,name.c_str(),&st,AT_SYMLINK_NOFOLLOW))continue;
  if(S_ISDIR(st.st_mode)){
   FD child(::openat(fd,name.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));struct stat opened{};
   if(child.value<0||::fstat(child.value,&opened)||!same(st,opened))continue;
   clear(child.value,depth+1);if(entry_is(fd,name,opened))::unlinkat(fd,name.c_str(),AT_REMOVEDIR);
  }else if(entry_is(fd,name,st))::unlinkat(fd,name.c_str(),0);
 }
 ::closedir(stream);
}
}
struct cauces_directory{
 FD parent,root;std::string path,name;struct stat identity{};bool published=false;std::atomic_bool cancelled{false};
 explicit cauces_directory(const fs::path& value):parent(::open(value.parent_path().c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC)),root(),path(value.string()),name(value.filename().string()){
  check(parent.value>=0&&component(name),"No se puede abrir la carpeta privada.");
  root.value=::openat(parent.value,name.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
  check(root.value>=0&&!::fstat(root.value,&identity)&&S_ISDIR(identity.st_mode)&&identity.st_uid==::getuid()&&(identity.st_mode&077)==0,"La carpeta temporal no es privada o ha cambiado.");
  check(entry_is(parent.value,name,identity),"La carpeta temporal ha cambiado.");
 }
 ~cauces_directory(){if(!published&&root.value>=0&&entry_is(parent.value,name,identity)){clear(root.value);if(entry_is(parent.value,name,identity))::unlinkat(parent.value,name.c_str(),AT_REMOVEDIR);}}
};
extern "C" cauces_directory* cauces_directory_adopt(const char* path,char* error,size_t capacity){
 diagnostic(error,capacity,"");try{check(path,"Falta la carpeta.");return new cauces_directory(fs::path(path));}catch(const std::exception& e){diagnostic(error,capacity,e.what());return nullptr;}
}
extern "C" cauces_directory* cauces_directory_create(const char* parent,const char* prefix,char* error,size_t capacity){
 diagnostic(error,capacity,"");try{
  check(parent&&prefix&&component(prefix),"Nombre temporal inválido.");
  // Resolve existing ancestors once, before pinning and creating a private child.
  auto base=fs::canonical(parent);FD dir(::open(base.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));check(dir.value>=0,"No se puede abrir el destino.");
  // mkdirat keeps creation anchored to this parent, even if an ancestor moves.
  for(unsigned i=0;i<32;++i){std::array<unsigned char,16> bytes{};::arc4random_buf(bytes.data(),bytes.size());std::string name=prefix;const char* hex="0123456789abcdef";for(auto b:bytes){name+=hex[b>>4];name+=hex[b&15];}
   if(!::mkdirat(dir.value,name.c_str(),0700)){
    auto result=std::make_unique<cauces_directory>(base/name);struct stat actual{},pinned{};::fstat(result->parent.value,&actual);::fstat(dir.value,&pinned);
    check(same(actual,pinned),"El destino cambió durante la creación.");return result.release();
   }
   check(errno==EEXIST,"No se puede crear la carpeta privada; comprueba espacio y permisos.");
  }throw std::runtime_error("No se puede reservar un temporal único.");
 }catch(const std::exception& e){diagnostic(error,capacity,e.what());return nullptr;}
}
extern "C" const char* cauces_directory_path(const cauces_directory* value){return value?value->path.c_str():nullptr;}
extern "C" int cauces_directory_copy(cauces_directory* dir,const char* source,const char* filename,char* error,size_t capacity){
 diagnostic(error,capacity,"");try{
  check(dir&&source&&filename&&component(filename)&&!dir->published&&!dir->cancelled&&entry_is(dir->parent.value,dir->name,dir->identity),"Carpeta de trabajo inválida o sustituida.");
  FD input(::open(source,O_RDONLY|O_NONBLOCK|O_NOFOLLOW|O_CLOEXEC));struct stat before{},after{};
  check(input.value>=0&&!::fstat(input.value,&before)&&S_ISREG(before.st_mode),"El origen no es un archivo local regular legible.");
  check(before.st_size<=1024LL*1024*1024,"Archivo demasiado grande para esta beta (máximo 1 GiB por archivo). ");
  FD output(::openat(dir->root.value,filename,O_RDWR|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600));check(output.value>=0,"No se puede crear la copia; no se sobrescriben archivos.");
  CC_SHA256_CTX src{},dst{};CC_SHA256_Init(&src);CC_SHA256_Init(&dst);std::array<char,65536> block{};off_t total=0;
  for(;;){check(!dir->cancelled,"Copia cancelada.");ssize_t n=::read(input.value,block.data(),block.size());if(n<0&&errno==EINTR)continue;check(n>=0,"Fallo de lectura.");if(!n)break;check(total<=before.st_size-n,"El origen cambió durante la copia.");total+=n;CC_SHA256_Update(&src,block.data(),CC_LONG(n));ssize_t offset=0;while(offset<n){ssize_t k=::write(output.value,block.data()+offset,n-offset);if(k<0&&errno==EINTR)continue;check(k>0,"No hay espacio suficiente para completar la copia.");offset+=k;}}
  check(!::fstat(input.value,&after)&&same(before,after)&&before.st_size==after.st_size&&total==before.st_size&&before.st_mtimespec.tv_sec==after.st_mtimespec.tv_sec&&before.st_mtimespec.tv_nsec==after.st_mtimespec.tv_nsec,"El origen cambió durante la copia.");
  check(!::fsync(output.value)&&::lseek(output.value,0,SEEK_SET)==0,"No se puede finalizar la copia.");
  off_t verified=0;
  for(;;){check(!dir->cancelled,"Copia cancelada.");ssize_t n=::read(output.value,block.data(),block.size());if(n<0&&errno==EINTR)continue;check(n>=0,"No se puede verificar la copia.");if(!n)break;check(verified<=total-n,"La copia cambió durante su verificación.");verified+=n;CC_SHA256_Update(&dst,block.data(),CC_LONG(n));}
  check(verified==total,"La copia está incompleta.");
  unsigned char a[32],b[32];CC_SHA256_Final(a,&src);CC_SHA256_Final(b,&dst);check(!std::memcmp(a,b,32),"La copia no coincide con el origen.");return 0;
 }catch(const std::exception& e){diagnostic(error,capacity,e.what());return 1;}
}
extern "C" int cauces_directory_publish(cauces_directory* dir,const char* name,char* error,size_t capacity){
 diagnostic(error,capacity,"");try{
  check(dir&&name&&component(name)&&!dir->published&&!dir->cancelled&&entry_is(dir->parent.value,dir->name,dir->identity),"La exportación temporal ha cambiado.");
  check(!::renameatx_np(dir->parent.value,dir->name.c_str(),dir->parent.value,name,RENAME_EXCL),"No se puede publicar; puede existir una exportación con ese nombre.");dir->published=true;::fsync(dir->parent.value);return 0;
 }catch(const std::exception& e){diagnostic(error,capacity,e.what());return 1;}
}
extern "C" void cauces_directory_cancel(cauces_directory* value){if(value)value->cancelled=true;}
extern "C" void cauces_directory_destroy(cauces_directory* value){delete value;}
