/**
 * bindings.cpp - pybind11 module definition for chaos_crypto_cpp
 *
 * This is the only file that contains pybind11 module registration.
 * All algorithm logic is in separate .cpp/.h files.
 */

#include "encryption.h"
#include "decryption.h"

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;

PYBIND11_MODULE(chaos_crypto_cpp, m) {
    m.doc() = "C++ implementation of chaos-based image encryption/decryption";

    m.def("encryption", &chaos::encryption,
          "Encrypt an image using chaos algorithm.\n\n"
          "Args:\n"
          "    image: RGB image as uint8 numpy array with shape (M, W, 3)\n"
          "    key: Chaos key string in format 'p1,q1'\n\n"
          "Returns:\n"
          "    Encrypted image as uint8 numpy array with shape (M, W, 3)",
          py::arg("image"), py::arg("key"));

    m.def("decryption", &chaos::decryption,
          "Decrypt an image using chaos algorithm.\n\n"
          "Args:\n"
          "    image: Encrypted RGB image as uint8 numpy array with shape (M, W, 3)\n"
          "    key: Chaos key string in format 'p1,q1'\n\n"
          "Returns:\n"
          "    Decrypted image as uint8 numpy array with shape (M, W, 3)",
          py::arg("image"), py::arg("key"));
}
