#pragma once
#include "pipeline.hpp"
#include "security.h"
#include <filesystem>
#include <cstdint>
namespace ds {
struct WavInfo;
uint64_t required_working_space(const WavInfo& info);
class ScratchSpace {
    std::filesystem::path root;
    cauces_directory* owned=nullptr;
public:
    explicit ScratchSpace(const std::filesystem::path& parent);
    ~ScratchSpace();
    ScratchSpace(const ScratchSpace&)=delete;
    ScratchSpace& operator=(const ScratchSpace&)=delete;
    Buffer allocate(size_t count);
    const std::filesystem::path& directory() const { return root; }
};
}
