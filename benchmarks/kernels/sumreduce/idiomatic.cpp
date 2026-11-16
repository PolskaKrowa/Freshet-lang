// sumreduce — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 06)
// Stresses: f64 reduction (serial here — the parallel policy applies to
// Freshet / tuned C++ / Rust only).
// Clean idiomatic style: std::vector, plain ascending loops.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 32000000;
    const int R = 4;

    std::vector<double> d(static_cast<size_t>(N));
    for (int i = 0; i < N; ++i) {
        d[static_cast<size_t>(i)] = static_cast<double>(i & 1023) * 0.5 + 0.25;
    }

    double total = 0.0;
    for (int r = 0; r < R; ++r) {
        double acc = 0.0;
        for (int i = 0; i < N; ++i) {
            acc += d[static_cast<size_t>(i)];
        }
        total = total + acc;
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
