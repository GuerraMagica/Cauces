// Experimental Windows adapter, consumed by prepare_source.py.
class RegularWavFile final {
    HANDLE file_=INVALID_HANDLE_VALUE;
    uint64_t length_=0, position_=0;
public:
    explicit RegularWavFile(const std::filesystem::path& path) {
        file_=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,
                          FILE_ATTRIBUTE_NORMAL|FILE_FLAG_OPEN_REPARSE_POINT,nullptr);
        if(file_==INVALID_HANDLE_VALUE)throw std::runtime_error("The WAV file could not be opened.");
        BY_HANDLE_FILE_INFORMATION info{}; LARGE_INTEGER length{};
        if(!GetFileInformationByHandle(file_,&info)||GetFileType(file_)!=FILE_TYPE_DISK||
           (info.dwFileAttributes&(FILE_ATTRIBUTE_REPARSE_POINT|FILE_ATTRIBUTE_DIRECTORY))||
           !GetFileSizeEx(file_,&length)||length.QuadPart<0) {
            CloseHandle(file_);file_=INVALID_HANDLE_VALUE;
            throw std::runtime_error("The source is not a readable regular WAV file.");
        }
        length_=uint64_t(length.QuadPart);
    }
    ~RegularWavFile(){if(file_!=INVALID_HANDLE_VALUE)CloseHandle(file_);}
    RegularWavFile(const RegularWavFile&)=delete;
    RegularWavFile& operator=(const RegularWavFile&)=delete;
    uint64_t size()const{return length_;}
    void seek(uint64_t position){
        if(position>length_)throw std::runtime_error("The WAV file is truncated.");
        LARGE_INTEGER p{};p.QuadPart=LONGLONG(position);
        if(!SetFilePointerEx(file_,p,nullptr,FILE_BEGIN))throw std::runtime_error("WAV seek failed.");
        position_=position;
    }
    void read(unsigned char* dest,size_t count){
        if(uint64_t(count)>length_-position_)throw std::runtime_error("The WAV file is truncated.");
        while(count){
            DWORD got=0;DWORD chunk=DWORD(std::min(count,size_t(0x40000000)));
            if(!ReadFile(file_,dest,chunk,&got,nullptr)||!got)throw std::runtime_error("WAV read failed.");
            position_+=got;dest+=got;count-=got;
        }
    }
};
