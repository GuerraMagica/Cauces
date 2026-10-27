#include "scratch.hpp"
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <unistd.h>
namespace fs=std::filesystem;
int main(){
 char pattern[]="/tmp/cauces-cleanup-XXXXXX";auto tmp=::mkdtemp(pattern);if(!tmp)return 2;fs::path parent=tmp,root;
 {ds::ScratchSpace space(parent);root=space.directory();fs::rename(root,parent/"retired");fs::create_directory(root);std::ofstream(root/"keep")<<"replacement";}
 bool safe=fs::exists(root/"keep")&&fs::exists(parent/"retired");fs::remove_all(parent);
 if(!safe)throw std::runtime_error("cleanup deleted a replacement directory");
}
