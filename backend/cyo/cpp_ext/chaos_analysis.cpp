/**
 * chaos_analysis.cpp - Chaos system analysis implementation
 *
 * C++ accelerated bifurcation, Lyapunov exponent, and phase diagram computation.
 * Replaces the numba JIT Python code in cyo/utils/chaos.py.
 */

#include "chaos_analysis.h"
#include <cmath>
#include <algorithm>
#include <array>

namespace chaos {

// =========================================================================
// Internal: 2x2 QR decomposition (avoids Eigen/LAPACK dependency)
// =========================================================================

/**
 * Perform QR decomposition of a 2x2 matrix using Givens rotation.
 * Input:  B[0..3] = [b00, b01, b10, b11] (row-major)
 * Output: Q[0..3], R[0..3] (row-major)
 */
static void qr2x2(const double B[4], double Q[4], double R[4]) {
    double b00 = B[0], b01 = B[1], b10 = B[2], b11 = B[3];

    // Givens rotation to zero out B[1][0]
    double r = std::hypot(b00, b10);
    double c, s;
    if (r < 1e-15) {
        c = 1.0;
        s = 0.0;
    } else {
        c = b00 / r;
        s = b10 / r;
    }

    // Q = [[c, -s], [s, c]]  (transpose of Givens rotation)
    // R = G * B  where G = [[c, s], [-s, c]]
    R[0] = c * b00 + s * b10;   // r00
    R[1] = c * b01 + s * b11;   // r01
    R[2] = -s * b00 + c * b10;  // r10 (should be ~0)
    R[3] = -s * b01 + c * b11;  // r11

    // Q columns (Q such that B = Q*R)
    Q[0] = c;   Q[1] = -s;
    Q[2] = s;   Q[3] = c;
}

/**
 * Multiply two 2x2 matrices: C = A * B (all row-major).
 */
static inline void mat2x2_mul(const double A[4], const double B[4], double C[4]) {
    C[0] = A[0] * B[0] + A[1] * B[2];
    C[1] = A[0] * B[1] + A[1] * B[3];
    C[2] = A[2] * B[0] + A[3] * B[2];
    C[3] = A[2] * B[1] + A[3] * B[3];
}

// =========================================================================
// Core analysis loop (shared logic for varying k and varying a)
// =========================================================================

/**
 * Run the analysis for a single parameter point.
 *
 * @param a           Current a value
 * @param k           Current k value
 * @param iterations  Total iteration count
 * @param keep_last   Last N iterations kept for bifurcation data
 * @param transient   Transient iterations to skip for Lyapunov
 * @param param_val   The varying parameter value (for bif_x)
 * @param bif_x       [out] Bifurcation x data (appended)
 * @param bif_y       [out] Bifurcation y data (appended)
 * @param le1_out     [out] Lyapunov exponent 1
 * @param le2_out     [out] Lyapunov exponent 2
 */
static void run_single_point(double a, double k,
                             int iterations, int keep_last, int transient,
                             double param_val,
                             std::vector<double>& bif_x,
                             std::vector<double>& bif_y,
                             double& le1_out, double& le2_out) {
    const double x_init = 0.01, y_init = 0.01;
    double x = x_init, y = y_init;

    // Q matrix (identity initially), stored row-major [q00, q01, q10, q11]
    double Q[4] = {1.0, 0.0, 0.0, 1.0};
    double sum_log_r1 = 0.0;
    double sum_log_r2 = 0.0;

    const int bif_start = iterations - keep_last;

    for (int n = 0; n < iterations; n++) {
        double x_prev = x, y_prev = y;
        auto [xn, yn] = iter_system(x, y, a, k);
        x = xn;
        y = yn;

        // Bifurcation data collection
        if (n >= bif_start) {
            bif_x.push_back(param_val);
            bif_y.push_back(x);
        }

        // Lyapunov exponent via QR decomposition
        auto [Xx, Xy, Yx, Yy] = calc_jacobian(x_prev, y_prev, x, a, k);

        double J[4] = {Xx, Xy, Yx, Yy};
        double B[4], Qnew[4], R[4];
        mat2x2_mul(J, Q, B);
        qr2x2(B, Qnew, R);

        // Update Q
        Q[0] = Qnew[0]; Q[1] = Qnew[1];
        Q[2] = Qnew[2]; Q[3] = Qnew[3];

        if (n >= transient) {
            sum_log_r1 += std::log(std::abs(R[0]) + 1e-12);
            sum_log_r2 += std::log(std::abs(R[3]) + 1e-12);
        }
    }

    double valid_steps = static_cast<double>(iterations - transient);
    le1_out = sum_log_r1 / valid_steps;
    le2_out = sum_log_r2 / valid_steps;
}

// =========================================================================
// Public API implementations
// =========================================================================

AnalysisResult compute_for_varying_k(double a_fixed, double k_start, double k_end,
                                     double step, int iterations,
                                     int keep_last, int transient) {
    int num_steps = static_cast<int>((k_end - k_start) / step) + 1;

    AnalysisResult result;
    result.axis_vals.resize(num_steps);
    result.le1.resize(num_steps);
    result.le2.resize(num_steps);
    result.bif_x.reserve(num_steps * keep_last);
    result.bif_y.reserve(num_steps * keep_last);

    // Generate linspace for k values
    for (int i = 0; i < num_steps; i++) {
        result.axis_vals[i] = k_start + i * (k_end - k_start) / (num_steps - 1.0);
    }
    if (num_steps == 1) {
        result.axis_vals[0] = k_start;
    }

    for (int i = 0; i < num_steps; i++) {
        double k = result.axis_vals[i];
        run_single_point(a_fixed, k, iterations, keep_last, transient,
                         k, result.bif_x, result.bif_y,
                         result.le1[i], result.le2[i]);
    }

    return result;
}

AnalysisResult compute_for_varying_a(double k_fixed, double a_start, double a_end,
                                     double step, int iterations,
                                     int keep_last, int transient) {
    int num_steps = static_cast<int>((a_end - a_start) / step) + 1;

    AnalysisResult result;
    result.axis_vals.resize(num_steps);
    result.le1.resize(num_steps);
    result.le2.resize(num_steps);
    result.bif_x.reserve(num_steps * keep_last);
    result.bif_y.reserve(num_steps * keep_last);

    // Generate linspace for a values
    for (int i = 0; i < num_steps; i++) {
        result.axis_vals[i] = a_start + i * (a_end - a_start) / (num_steps - 1.0);
    }
    if (num_steps == 1) {
        result.axis_vals[0] = a_start;
    }

    for (int i = 0; i < num_steps; i++) {
        double a = result.axis_vals[i];
        run_single_point(a, k_fixed, iterations, keep_last, transient,
                         a, result.bif_x, result.bif_y,
                         result.le1[i], result.le2[i]);
    }

    return result;
}

std::pair<std::vector<double>, std::vector<double>>
calculate_phase_diagram(double a, double k, int iterations, int keep_last) {
    std::vector<double> x_traj, y_traj;
    x_traj.reserve(keep_last);
    y_traj.reserve(keep_last);

    double x = 0.01, y = 0.01;
    const int collect_start = iterations - keep_last;

    for (int n = 0; n < iterations; n++) {
        auto [xn, yn] = iter_system(x, y, a, k);
        x = xn;
        y = yn;

        if (n >= collect_start) {
            x_traj.push_back(x);
            y_traj.push_back(y);
        }
    }

    return {x_traj, y_traj};
}

// =========================================================================
// Python-facing wrappers
// =========================================================================

/**
 * Helper: convert std::vector<double> to py::array_t<double> (zero-copy).
 */
static py::array_t<double> vec_to_numpy(std::vector<double>&& v) {
    auto* data = v.data();
    auto size = static_cast<py::ssize_t>(v.size());
    // Transfer ownership: move vector into capsule so Python manages lifetime
    auto capsule = py::capsule(new std::vector<double>(std::move(v)),
                               [](void* p) { delete static_cast<std::vector<double>*>(p); });
    return py::array_t<double>({size}, {sizeof(double)},
                               static_cast<std::vector<double>*>(capsule.get_pointer())->data(),
                               capsule);
}

py::tuple compute_for_varying_k_py(double a_fixed, double k_start, double k_end,
                                   double step, int iterations,
                                   int keep_last, int transient) {
    auto result = compute_for_varying_k(a_fixed, k_start, k_end, step,
                                        iterations, keep_last, transient);
    return py::make_tuple(
        vec_to_numpy(std::move(result.axis_vals)),
        vec_to_numpy(std::move(result.bif_x)),
        vec_to_numpy(std::move(result.bif_y)),
        vec_to_numpy(std::move(result.le1)),
        vec_to_numpy(std::move(result.le2))
    );
}

py::tuple compute_for_varying_a_py(double k_fixed, double a_start, double a_end,
                                   double step, int iterations,
                                   int keep_last, int transient) {
    auto result = compute_for_varying_a(k_fixed, a_start, a_end, step,
                                        iterations, keep_last, transient);
    return py::make_tuple(
        vec_to_numpy(std::move(result.axis_vals)),
        vec_to_numpy(std::move(result.bif_x)),
        vec_to_numpy(std::move(result.bif_y)),
        vec_to_numpy(std::move(result.le1)),
        vec_to_numpy(std::move(result.le2))
    );
}

py::tuple calculate_phase_diagram_py(double a, double k,
                                     int iterations, int keep_last) {
    auto [x_traj, y_traj] = calculate_phase_diagram(a, k, iterations, keep_last);
    // Return as Python lists (matching original behavior)
    py::list x_list(x_traj.size()), y_list(y_traj.size());
    for (size_t i = 0; i < x_traj.size(); i++) {
        x_list[i] = x_traj[i];
        y_list[i] = y_traj[i];
    }
    return py::make_tuple(x_list, y_list);
}

} // namespace chaos
