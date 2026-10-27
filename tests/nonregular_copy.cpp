#include "security.h"
#include "wav.hpp"
#include <filesystem>
#include <stdexcept>
#include <sys/stat.h>
#include <unistd.h>
int main(){
 char pattern[]="/tmp/cauces-fifo-XXXXXX";auto parent=::mkdtemp(pattern);if(!parent)return 2;
 auto source=std::filesystem::path(parent)/"fifo.wav";::mkfifo(source.c_str(),0600);char error[512]{};
 auto directory=cauces_directory_create(parent,"copy-",error,sizeof(error));if(!directory)throw std::runtime_error(error);
 bool rejected=false;try{ds::inspect_wav(source);}catch(const std::exception&){rejected=true;}
 if(!rejected)throw std::runtime_error("WAV reader accepted nonregular source");
 int result=cauces_directory_copy(directory,source.c_str(),"copy.wav",error,sizeof(error));
 cauces_directory_destroy(directory);std::filesystem::remove_all(parent);
 if(result!=1)throw std::runtime_error("nonregular source accepted");
}
