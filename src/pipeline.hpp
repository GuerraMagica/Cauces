#pragma once
#include "models.hpp"
#include <array>
#include <functional>
#include <memory>
#include <string>

namespace ds {
// Storage ownership is supplied by the adapter. The core never opens files.
struct Storage {
    virtual ~Storage() = default;
    virtual float* data() = 0;
    virtual size_t size() const = 0;
};
using Buffer = std::shared_ptr<Storage>;
using BufferFactory = std::function<Buffer(size_t)>;
using Progress = std::function<bool(double,const std::string&)>;
struct Result {
    std::array<Buffer,2> voices;
    Buffer residual;
    size_t count;
    int channels, sample_rate;
};
class Pipeline {
public:
    explicit Pipeline(Models* models, BufferFactory factory = {}, Progress progress = {});
    // Input is planar; dual mono is validated sample by sample. Result stores mono
    // stems; the adapter reproduces the identical channels without reprocessing.
    Result separate(const float* input, size_t count, int channels, int sample_rate);
private:
    Models* models;
    BufferFactory factory;
    Progress progress;
    Buffer allocate(size_t count);
    void report(double value,const std::string& stage);
    std::array<Buffer,2> low_band(const float* audio,size_t count);
    std::array<Buffer,2> refine(const float* mix,const std::array<Buffer,2>& guides,size_t count);
};
}
