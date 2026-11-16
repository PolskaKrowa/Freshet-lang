// stencil — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 04)
// Stresses: 2-D 5-point Jacobi with double buffering, non-dyadic rounding (0.2).
// Clean idiomatic style: std::vector, exact spec expression tree
// (up, down, left, right, centre), std::swap for the buffer swap.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <utility>

__attribute__((noinline)) int64_t hot() {
    const int G = 1024;
    const int T = 60;
    const size_t GG = static_cast<size_t>(G) * static_cast<size_t>(G);

    std::vector<double> A(GG);
    std::vector<double> B(GG);
    for (size_t idx = 0; idx < GG; ++idx) {
        double v = static_cast<double>(idx & 63) * 0.25;
        A[idx] = v;
        B[idx] = v;
    }

    for (int t = 0; t < T; ++t) {
        for (int i = 1; i < G - 1; ++i) {
            for (int j = 1; j < G - 1; ++j) {
                B[static_cast<size_t>(i) * G + j] =
                    0.2 * A[static_cast<size_t>(i - 1) * G + j] +
                    0.2 * A[static_cast<size_t>(i + 1) * G + j] +
                    0.2 * A[static_cast<size_t>(i) * G + (j - 1)] +
                    0.2 * A[static_cast<size_t>(i) * G + (j + 1)] +
                    0.2 * A[static_cast<size_t>(i) * G + j];
            }
        }
        std::swap(A, B);  // swap the two buffers
    }

    double s1 = 0.0;
    for (size_t idx = 0; idx < GG; ++idx) {
        s1 += A[idx];
    }
    double s2 = 0.0;
    for (size_t idx = 0; idx < GG; ++idx) {
        s2 += B[idx];
    }

    return static_cast<int64_t>((s1 + s2) * 65536.0);  // truncate toward zero
}

int main() {
    auto t0 = std::chrono::steady_clock::now();
    int64_t cs = hot();
    auto t1 = std::chrono::steady_clock::now();
    uint64_t ns = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count());
    std::printf("TIME %llu\nCS %lld\n", static_cast<unsigned long long>(ns),
                static_cast<long long>(cs));
    return 0;
}
