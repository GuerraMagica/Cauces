#include "models.hpp"
#include <chrono>
#include <cmath>
#include <iostream>
#include <stdexcept>

int main(int argc, char** argv) {
    try {
        if (argc < 2) throw std::runtime_error("usage: runtime_probe models [threads] [length]");
        const int threads = argc > 2 ? std::stoi(argv[2]) : 1;
        const size_t count = argc > 3 ? std::stoul(argv[3]) : 512;
        auto start = std::chrono::steady_clock::now();
        ds::Models models(argv[1], threads);
        auto loaded = std::chrono::steady_clock::now();
        std::vector<float> input(count, 0);
        input[0] = .25f;
        for (int repeat = 0; repeat < 2; ++repeat) {
            auto t = std::chrono::steady_clock::now();
            auto out = models.separate(input);
            if (out.size() != 2 * (count / 8 * 8)) throw std::runtime_error("wrong separator shape");
            for (float v : out) if (!std::isfinite(v)) throw std::runtime_error("nonfinite separator");
            size_t frames = 2;
            auto refined = models.refine(std::vector<float>(2*1025*frames, 0),
                                         std::vector<float>(3*2*1025*frames, 0), frames);
            if (refined.size() != 3*2*1025*frames) throw std::runtime_error("wrong refiner shape");
            for (float v : refined) if (!std::isfinite(v)) throw std::runtime_error("nonfinite refiner");
            std::cout << "run_" << repeat << "_seconds=" << std::chrono::duration<double>(std::chrono::steady_clock::now()-t).count() << '\n';
        }
        std::cout << "runtime=" << ds::Models::version() << " load_seconds=" << std::chrono::duration<double>(loaded-start).count() << '\n';
        return 0;
    } catch (const std::exception& e) { std::cerr << e.what() << '\n'; return 1; }
}
