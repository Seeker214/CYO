/**
 * decryption.cpp - Chaos-based image decryption implementation
 *
 * Matches cyo/services/chaos_algorithm.py::decryption()
 */

#include "decryption.h"
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

py::array_t<uint8_t> decryption(py::array_t<uint8_t, py::array::c_style> image,
                                const std::string& key) {
    auto buf = image.request();
    if (buf.ndim != 3 || buf.shape[2] != 3) {
        throw std::runtime_error("Image must have shape (M, W, 3)");
    }

    const int M = static_cast<int>(buf.shape[0]);
    const int W = static_cast<int>(buf.shape[1]);
    const int Sum = M * W;

    auto [p1_val, q1_val] = parse_key(key);

    auto rm = get_R_matrices(W, M, p1_val, q1_val);

    const int t = gcd_impl(M, W);
    const int Min_val = std::min(M, W);

    // =========================================================================
    // Step 1: Extract channels, flatten in Fortran order, concatenate
    // =========================================================================
    const uint8_t* img_data = static_cast<const uint8_t*>(buf.ptr);

    std::vector<double> ch1(Sum), ch2(Sum), ch3(Sum);
    for (int i = 0; i < M; i++) {
        for (int j = 0; j < W; j++) {
            int idx = i * W + j;
            int img_idx = idx * 3;
            ch1[idx] = static_cast<double>(img_data[img_idx]);
            ch2[idx] = static_cast<double>(img_data[img_idx + 1]);
            ch3[idx] = static_cast<double>(img_data[img_idx + 2]);
        }
    }

    std::vector<double> f1(Sum), f2(Sum), f3(Sum);
    flatten_fortran(ch1.data(), M, W, f1.data());
    flatten_fortran(ch2.data(), M, W, f2.data());
    flatten_fortran(ch3.data(), M, W, f3.data());

    const int total_len = 3 * Sum;
    std::vector<double> C(total_len);
    std::copy(f1.begin(), f1.end(), C.begin());
    std::copy(f2.begin(), f2.end(), C.begin() + Sum);
    std::copy(f3.begin(), f3.end(), C.begin() + 2 * Sum);

    // Compute diffusion keys S1, S2
    std::vector<double> S1(total_len), S2(total_len);
    for (int i = 0; i < total_len; i++) {
        S1[i] = std::floor(256.0 * (rm.p[i] + rm.q[i]) / 2.0);
        S2[i] = std::floor(256.0 * rm.p[i]);
    }

    // =========================================================================
    // Step 2: Reverse forward diffusion (C -> D)
    // =========================================================================
    std::vector<double> D(total_len);
    D[0] = pymod256(C[0] - S2[0]);
    for (int i = 1; i < total_len; i++) {
        D[i] = pymod256(C[i] - C[i - 1] - S2[i]);
    }

    // =========================================================================
    // Step 3: Reverse backward diffusion (D -> E)
    // =========================================================================
    std::vector<double> E(total_len);
    E[total_len - 1] = pymod256(D[total_len - 1] - S1[total_len - 1]);
    for (int i = total_len - 2; i >= 0; i--) {
        E[i] = pymod256(D[i] - D[i + 1] - S1[i]);
    }

    // =========================================================================
    // Step 4: De-interleave and reshape
    // =========================================================================
    std::vector<double> r_flat(Sum), g_flat(Sum), b_flat(Sum);
    for (int i = 0; i < Sum; i++) {
        r_flat[i] = E[3 * i];
        g_flat[i] = E[3 * i + 1];
        b_flat[i] = E[3 * i + 2];
    }

    std::vector<double> I1(Sum), I2(Sum), I3(Sum);
    reshape_fortran(r_flat.data(), M, W, I1.data());
    reshape_fortran(g_flat.data(), M, W, I2.data());
    reshape_fortran(b_flat.data(), M, W, I3.data());

    // =========================================================================
    // Step 5: Reverse cross-scrambling
    // =========================================================================
    int i_start = ((M - t) / t) * t;
    int j_start = ((W - t) / t) * t;

    for (int i = i_start; i >= 0; i -= t) {
        for (int j = j_start; j >= 0; j -= t) {
            int wi = std::min(static_cast<int>(std::floor(rm.RR[i * W + j] * M)), M - 1);
            int wj = std::min(static_cast<int>(std::floor(rm.RG[i * W + j] * W)), W - 1);
            int wy = std::min(static_cast<int>(std::floor(rm.RB[i * W + j] * Min_val)),
                              Min_val - 1);

            // Reverse column transformation (roll by -wy)
            std::vector<double> col_combined(3 * M);
            for (int r = 0; r < M; r++) {
                col_combined[r]         = I1[r * W + wj];
                col_combined[M + r]     = I2[r * W + wj];
                col_combined[2 * M + r] = I3[r * W + wj];
            }
            roll_array(col_combined.data(), 3 * M, -wy);
            for (int r = 0; r < M; r++) {
                I1[r * W + wj] = col_combined[r];
                I2[r * W + wj] = col_combined[M + r];
                I3[r * W + wj] = col_combined[2 * M + r];
            }

            // Reverse row transformation (roll by -wy)
            std::vector<double> row_combined(3 * W);
            for (int c = 0; c < W; c++) {
                row_combined[c]         = I1[wi * W + c];
                row_combined[W + c]     = I2[wi * W + c];
                row_combined[2 * W + c] = I3[wi * W + c];
            }
            roll_array(row_combined.data(), 3 * W, -wy);
            for (int c = 0; c < W; c++) {
                I1[wi * W + c] = row_combined[c];
                I2[wi * W + c] = row_combined[W + c];
                I3[wi * W + c] = row_combined[2 * W + c];
            }
        }
    }

    // =========================================================================
    // Output
    // =========================================================================
    auto result = py::array_t<uint8_t>({M, W, 3});
    auto res_buf = result.request();
    uint8_t* res_data = static_cast<uint8_t*>(res_buf.ptr);

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < W; j++) {
            int idx = i * W + j;
            int img_idx = idx * 3;
            res_data[img_idx]     = static_cast<uint8_t>(I1[idx]);
            res_data[img_idx + 1] = static_cast<uint8_t>(I2[idx]);
            res_data[img_idx + 2] = static_cast<uint8_t>(I3[idx]);
        }
    }

    return result;
}

} // namespace chaos
