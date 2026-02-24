/**
 * encryption.cpp - Chaos-based image encryption implementation
 *
 * Matches cyo/services/chaos_algorithm.py::encryption()
 */

#include "encryption.h"
#include "chaos_sequence.h"
#include "utils.h"

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <vector>

namespace py = pybind11;

namespace chaos {

py::array_t<uint8_t> encryption(py::array_t<uint8_t, py::array::c_style> image,
                                const std::string& key) {
    auto buf = image.request();
    if (buf.ndim != 3 || buf.shape[2] != 3) {
        throw std::runtime_error("Image must have shape (M, W, 3)");
    }

    const int M = static_cast<int>(buf.shape[0]);  // height
    const int W = static_cast<int>(buf.shape[1]);  // width
    const int Sum = M * W;

    auto [p1_val, q1_val] = parse_key(key);

    // Generate chaos matrices
    auto rm = get_R_matrices(W, M, p1_val, q1_val);

    const int t = gcd_impl(M, W);
    const int Min_val = std::min(M, W);

    // Copy image channels to double arrays (row-major M x W)
    std::vector<double> I1(Sum), I2(Sum), I3(Sum);
    const uint8_t* img_data = static_cast<const uint8_t*>(buf.ptr);

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < W; j++) {
            int idx = i * W + j;
            int img_idx = idx * 3;
            I1[idx] = static_cast<double>(img_data[img_idx]);
            I2[idx] = static_cast<double>(img_data[img_idx + 1]);
            I3[idx] = static_cast<double>(img_data[img_idx + 2]);
        }
    }

    // =========================================================================
    // Step 1: Cross-scrambling
    // =========================================================================
    for (int i = 0; i < M; i += t) {
        for (int j = 0; j < W; j += t) {
            int wi = std::min(static_cast<int>(std::floor(rm.RR[i * W + j] * M)), M - 1);
            int wj = std::min(static_cast<int>(std::floor(rm.RG[i * W + j] * W)), W - 1);
            int wy = std::min(static_cast<int>(std::floor(rm.RB[i * W + j] * Min_val)),
                              Min_val - 1);

            // Row transformation: cross-channel circular shift
            std::vector<double> row_combined(3 * W);
            for (int c = 0; c < W; c++) {
                row_combined[c]         = I1[wi * W + c];
                row_combined[W + c]     = I2[wi * W + c];
                row_combined[2 * W + c] = I3[wi * W + c];
            }
            roll_array(row_combined.data(), 3 * W, wy);
            for (int c = 0; c < W; c++) {
                I1[wi * W + c] = row_combined[c];
                I2[wi * W + c] = row_combined[W + c];
                I3[wi * W + c] = row_combined[2 * W + c];
            }

            // Column transformation: cross-channel circular shift
            std::vector<double> col_combined(3 * M);
            for (int r = 0; r < M; r++) {
                col_combined[r]         = I1[r * W + wj];
                col_combined[M + r]     = I2[r * W + wj];
                col_combined[2 * M + r] = I3[r * W + wj];
            }
            roll_array(col_combined.data(), 3 * M, wy);
            for (int r = 0; r < M; r++) {
                I1[r * W + wj] = col_combined[r];
                I2[r * W + wj] = col_combined[M + r];
                I3[r * W + wj] = col_combined[2 * M + r];
            }
        }
    }

    // =========================================================================
    // Step 2: Diffusion
    // =========================================================================

    // Flatten channels in Fortran order and interleave [R0,G0,B0,R1,G1,B1,...]
    std::vector<double> f1(Sum), f2(Sum), f3(Sum);
    flatten_fortran(I1.data(), M, W, f1.data());
    flatten_fortran(I2.data(), M, W, f2.data());
    flatten_fortran(I3.data(), M, W, f3.data());

    const int total_len = 3 * Sum;
    std::vector<double> A(total_len);
    for (int i = 0; i < Sum; i++) {
        A[3 * i]     = f1[i];
        A[3 * i + 1] = f2[i];
        A[3 * i + 2] = f3[i];
    }

    // Compute diffusion keys S1, S2
    std::vector<double> S1(total_len), S2(total_len);
    for (int i = 0; i < total_len; i++) {
        S1[i] = std::floor(256.0 * (rm.p[i] + rm.q[i]) / 2.0);
        S2[i] = std::floor(256.0 * rm.p[i]);
    }

    // Backward diffusion
    std::vector<double> B(total_len);
    B[total_len - 1] = pymod256(A[total_len - 1] + S1[total_len - 1]);
    for (int i = total_len - 2; i >= 0; i--) {
        B[i] = pymod256(B[i + 1] + S1[i] + A[i]);
    }

    // Forward diffusion
    std::vector<double> C(total_len);
    C[0] = pymod256(B[0] + S2[0]);
    for (int i = 1; i < total_len; i++) {
        C[i] = pymod256(C[i - 1] + B[i] + S2[i]);
    }

    // =========================================================================
    // Step 3: Reshape output
    // =========================================================================
    std::vector<double> out1(Sum), out2(Sum), out3(Sum);
    reshape_fortran(C.data(), M, W, out1.data());
    reshape_fortran(C.data() + Sum, M, W, out2.data());
    reshape_fortran(C.data() + 2 * Sum, M, W, out3.data());

    // Create output numpy array
    auto result = py::array_t<uint8_t>({M, W, 3});
    auto res_buf = result.request();
    uint8_t* res_data = static_cast<uint8_t*>(res_buf.ptr);

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < W; j++) {
            int idx = i * W + j;
            int img_idx = idx * 3;
            res_data[img_idx]     = static_cast<uint8_t>(out1[idx]);
            res_data[img_idx + 1] = static_cast<uint8_t>(out2[idx]);
            res_data[img_idx + 2] = static_cast<uint8_t>(out3[idx]);
        }
    }

    return result;
}

} // namespace chaos
