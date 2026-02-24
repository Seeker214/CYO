#pragma once
/**
 * utils.h - Common utility functions for chaos-based image encryption
 *
 * Provides: gcd, pymod256, flatten_fortran, reshape_fortran, roll_array
 */

#include <algorithm>
#include <cmath>
#include <vector>

namespace chaos {

/**
 * Compute GCD of two integers.
 */
inline int gcd_impl(int a, int b) {
    a = std::abs(a);
    b = std::abs(b);
    while (b) {
        int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

/**
 * Python-style modulo: always returns non-negative result for positive divisor.
 * In Python: (-5) % 256 == 251
 * In C++:  fmod(-5, 256) == -5  (need correction)
 */
inline double pymod256(double x) {
    double r = std::fmod(x, 256.0);
    return r < 0.0 ? r + 256.0 : r;
}

/**
 * Flatten a 2D row-major array (M x W) to 1D in Fortran (column-major) order.
 * out[j*M + i] = mat[i*W + j]
 */
inline void flatten_fortran(const double* mat, int M, int W, double* out) {
    int idx = 0;
    for (int j = 0; j < W; j++) {
        for (int i = 0; i < M; i++) {
            out[idx++] = mat[i * W + j];
        }
    }
}

/**
 * Reshape a 1D array to 2D row-major (M x W) using Fortran order.
 * out[i*W + j] = flat[j*M + i]
 */
inline void reshape_fortran(const double* flat, int M, int W, double* out) {
    for (int j = 0; j < W; j++) {
        for (int i = 0; i < M; i++) {
            out[i * W + j] = flat[j * M + i];
        }
    }
}

/**
 * In-place circular roll (positive shift = right/down, matching numpy.roll).
 * Uses reverse-based rotation for O(n) time and O(1) extra space.
 */
inline void roll_array(double* arr, int len, int shift) {
    if (len <= 0) return;
    shift = ((shift % len) + len) % len;
    if (shift == 0) return;
    std::reverse(arr, arr + len);
    std::reverse(arr, arr + shift);
    std::reverse(arr + shift, arr + len);
}

} // namespace chaos
