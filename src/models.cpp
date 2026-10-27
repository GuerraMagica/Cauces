#include "models.hpp"
#include "model_assets.hpp"
#include <onnxruntime_cxx_api.h>
#include <array>
#include <cmath>
#include <filesystem>
#include <stdexcept>

namespace ds {
struct Models::Impl {
    ModelAssets assets;
    Ort::Env env{ORT_LOGGING_LEVEL_WARNING, "Cauces"};
    Ort::SessionOptions options;
    Ort::Session separator{nullptr}, refiner{nullptr};
    Ort::MemoryInfo memory = Ort::MemoryInfo::CreateCpu(OrtArenaAllocator, OrtMemTypeDefault);

    Impl(const std::string& directory, int threads):assets(directory) {
        if (threads < 1 || threads > 64) throw std::invalid_argument("Número de hilos inválido.");
        env.DisableTelemetryEvents();
        options.SetIntraOpNumThreads(threads);
        options.SetInterOpNumThreads(1);
        options.SetExecutionMode(ExecutionMode::ORT_SEQUENTIAL);
        options.SetGraphOptimizationLevel(GraphOptimizationLevel::ORT_ENABLE_ALL);
        options.AddConfigEntry("session.intra_op.allow_spinning", "0");
        options.AddExternalInitializersFromFilesInMemory({"weights.bin"},{assets.weights.data()},{assets.weights.size()});
        // Sessions consume the very bytes whose hashes were verified, without reopening paths.
        separator = Ort::Session(env,assets.separator.data(),assets.separator.size(),options);
        refiner = Ort::Session(env,assets.refiner.data(),assets.refiner.size(),options);
    }
    Ort::Value tensor(const std::vector<float>& v, const std::vector<int64_t>& shape) {
        // Run receives these buffers as immutable model inputs.
        return Ort::Value::CreateTensor<float>(memory, const_cast<float*>(v.data()), v.size(), shape.data(), shape.size());
    }
    static std::vector<float> copy(const Ort::Value& value, const std::vector<int64_t>& expected) {
        if (!value.IsTensor()) throw std::runtime_error("El modelo no devolvió un tensor.");
        auto type = value.GetTensorTypeAndShapeInfo();
        if (type.GetElementType() != ONNX_TENSOR_ELEMENT_DATA_TYPE_FLOAT || type.GetShape() != expected)
            throw std::runtime_error("El modelo devolvió dimensiones inesperadas.");
        auto data = value.GetTensorData<float>();
        std::vector<float> result(data, data + type.GetElementCount());
        for (float sample : result) if (!std::isfinite(sample)) throw std::runtime_error("El modelo devolvió audio no finito.");
        return result;
    }
};

Models::Models(const std::string& directory, int threads) : impl(std::make_unique<Impl>(directory, threads)) {}
Models::~Models() = default;
std::string Models::version() { return OrtGetApiBase()->GetVersionString(); }

std::vector<float> Models::separate(const std::vector<float>& audio) {
    if (audio.size() < 512 || audio.size() > 128000) throw std::invalid_argument("Bloque de separación fuera de rango.");
    auto input = impl->tensor(audio, {1, static_cast<int64_t>(audio.size())});
    const char* inputs[] = {"audio"};
    const char* outputs[] = {"voices"};
    auto out = impl->separator.Run(Ort::RunOptions{nullptr}, inputs, &input, 1, outputs, 1);
    return Impl::copy(out[0], {1, 2, static_cast<int64_t>(audio.size()/8*8)});
}

std::vector<float> Models::refine(const std::vector<float>& mixture,
                                  const std::vector<float>& guides, size_t frames) {
    if (!frames || frames > 301 || mixture.size() != 2*1025*frames || guides.size() != 3*2*1025*frames)
        throw std::invalid_argument("Dimensiones inválidas del refinador.");
    std::array<Ort::Value, 2> inputs = {
        impl->tensor(mixture, {1, 2, 1025, static_cast<int64_t>(frames)}),
        impl->tensor(guides, {1, 3, 2, 1025, static_cast<int64_t>(frames)})};
    const char* names[] = {"mixture", "guides"};
    const char* outputs[] = {"refined"};
    auto out = impl->refiner.Run(Ort::RunOptions{nullptr}, names, inputs.data(), inputs.size(), outputs, 1);
    return Impl::copy(out[0], {1, 3, 2, 1025, static_cast<int64_t>(frames)});
}
}
