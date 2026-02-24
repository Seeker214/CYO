/**
 * bindings.cpp - pybind11 module definition for chaos_crypto_cpp
 *
 * This is the only file that contains pybind11 module registration.
 * All algorithm logic is in separate .cpp/.h files.
 */

#include "encryption.h"
#include "decryption.h"
#include "chaos_analysis.h"

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

    // === Chaos Analysis Functions ===

    m.def("compute_for_varying_k", &chaos::compute_for_varying_k_py,
          "Compute bifurcation + Lyapunov exponents for varying k.\n\n"
          "Args:\n"
          "    a_fixed: Fixed value of parameter a\n"
          "    k_start: Start of k range\n"
          "    k_end: End of k range\n"
          "    step: Step size\n"
          "    iterations: Iterations per point (default 5000)\n"
          "    keep_last: Last N points for bifurcation (default 100)\n"
          "    transient: Transient skip for Lyapunov (default 300)\n\n"
          "Returns:\n"
          "    Tuple of (axis_vals, bif_x, bif_y, le1, le2) as numpy arrays",
          py::arg("a_fixed"), py::arg("k_start"), py::arg("k_end"),
          py::arg("step"), py::arg("iterations") = 5000,
          py::arg("keep_last") = 100, py::arg("transient") = 300);

    m.def("compute_for_varying_a", &chaos::compute_for_varying_a_py,
          "Compute bifurcation + Lyapunov exponents for varying a.\n\n"
          "Args:\n"
          "    k_fixed: Fixed value of parameter k\n"
          "    a_start: Start of a range\n"
          "    a_end: End of a range\n"
          "    step: Step size\n"
          "    iterations: Iterations per point (default 5000)\n"
          "    keep_last: Last N points for bifurcation (default 100)\n"
          "    transient: Transient skip for Lyapunov (default 300)\n\n"
          "Returns:\n"
          "    Tuple of (axis_vals, bif_x, bif_y, le1, le2) as numpy arrays",
          py::arg("k_fixed"), py::arg("a_start"), py::arg("a_end"),
          py::arg("step"), py::arg("iterations") = 5000,
          py::arg("keep_last") = 100, py::arg("transient") = 300);

    m.def("calculate_phase_diagram", &chaos::calculate_phase_diagram_py,
          "Calculate phase diagram for given parameters.\n\n"
          "Args:\n"
          "    a: Parameter a\n"
          "    k: Parameter k\n"
          "    iterations: Total iterations (default 10000)\n"
          "    keep_last: Last N points to keep (default 2000)\n\n"
          "Returns:\n"
          "    Tuple of (x_trajectory, y_trajectory) as Python lists",
          py::arg("a"), py::arg("k"),
          py::arg("iterations") = 10000, py::arg("keep_last") = 2000);
}
