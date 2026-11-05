#pragma once
// Experimental adapter only. The Mac build uses the original SDK header.
#ifdef _WIN32
#include <windows.h>
#include <bcrypt.h>
#include <stdexcept>
using CC_LONG = unsigned long;
inline unsigned char* CC_SHA256(const void* data, CC_LONG count, unsigned char* output) {
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    if (BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0) < 0)
        throw std::runtime_error("SHA-256 provider could not be opened.");
    const auto status = BCryptHash(algorithm, nullptr, 0,
        const_cast<unsigned char*>(static_cast<const unsigned char*>(data)), count, output, 32);
    BCryptCloseAlgorithmProvider(algorithm, 0);
    if (status < 0) throw std::runtime_error("SHA-256 failed.");
    return output;
}
#else
#include <openssl/sha.h>
using CC_LONG = unsigned long;
inline unsigned char* CC_SHA256(const void* data, CC_LONG count, unsigned char* output) {
    if (!SHA256(static_cast<const unsigned char*>(data), count, output))
        throw std::runtime_error("SHA-256 failed.");
    return output;
}
#endif
