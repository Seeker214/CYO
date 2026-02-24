#pragma once
/**
 * decryption.h - Chaos-based image decryption
 */

#include <pybind11/numpy.h>
#include <string>

namespace py = pybind11;

namespace chaos {

/**
 * Decrypt an image using chaos-based algorithm.
 *
 * Steps (reverse of encryption):
 *   1. Reverse forward diffusion
 *   2. Reverse backward diffusion
 *   3. Reverse cross-scrambling
 *
 * @param image  Encrypted RGB image as uint8 numpy array (M, W, 3)
 * @param key    Chaos key string "p1,q1"
 * @return       Decrypted image as uint8 numpy array (M, W, 3)
 */
py::array_t<uint8_t> decryption(py::array_t<uint8_t, py::array::c_style> image,
                                const std::string& key);

} // namespace chaos
