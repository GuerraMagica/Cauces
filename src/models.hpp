#pragma once
#include <cstddef>
#include <memory>
#include <string>
#include <vector>

namespace ds {
class Models {
public:
    explicit Models(const std::string& directory, int threads = 1);
    ~Models();
    Models(const Models&) = delete;
    Models& operator=(const Models&) = delete;
    std::vector<float> separate(const std::vector<float>& audio);
    std::vector<float> refine(const std::vector<float>& mixture,
                              const std::vector<float>& guides, size_t frames);
    static std::string version();
private:
    struct Impl;
    std::unique_ptr<Impl> impl;
};
}
