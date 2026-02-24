#pragma once
/**
 * chaos_sequence.h - Chaos sequence generation and R matrix computation
 *
 * Provides: generate_p_q, RMatrices, get_R_matrices, parse_key
 */

#include <cmath>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace chaos {

/**
 * Holds the R matrices and chaos sequences for encryption/decryption.
 */
struct RMatrices {
    std::vector<double> RR, RG, RB;  // Each M*W, stored row-major
    std::vector<double> p, q;         // Each 3*Sum
};

/**
 * Generate chaos sequences p and q.
 * Matches cyo/utils/chaos.py::get_p_and_q()
 *
 * Chaotic map:
 *   p(n+1) = sin(21 / (a*k*p(n) * (q(n)+3) * (1 - k*p(n))))
 *   q(n+1) = sin(21 / (a*q(n) * (k*p(n+1)+3) * (1 - q(n))))
 *
 * After 1000 warmup iterations, output sequences are normalized:
 *   p_out = floor((p + a) / (2a) * 10^4) / 10^4
 *   q_out = abs(floor(q / k * 10^4) / 10^4)
 */
void generate_p_q(int Sum, float p1_init, float q1_init,
                  std::vector<double>& p_out, std::vector<double>& q_out);

/**
 * Generate R matrices from chaos sequences.
 * Matches cyo/utils/chaos.py::get_R_matrix()
 */
RMatrices get_R_matrices(int W, int M, float p1, float q1);

/**
 * Parse key string "p1,q1" -> (float, float).
 * Throws std::runtime_error on invalid format.
 */
std::pair<float, float> parse_key(const std::string& key);

} // namespace chaos
