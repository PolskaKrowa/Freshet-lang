// matmul — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 03)
// Stresses: dense f64 triple loop in the i-k-j order, repeated accumulation into C.
// Clean idiomatic style: std::vector, flat row-major, exact spec loop order.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 256;
    const int R = 50;
    const size_t NN = static_cast<size_t>(N) * static_cast<size_t>(N);

    std::vector<double> A(NN);
    std::vector<double> B(NN);
    std::vector<double> C(NN, 0.0);
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            A[static_cast<size_t>(i) * N + j] =
                static_cast<double>((i * 7 + j * 13) & 63) * 0.25;
            B[static_cast<size_t>(i) * N + j] =
                static_cast<double>((i * 11 + j * 3) & 15) * 0.5;
        }
    }

    for (int r = 0; r < R; ++r) {
        for (int i = 0; i < N; ++i) {
            for (int k = 0; k < N; ++k) {
                double aik = A[static_cast<size_t>(i) * N + k];
                for (int j = 0; j < N; ++j) {
                    C[static_cast<size_t>(i) * N + j] +=
                        aik * B[static_cast<size_t>(k) * N + j];
                }
            }
        }
    }

    double s = 0.0;
    for (size_t idx = 0; idx < NN; ++idx) {
        s += C[idx];
    }

    return static_cast<int64_t>(s * 65536.0);  // truncate toward zero
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
