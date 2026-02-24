/**
 * chaos_sequence.cpp - Chaos sequence generation implementation
 */

#include "chaos_sequence.h"
#include <cmath>
#include <sstream>
#include <stdexcept>

namespace chaos {

void generate_p_q(int Sum, float p1_init, float q1_init,
                  std::vector<double>& p_out, std::vector<double>& q_out) {
    const int total = Sum * 3 + 1000;
    std::vector<double> p(total), q(total);
    const double a = 0.6, k = 0.8;

    // Initialize with float32 precision (matching numpy.float32 conversion)
    p[0] = static_cast<double>(p1_init);
    q[0] = static_cast<double>(q1_init);

    for (int i = 0; i < total - 1; i++) {
        double dp = a * k * p[i] * (q[i] + 3.0) * (1.0 - k * p[i]);
        p[i + 1] = std::sin(21.0 / dp);

        double dq = a * q[i] * (k * p[i + 1] + 3.0) * (1.0 - q[i]);
        q[i + 1] = std::sin(21.0 / dq);
    }

    // Slice [1000 : Sum*3+1000] and normalize
    const int out_len = Sum * 3;
    p_out.resize(out_len);
    q_out.resize(out_len);

    for (int i = 0; i < out_len; i++) {
        // p normalization: (p + a) / (2*a), floor to 4 decimal places
        double pv = p[1000 + i];
        pv = (pv + a) / (2.0 * a);
        pv = std::floor(pv * 1e4) / 1e4;
        p_out[i] = pv;

        // q normalization: q / k, floor to 4 decimal places, abs
        double qv = q[1000 + i];
        qv = qv / k;
        qv = std::floor(qv * 1e4) / 1e4;
        qv = std::abs(qv);
        q_out[i] = qv;
    }
}

RMatrices get_R_matrices(int W, int M, float p1, float q1) {
    RMatrices result;
    const int Sum = W * M;

    generate_p_q(Sum, p1, q1, result.p, result.q);

    result.RR.resize(M * W);
    result.RG.resize(M * W);
    result.RB.resize(M * W);

    for (int i = 0; i < M; i++) {
        for (int j = 0; j < W; j++) {
            int idx = i * W + j;
            result.RR[idx] = result.q[idx];
            result.RG[idx] = result.q[Sum + idx];
            result.RB[idx] = result.q[2 * Sum + idx];
        }
    }

    return result;
}

std::pair<float, float> parse_key(const std::string& key) {
    float p1, q1;
    std::istringstream iss(key);
    char comma;
    if (!(iss >> p1 >> comma >> q1) || comma != ',') {
        throw std::runtime_error("Invalid key format. Expected 'p1,q1', got: " + key);
    }
    return {p1, q1};
}

} // namespace chaos
