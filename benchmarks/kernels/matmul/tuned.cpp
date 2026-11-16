// matmul — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 03)
// Stresses: dense f64 triple loop in the i-k-j order, repeated accumulation into C.
// Hand-tuned: __restrict__ pointers, hoisted row bases (Crow/Brow/aik), 4-way
// unrolled j-loop. Each C[i*N+j] still receives its contributions in the spec's
// exact (r asc, k asc) order; unrolling over j is per-element independent.
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
    double* __restrict__ Ap = A.data();
    double* __restrict__ Bp = B.data();
    double* __restrict__ Cp = C.data();
    for (int i = 0; i < N; ++i) {
        double* arow = Ap + static_cast<size_t>(i) * N;
        double* brow = Bp + static_cast<size_t>(i) * N;
        for (int j = 0; j < N; ++j) {
            arow[j] = static_cast<double>((i * 7 + j * 13) & 63) * 0.25;
            brow[j] = static_cast<double>((i * 11 + j * 3) & 15) * 0.5;
        }
    }

    const int n4 = N & ~3;
    for (int r = 0; r < R; ++r) {
        for (int i = 0; i < N; ++i) {
            double* __restrict__ crow = Cp + static_cast<size_t>(i) * N;
            for (int k = 0; k < N; ++k) {
                const double aik = Ap[static_cast<size_t>(i) * N + k];
                const double* __restrict__ bkrow = Bp + static_cast<size_t>(k) * N;
                int j = 0;
                for (; j < n4; j += 4) {
                    crow[j] += aik * bkrow[j];
                    crow[j + 1] += aik * bkrow[j + 1];
                    crow[j + 2] += aik * bkrow[j + 2];
                    crow[j + 3] += aik * bkrow[j + 3];
                }
                for (; j < N; ++j) {
                    crow[j] += aik * bkrow[j];
                }
            }
        }
    }

    double s = 0.0;
    for (size_t idx = 0; idx < NN; ++idx) {
        s += Cp[idx];
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
