// axpy — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 02)
// Stresses: read-modify-write streaming (y = y + a*x), store bandwidth.
// Hand-tuned: __restrict__ pointers, 4-way unrolled RMW sweep and tail.
// Each y[i] still receives its += in the spec's exact ascending order.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 4000000;
    const int R = 25;
    const double a = 0.5;

    std::vector<double> x(static_cast<size_t>(N));
    std::vector<double> y(static_cast<size_t>(N));
    double* __restrict__ xp = x.data();
    double* __restrict__ yp = y.data();
    for (int i = 0; i < N; ++i) {
        xp[i] = static_cast<double>(i & 511) * 0.5;
        yp[i] = static_cast<double>(i & 255) * 0.25;
    }

    const int n4 = N & ~3;
    for (int r = 0; r < R; ++r) {
        int i = 0;
        for (; i < n4; i += 4) {
            yp[i] += a * xp[i];
            yp[i + 1] += a * xp[i + 1];
            yp[i + 2] += a * xp[i + 2];
            yp[i + 3] += a * xp[i + 3];
        }
        for (; i < N; ++i) {
            yp[i] += a * xp[i];
        }
    }

    double s = 0.0;
    for (int i = 0; i < N; ++i) {
        s += yp[i];
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
