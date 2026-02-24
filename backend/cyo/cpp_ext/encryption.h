#pragma once
/**
 * encryption.h - Chaos-based image encryption
 */

#include <pybind11/numpy.h>
#include <string>

namespace py = pybind11;

namespace chaos {

/**
 * Encrypt an image using chaos-based algorithm.
 *
 * Steps:
 *   1. Cross-scrambling using chaos matrices
 *   2. Backward diffusion
 *   3. Forward diffusion
 *
 * @param image  Input RGB image as uint8 numpy array (M, W, 3)
 * @param key    Chaos key string "p1,q1"
 * @return       Encrypted image as uint8 numpy array (M, W, 3)
 */
py::array_t<uint8_t> encryption(py::array_t<uint8_t, py::array::c_style> image,
                                const std::string& key);

} // namespace chaos
