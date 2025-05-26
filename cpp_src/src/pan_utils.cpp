#include "fintechx_core/pan_utils.hpp"
#include <numeric>
#include <algorithm>
#include <random>
#include <stdexcept>
#include <vector>
#include <chrono>

namespace fintechx_core {

// Helper function to check if a string contains only digits
bool is_digits(const std::string &str) {
    return std::all_of(str.begin(), str.end(), ::isdigit);
}

// Luhn algorithm implementation
bool luhn_check(const std::string& pan) {
    if (pan.empty() || !is_digits(pan)) {
        return false;
    }

    int sum = 0;
    int nDigits = pan.length();
    bool alternate = false;

    for (int i = nDigits - 1; i >= 0; i--) {
        int digit = pan[i] - '0';

        if (alternate) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        sum += digit;
        alternate = !alternate;
    }
    return (sum % 10 == 0);
}

// Helper function to calculate Luhn check digit
char calculate_luhn_check_digit(const std::string& partial_pan) {
    std::string pan_with_zero = partial_pan + '0';
    int sum = 0;
    int nDigits = pan_with_zero.length();
    bool alternate = false; // Start alternating from the rightmost digit (which is the placeholder '0')

    for (int i = nDigits - 1; i >= 0; i--) {
        int digit = pan_with_zero[i] - '0';

        if (alternate) {
            digit *= 2;
            if (digit > 9) {
                digit -= 9;
            }
        }
        sum += digit;
        alternate = !alternate;
    }

    int check_digit = (sum % 10 == 0) ? 0 : (10 - (sum % 10));
    return check_digit + '0';
}

std::optional<std::string> generate_pan(const std::string& prefix, int length) {
    if (length <= 0 || prefix.length() >= static_cast<size_t>(length) || !is_digits(prefix)) {
        return std::nullopt; // Invalid input
    }

    // Seed the random number generator properly
    unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
    std::mt19937 generator(seed);
    std::uniform_int_distribution<int> distribution(0, 9);

    std::string partial_pan = prefix;
    int remaining_digits = length - prefix.length() - 1; // -1 for the check digit

    if (remaining_digits < 0) {
         return std::nullopt; // Prefix itself is already too long or exactly length-1
    }

    for (int i = 0; i < remaining_digits; ++i) {
        partial_pan += std::to_string(distribution(generator));
    }

    char check_digit = calculate_luhn_check_digit(partial_pan);
    return partial_pan + check_digit;
}

std::vector<std::string> generate_pan_batch(const std::string& prefix, int length, int count) {
    std::vector<std::string> batch;
    if (count <= 0 || length <= 0 || prefix.length() >= static_cast<size_t>(length) || !is_digits(prefix)) {
        return batch; // Return empty vector for invalid input
    }

    batch.reserve(count);
    for (int i = 0; i < count; ++i) {
        std::optional<std::string> pan = generate_pan(prefix, length);
        if (pan) {
            batch.push_back(*pan);
        } else {
            // Handle potential generation failure (though unlikely with valid inputs here)
            // For simplicity, we just skip adding if generation fails, 
            // but a more robust approach might retry or log an error.
        }
    }
    return batch;
}

}

