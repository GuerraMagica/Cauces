// Experimental Windows adapter. The expected hashes below stay in original source.
std::vector<char> read_verified(const std::filesystem::path& root,const char* name,size_t maximum,const char* expected){
    const auto path=root/name;
    HANDLE raw=CreateFileW(path.c_str(),GENERIC_READ,FILE_SHARE_READ,nullptr,OPEN_EXISTING,
                          FILE_ATTRIBUTE_NORMAL|FILE_FLAG_OPEN_REPARSE_POINT,nullptr);
    if(raw==INVALID_HANDLE_VALUE)throw std::runtime_error("Model integrity check failed: asset unavailable.");
    struct File {HANDLE h;~File(){CloseHandle(h);}} file{raw};
    BY_HANDLE_FILE_INFORMATION info{};LARGE_INTEGER size{};
    if(!GetFileInformationByHandle(raw,&info)||GetFileType(raw)!=FILE_TYPE_DISK||
       (info.dwFileAttributes&(FILE_ATTRIBUTE_REPARSE_POINT|FILE_ATTRIBUTE_DIRECTORY))||
       !GetFileSizeEx(raw,&size)||size.QuadPart<=0||uint64_t(size.QuadPart)>maximum)
        throw std::runtime_error("Model integrity check failed: asset invalid.");
    std::vector<char> bytes(size_t(size.QuadPart));size_t done=0;
    while(done<bytes.size()){
        DWORD got=0;DWORD chunk=DWORD(std::min(bytes.size()-done,size_t(0x40000000)));
        if(!ReadFile(raw,bytes.data()+done,chunk,&got,nullptr)||!got)
            throw std::runtime_error("Model integrity check failed while reading.");
        done+=got;
    }
    unsigned char hash[32];CC_SHA256(bytes.data(),CC_LONG(bytes.size()),hash);
    std::ostringstream hex;hex<<std::hex<<std::setfill('0');for(auto value:hash)hex<<std::setw(2)<<int(value);
    if(hex.str()!=expected)throw std::runtime_error("Model integrity check failed: asset hash mismatch.");
    return bytes;
}
