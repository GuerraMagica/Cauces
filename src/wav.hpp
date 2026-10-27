#pragma once
#include "pipeline.hpp"
#include <cstdint>
#include <filesystem>
#include <optional>
namespace ds {
struct WavInfo {
    int rate=0,channels=0,bits=0,format=0;
    size_t frames=0;
    uint64_t data_offset=0,data_bytes=0;
    std::optional<uint64_t> time_reference;
};
struct Audio { WavInfo info; Buffer samples; };
WavInfo inspect_wav(const std::filesystem::path& path);
Audio read_wav(const std::filesystem::path& path,BufferFactory factory={});
void write_wav_exclusive(const std::filesystem::path& path,const float* mono,size_t frames,
                         int rate,int channels,std::optional<uint64_t> time_reference);
}
