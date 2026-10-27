#pragma once
#include <string>
#include <vector>
namespace ds {
struct ModelAssets {
 std::vector<char> separator,refiner,weights;
 explicit ModelAssets(const std::string& directory);
};
}
