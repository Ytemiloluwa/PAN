#include "fintechx_core/encryption_utils.hpp"
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/err.h>
#include <stdexcept>
#include <vector>
#include <iostream> // For error reporting during development

namespace fintechx_core {

// Helper function to handle OpenSSL errors
void handle_openssl_errors() {
    unsigned long errCode;
    while((errCode = ERR_get_error())) {
        char *err = ERR_error_string(errCode, NULL);
        // In production, log this error instead of printing to stderr
        std::cerr << "OpenSSL Error: " << err << std::endl;
    }
    // Consider throwing an exception here in a real application
    // throw std::runtime_error("OpenSSL error occurred");
}

std::optional<std::vector<unsigned char>> encrypt_aes_gcm(
    const std::vector<unsigned char>& plaintext,
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& iv,
    const std::vector<unsigned char>& aad
) {
    // Basic validation
    if (key.size() != 32 || iv.size() != 12) { // AES-256 key = 32 bytes, GCM recommended IV = 12 bytes
        std::cerr << "Error: Invalid key or IV size." << std::endl;
        return std::nullopt;
    }

    std::vector<unsigned char> ciphertext(plaintext.size()); // Ciphertext can be same size as plaintext for GCM
    std::vector<unsigned char> tag(16); // GCM tag is typically 16 bytes
    int len = 0;
    int ciphertext_len = 0;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        handle_openssl_errors();
        return std::nullopt;
    }

    // Initialize encryption operation.
    if (1 != EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Set IV length (important for GCM)
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv.size(), NULL)) {
         handle_openssl_errors();
         EVP_CIPHER_CTX_free(ctx);
         return std::nullopt;
    }

    // Initialize key and IV
    if (1 != EVP_EncryptInit_ex(ctx, NULL, NULL, key.data(), iv.data())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Provide AAD data if available
    if (!aad.empty()) {
        if (1 != EVP_EncryptUpdate(ctx, NULL, &len, aad.data(), aad.size())) {
            handle_openssl_errors();
            EVP_CIPHER_CTX_free(ctx);
            return std::nullopt;
        }
    }

    // Encrypt plaintext
    if (1 != EVP_EncryptUpdate(ctx, ciphertext.data(), &len, plaintext.data(), plaintext.size())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }
    ciphertext_len = len;

    // Finalize encryption (handles padding, not needed for GCM but required call)
    if (1 != EVP_EncryptFinal_ex(ctx, ciphertext.data() + len, &len)) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }
    ciphertext_len += len;

    // Get the authentication tag
    if (1 != EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, tag.size(), tag.data())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    EVP_CIPHER_CTX_free(ctx);

    // Append tag to ciphertext
    ciphertext.resize(ciphertext_len); // Adjust size if padding occurred (shouldn't for GCM)
    ciphertext.insert(ciphertext.end(), tag.begin(), tag.end());

    return ciphertext;
}

std::optional<std::vector<unsigned char>> decrypt_aes_gcm(
    const std::vector<unsigned char>& ciphertext_with_tag,
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& iv,
    const std::vector<unsigned char>& aad
) {
    // Basic validation
    if (key.size() != 32 || iv.size() != 12 || ciphertext_with_tag.size() < 16) { // 16 bytes for the tag
        std::cerr << "Error: Invalid key, IV, or ciphertext size." << std::endl;
        return std::nullopt;
    }

    size_t ciphertext_len = ciphertext_with_tag.size() - 16;
    std::vector<unsigned char> ciphertext(ciphertext_with_tag.begin(), ciphertext_with_tag.begin() + ciphertext_len);
    std::vector<unsigned char> tag(ciphertext_with_tag.end() - 16, ciphertext_with_tag.end());
    std::vector<unsigned char> plaintext(ciphertext_len); // Max possible size
    int len = 0;
    int plaintext_len = 0;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        handle_openssl_errors();
        return std::nullopt;
    }

    // Initialize decryption operation
    if (!EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL)) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Set IV length
    if (!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, iv.size(), NULL)) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Initialize key and IV
    if (!EVP_DecryptInit_ex(ctx, NULL, NULL, key.data(), iv.data())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Provide AAD data if available
    if (!aad.empty()) {
        if (!EVP_DecryptUpdate(ctx, NULL, &len, aad.data(), aad.size())) {
            handle_openssl_errors();
            EVP_CIPHER_CTX_free(ctx);
            return std::nullopt;
        }
    }

    // Decrypt ciphertext
    if (!EVP_DecryptUpdate(ctx, plaintext.data(), &len, ciphertext.data(), ciphertext.size())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }
    plaintext_len = len;

    // Set expected tag value
    if (!EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, tag.size(), tag.data())) {
        handle_openssl_errors();
        EVP_CIPHER_CTX_free(ctx);
        return std::nullopt;
    }

    // Finalize decryption - crucial step that verifies the tag
    int ret = EVP_DecryptFinal_ex(ctx, plaintext.data() + len, &len);

    EVP_CIPHER_CTX_free(ctx);

    if (ret > 0) {
        // Success: Tag verified
        plaintext_len += len;
        plaintext.resize(plaintext_len);
        return plaintext;
    } else {
        // Failure: Tag verification failed or other error
        handle_openssl_errors(); // Log the specific error if possible
        std::cerr << "Error: AES-GCM decryption failed (likely tag mismatch)." << std::endl;
        return std::nullopt;
    }
}

std::vector<unsigned char> generate_random_bytes(size_t length) {
    std::vector<unsigned char> bytes(length);
    if (1 != RAND_bytes(bytes.data(), length)) {
        handle_openssl_errors();
        throw std::runtime_error("Failed to generate random bytes");
    }
    return bytes;
}

std::vector<unsigned char> derive_key_pbkdf2(
    const std::string& password,
    const std::vector<unsigned char>& salt,
    int iterations,
    size_t key_length
) {
    std::vector<unsigned char> derived_key(key_length);
    int result = PKCS5_PBKDF2_HMAC(
        password.c_str(),
        password.length(),
        salt.data(),
        salt.size(),
        iterations,
        EVP_sha256(), // Use SHA256
        key_length,
        derived_key.data()
    );

    if (result != 1) {
        handle_openssl_errors();
        throw std::runtime_error("PBKDF2 key derivation failed");
    }
    return derived_key;
}

}

