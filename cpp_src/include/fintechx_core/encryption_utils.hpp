#ifndef FINTECHX_CORE_ENCRYPTION_UTILS_HPP
#define FINTECHX_CORE_ENCRYPTION_UTILS_HPP

#include <string>
#include <vector>
#include <optional>

namespace fintechx_core {

/**
 * @brief Encrypts plaintext data using AES-256-GCM.
 *
 * AES-GCM provides both confidentiality and data authenticity.
 *
 * @param plaintext The data to encrypt.
 * @param key The 256-bit (32 bytes) encryption key.
 * @param iv The 96-bit (12 bytes) initialization vector (IV). Must be unique for each encryption with the same key.
 * @param aad Additional Authenticated Data (optional). Data that will be authenticated but not encrypted.
 * @return An optional containing the ciphertext if encryption is successful, std::nullopt otherwise.
 *         The ciphertext includes the authentication tag appended at the end.
 */
std::optional<std::vector<unsigned char>> encrypt_aes_gcm(
    const std::vector<unsigned char>& plaintext,
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& iv,
    const std::vector<unsigned char>& aad = {}
);

/**
 * @brief Decrypts ciphertext data using AES-256-GCM.
 *
 * Verifies the authenticity of the data using the embedded tag.
 *
 * @param ciphertext The data to decrypt (including the appended 16-byte authentication tag).
 * @param key The 256-bit (32 bytes) encryption key.
 * @param iv The 96-bit (12 bytes) initialization vector (IV) used during encryption.
 * @param aad Additional Authenticated Data (optional) used during encryption.
 * @return An optional containing the original plaintext if decryption and authentication are successful, std::nullopt otherwise.
 */
std::optional<std::vector<unsigned char>> decrypt_aes_gcm(
    const std::vector<unsigned char>& ciphertext,
    const std::vector<unsigned char>& key,
    const std::vector<unsigned char>& iv,
    const std::vector<unsigned char>& aad = {}
);

/**
 * @brief Generates a cryptographically secure random byte vector.
 *
 * Useful for generating keys, IVs, or salts.
 *
 * @param length The desired length of the byte vector in bytes.
 * @return A vector containing the random bytes.
 * @throws std::runtime_error if the random number generator fails.
 */
std::vector<unsigned char> generate_random_bytes(size_t length);


/**
 * @brief Derives a key from a password using PBKDF2-HMAC-SHA256.
 *
 * @param password The user's password.
 * @param salt A unique salt for this password. Should be stored alongside the derived key or hash.
 * @param iterations The number of iterations (higher is more secure but slower). Recommend >= 100,000.
 * @param key_length The desired length of the derived key in bytes (e.g., 32 for AES-256).
 * @return The derived key.
 * @throws std::runtime_error if key derivation fails.
 */
std::vector<unsigned char> derive_key_pbkdf2(
    const std::string& password,
    const std::vector<unsigned char>& salt,
    int iterations,
    size_t key_length
);

}

#endif // FINTECHX_CORE_ENCRYPTION_UTILS_HPP

