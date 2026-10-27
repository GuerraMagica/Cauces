#pragma once
#include <cstddef>
#include <vector>
namespace ds {
constexpr size_t fft_size=2048, hop_size=480, bins=1025;
size_t resampled_length(size_t count, int source_rate, int target_rate);
void resample(const float* input, size_t count, int source_rate, int target_rate,
              float* output, size_t output_count);
struct Spectrum { size_t frames; std::vector<float> values; };
Spectrum spectrum(const float* input, size_t count);
std::vector<float> inverse_spectrum(const float* values, size_t frames, size_t count);
float fade(size_t index, size_t length, size_t start, size_t total, size_t overlap);
bool should_swap(const float* old1,const float* old2,const float* new1,const float* new2,size_t count);
}
