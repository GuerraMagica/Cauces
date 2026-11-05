"""Generate experimental platform adapters without touching snapshot/original DSP."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "source/src"
OUT = ROOT / "probe/generated"

def replace_once(text, old, new):
    if text.count(old) != 1:
        raise RuntimeError(f"Source context changed: {old[:80]!r}")
    return text.replace(old, new, 1)

def main():
    OUT.mkdir(exist_ok=True)
    text = (SRC / "models.cpp").read_text()
    text = replace_once(text, '{"weights.bin"}', '{ORT_TSTR("weights.bin")}')
    (OUT / "models.cpp").write_text(text)

    text = (SRC / "model_assets.cpp").read_text()
    text = replace_once(text, '#include <CommonCrypto/CommonDigest.h>',
                        '#include <stdexcept>\n#include <algorithm>\n#include <filesystem>\n#include <CommonCrypto/CommonDigest.h>')
    start = text.index('struct FD')
    end = text.index('\n}\nModelAssets::', start)
    text = text[:start] + '#ifdef _WIN32\n' + (ROOT/'probe/windows_assets.hpp').read_text() + '\n#else\n' + text[start:end] + '\n#endif\n' + text[end:]
    old = ' FD root(::open(directory.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC));if(root.value<0)throw std::runtime_error("Model integrity check failed: the model folder could not be opened.");'
    text = replace_once(text, old, '#ifdef _WIN32\n const auto root=std::filesystem::u8path(directory);\n#else\n' + old + '\n#endif')
    text = text.replace('read_verified(root.value,', 'read_verified(\n#ifdef _WIN32\n root,\n#else\n root.value,\n#endif\n ')
    (OUT / "model_assets.cpp").write_text(text)

    text = (SRC / "wav.cpp").read_text()
    text = replace_once(text, '#include <unistd.h>', '#include <unistd.h>\n#ifdef _WIN32\n#include <windows.h>\n#endif')
    start = text.index('class RegularWavFile final')
    end = text.index('\nRegularWavFile open_regular', start)
    text = text[:start] + '#ifdef _WIN32\n' + (ROOT/'probe/windows_read.hpp').read_text() + '\n#else\n' + text[start:end] + '\n#endif' + text[end:]
    start = text.index('void write_all(int fd,')
    end = text.index('\n}\n}\nstatic WavInfo', start)+2
    win_write = '''void write_all(HANDLE fd,const void* buffer,size_t bytes){
    auto p=static_cast<const unsigned char*>(buffer);
    while(bytes){DWORD wrote=0;DWORD chunk=DWORD(std::min(bytes,size_t(0x40000000)));
        if(!WriteFile(fd,p,chunk,&wrote,nullptr)||!wrote)throw std::runtime_error("WAV write failed.");
        bytes-=wrote;p+=wrote;
    }
}'''
    text = text[:start] + '#ifdef _WIN32\n' + win_write + '\n#else\n' + text[start:end] + '\n#endif' + text[end:]
    old = '    int fd=::open(path.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW,0600);\n    if(fd<0)throw std::runtime_error("The output could not be created. It may already exist or file permission is denied.");'
    text = replace_once(text, old, '''#ifdef _WIN32
    HANDLE fd=CreateFileW(path.c_str(),GENERIC_WRITE,0,nullptr,CREATE_NEW,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(fd==INVALID_HANDLE_VALUE)throw std::runtime_error("The output already exists or could not be created.");
#else
''' + old + '\n#endif')
    old = '''        if(::fsync(fd))throw std::runtime_error("Writing the WAV file could not be completed.");
        if(::close(fd)){fd=-1;throw std::runtime_error("The output WAV file could not be closed.");}fd=-1;'''
    text = replace_once(text, old, '''#ifdef _WIN32
        if(!FlushFileBuffers(fd))throw std::runtime_error("WAV flush failed.");
        if(!CloseHandle(fd)){fd=INVALID_HANDLE_VALUE;throw std::runtime_error("WAV close failed.");}fd=INVALID_HANDLE_VALUE;
#else
''' + old + '\n#endif')
    text = replace_once(text, '    }catch(...){if(fd>=0)::close(fd);::unlink(path.c_str());throw;}', '''    }catch(...){
#ifdef _WIN32
        if(fd!=INVALID_HANDLE_VALUE)CloseHandle(fd);
        DeleteFileW(path.c_str());
#else
        if(fd>=0)::close(fd);::unlink(path.c_str());
#endif
        throw;
    }''')
    (OUT / "wav.cpp").write_text(text)

if __name__ == "__main__":
    main()
