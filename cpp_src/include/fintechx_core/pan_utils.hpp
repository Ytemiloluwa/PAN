#ifndef FINTECHX_CORE_PAN_UTILS_HPP
#define FINTECHX_CORE_PAN_UTILS_HPP

#include <string>
#include <vector>
#include <optional>

namespace fintechx_core {

/**
 * @brief Validates a Primary Account Number (PAN) using the Luhn algorithm.
 *
 * @param pan The PAN string to validate. Should contain only digits.
 * @return true if the PAN is valid according to the Luhn algorithm, false otherwise.
 */
bool luhn_check(const std::string& pan);

/**
 * @brief Generates a single valid PAN based on a prefix and desired length.
 *
 * The function generates the remaining digits randomly and calculates the correct
 * Luhn check digit.
 *
 * @param prefix The starting digits of the PAN (e.g., Issuer Identification Number - IIN).
 * @param length The total desired length of the PAN (e.g., 15 for Amex, 16 for Visa/Mastercard).
 * @return An optional containing the generated PAN string if successful (valid prefix and length), std::nullopt otherwise.
 */
std::optional<std::string> generate_pan(const std::string& prefix, int length);

/**
 * @brief Generates a batch of valid PANs.
 *
 * @param prefix The starting digits for all PANs in the batch.
 * @param length The total desired length for each PAN.
 * @param count The number of PANs to generate.
 * @return A vector of generated PAN strings. May be empty if parameters are invalid.
 */
std::vector<std::string> generate_pan_batch(const std::string& prefix, int length, int count);

}

#endif // FINTECHX_CORE_PAN_UTILS_HPP

