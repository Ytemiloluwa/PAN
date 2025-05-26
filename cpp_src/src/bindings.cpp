#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // Needed for automatic type conversion std::vector <-> list/tuple
#include <pybind11/stl_bind.h> // Needed for binding std::vector
#include <pybind11/functional.h> // Needed for std::optional
#include <optional>

#include "fintechx_core/pan_utils.hpp"
#include "fintechx_core/encryption_utils.hpp"

namespace py = pybind11;

// Helper to convert std::vector<unsigned char> to Python bytes and vice-versa
// Pybind11 usually handles std::vector<char> or std::string correctly, but
// std::vector<unsigned char> might need explicit handling for bytes.
namespace pybind11 { namespace detail {
    template <> struct type_caster<std::vector<unsigned char>> {
    public:
        PYBIND11_TYPE_CASTER(std::vector<unsigned char>, _("bytes"));

        // Python -> C++ conversion
        bool load(handle src, bool convert) {
            if (!isinstance<bytes>(src)) {
                return false;
            }
            auto b = reinterpret_borrow<bytes>(src);
            const char* buffer = PYBIND11_BYTES_AS_STRING(b.ptr());
            size_t length = PYBIND11_BYTES_SIZE(b.ptr());
            value.assign(buffer, buffer + length);
            return true;
        }

        // C++ -> Python conversion
        static handle cast(const std::vector<unsigned char>& src, return_value_policy policy, handle parent) {
            return py::bytes(reinterpret_cast<const char*>(src.data()), src.size()).release();
        }
    };
}} // namespace pybind11::detail

PYBIND11_MODULE(fintechx_native, m) {
    m.doc() = "Native C++ core modules for FinTechX Desktop (PAN Utils, Encryption)"; // Optional module docstring

    // --- PAN Utils Bindings --- 
    m.def("luhn_check", &fintechx_core::luhn_check, 
          "Validates a PAN using the Luhn algorithm.",
          py::arg("pan"));

    m.def("generate_pan", &fintechx_core::generate_pan, 
          "Generates a single valid PAN based on prefix and length.",
          py::arg("prefix"), py::arg("length"));

    m.def("generate_pan_batch", &fintechx_core::generate_pan_batch, 
          "Generates a batch of valid PANs.",
          py::arg("prefix"), py::arg("length"), py::arg("count"));

    // --- Encryption Utils Bindings --- 
    m.def("encrypt_aes_gcm", &fintechx_core::encrypt_aes_gcm, 
          "Encrypts plaintext using AES-256-GCM. Returns ciphertext + tag.",
          py::arg("plaintext"), py::arg("key"), py::arg("iv"), py::arg("aad") = std::vector<unsigned char>{});

    m.def("decrypt_aes_gcm", &fintechx_core::decrypt_aes_gcm, 
          "Decrypts AES-256-GCM ciphertext. Expects ciphertext + tag. Returns plaintext or nullopt on failure.",
          py::arg("ciphertext_with_tag"), py::arg("key"), py::arg("iv"), py::arg("aad") = std::vector<unsigned char>{});

    m.def("generate_random_bytes", &fintechx_core::generate_random_bytes, 
          "Generates cryptographically secure random bytes.",
          py::arg("length"));

    m.def("derive_key_pbkdf2", &fintechx_core::derive_key_pbkdf2, 
          "Derives a key from a password using PBKDF2-HMAC-SHA256.",
          py::arg("password"), py::arg("salt"), py::arg("iterations"), py::arg("key_length"));

    // Optional: Add version info
#ifdef VERSION_INFO
    m.attr("__version__") = VERSION_INFO;
#else
    m.attr("__version__") = "dev";
#endif
}

