#pragma once
/**
 * chaos_analysis.h - Chaos system analysis (bifurcation, Lyapunov, phase diagram)
 *
 * Provides C++ accelerated implementations of:
 *   - iter_system: single-step chaotic map iteration
 *   - calc_jacobian: Jacobian matrix elements
 *   - compute_for_varying_k: bifurcation + Lyapunov for varying k
 *   - compute_for_varying_a: bifurcation + Lyapunov for varying a
 *   - calculate_phase_diagram: phase portrait computation
 *
 * Matches cyo/utils/chaos.py analysis functions.
 */

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <cmath>
#include <vector>
#include <tuple>

namespace py = pybind11;

namespace chaos {

/**
 * Result struct for bifurcation + Lyapunov analysis.
 */
struct AnalysisResult {
    std::vector<double> axis_vals;   // Parameter axis values (k or a)
    std::vector<double> bif_x;       // Bifurcation X (parameter value, flat)
    std::vector<double> bif_y;       // Bifurcation Y (system state x, flat)
    std::vector<double> le1;         // Lyapunov exponent 1
    std::vector<double> le2;         // Lyapunov exponent 2
};

/**
 * Single-step iteration of the 2D chaotic map.
 *
 *   x(n+1) = sin(21 / (a*k*x*(y+3)*(1-k*x)))
 *   y(n+1) = sin(21 / (a*y*(k*x(n+1)+3)*(1-y)))
 *
 * @param x  Current x value
 * @param y  Current y value
 * @param a  Parameter a
 * @param k  Parameter k
 * @return   (x_next, y_next)
 */
inline std::pair<double, double> iter_system(double x, double y, double a, double k) {
    double denom_x = a * k * x * (y + 3.0) * (1.0 - k * x);
    if (std::abs(denom_x) < 1e-10) denom_x = 1e-10;
    double x_next = std::sin(21.0 / denom_x);

    double denom_y = a * y * (k * x_next + 3.0) * (1.0 - y);
    if (std::abs(denom_y) < 1e-10) denom_y = 1e-10;
    double y_next = std::sin(21.0 / denom_y);

    return {x_next, y_next};
}

/**
 * Compute Jacobian matrix elements J = [[Xx, Xy], [Yx, Yy]].
 *
 * @param x       x(n)
 * @param y       y(n)
 * @param x_next  x(n+1)
 * @param a       Parameter a
 * @param k       Parameter k
 * @return        (Xx, Xy, Yx, Yy)
 */
inline std::tuple<double, double, double, double>
calc_jacobian(double x, double y, double x_next, double a, double k) {
    // Base 1 (for x equation)
    double denom_x = a * (y + 3.0) * k * x * (1.0 - k * x);
    if (std::abs(denom_x) < 1e-10) denom_x = 1e-10;
    double base1 = 21.0 / denom_x;

    // Base 2 (for y equation, uses x_next)
    double denom_y = a * (k * x_next + 3.0) * y * (1.0 - y);
    if (std::abs(denom_y) < 1e-10) denom_y = 1e-10;
    double base2 = 21.0 / denom_y;

    // Partial derivatives
    double Xx = -std::cos(base1) * base1 * (1.0 - 2.0 * k * x) / (x * (1.0 - k * x) + 1e-12);
    double Xy = -std::cos(base1) * base1 / (y + 3.0);
    double Yx = -std::cos(base2) * base2 * k * Xx / (k * x_next + 3.0);
    double Yy = -std::cos(base2) * base2 * (1.0 - 2.0 * y) / (y * (1.0 - y) + 1e-12);

    return {Xx, Xy, Yx, Yy};
}

/**
 * Compute bifurcation diagram + Lyapunov exponents for varying k.
 *
 * @param a_fixed     Fixed value of a
 * @param k_start     Start of k range
 * @param k_end       End of k range
 * @param step        Step size for k
 * @param iterations  Number of iterations per k value
 * @param keep_last   Number of last iterations to keep for bifurcation
 * @param transient   Number of transient iterations to skip for Lyapunov
 * @return            AnalysisResult
 */
AnalysisResult compute_for_varying_k(double a_fixed, double k_start, double k_end,
                                     double step, int iterations = 5000,
                                     int keep_last = 100, int transient = 300);

/**
 * Compute bifurcation diagram + Lyapunov exponents for varying a.
 *
 * @param k_fixed     Fixed value of k
 * @param a_start     Start of a range
 * @param a_end       End of a range
 * @param step        Step size for a
 * @param iterations  Number of iterations per a value
 * @param keep_last   Number of last iterations to keep for bifurcation
 * @param transient   Number of transient iterations to skip for Lyapunov
 * @return            AnalysisResult
 */
AnalysisResult compute_for_varying_a(double k_fixed, double a_start, double a_end,
                                     double step, int iterations = 5000,
                                     int keep_last = 100, int transient = 300);

/**
 * Calculate phase diagram for given parameters.
 *
 * @param a           Parameter a
 * @param k           Parameter k
 * @param iterations  Total number of iterations
 * @param keep_last   Number of last iterations to keep
 * @return            (x_trajectory, y_trajectory)
 */
std::pair<std::vector<double>, std::vector<double>>
calculate_phase_diagram(double a, double k, int iterations = 10000, int keep_last = 2000);

// ===== Python-facing wrappers (return numpy-friendly types) =====

/**
 * Python wrapper for compute_for_varying_k.
 * Returns tuple of numpy arrays.
 */
py::tuple compute_for_varying_k_py(double a_fixed, double k_start, double k_end,
                                   double step, int iterations = 5000,
                                   int keep_last = 100, int transient = 300);

/**
 * Python wrapper for compute_for_varying_a.
 * Returns tuple of numpy arrays.
 */
py::tuple compute_for_varying_a_py(double k_fixed, double a_start, double a_end,
                                   double step, int iterations = 5000,
                                   int keep_last = 100, int transient = 300);

/**
 * Python wrapper for calculate_phase_diagram.
 * Returns tuple of two lists.
 */
py::tuple calculate_phase_diagram_py(double a, double k,
                                     int iterations = 10000, int keep_last = 2000);

} // namespace chaos
