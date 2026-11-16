// dot — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 01)
// Stresses: unit-stride f64 multiply-add sweep, loop-carried accumulation.
// Clean idiomatic style: std::vector, indexed loops, no pragmas / restrict / threads.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 4000000;
    const int R = 25;

    std::vector<double> x(static_cast<size_t>(N));
    std::vector<double> y(static_cast<size_t>(N));
    for (int i = 0; i < N; ++i) {
        x[static_cast<size_t>(i)] = static_cast<double>(i & 1023) * 0.5;
        y[static_cast<size_t>(i)] = static_cast<double>(i & 255) * 0.25 + 0.125;
    }

    double total = 0.0;
    for (int r = 0; r < R; ++r) {
        for (int i = 0; i < N; ++i) {
            total += x[static_cast<size_t>(i)] * y[static_cast<size_t>(i)];
        }
    }

    return static_cast<int64_t>(total * 65536.0);  // truncate toward zero
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
