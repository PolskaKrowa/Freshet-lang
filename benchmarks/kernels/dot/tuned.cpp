// dot — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 01)
// Stresses: unit-stride f64 multiply-add sweep, loop-carried accumulation.
// Hand-tuned: __restrict__ pointers, hoisted bases, 4-way unrolled sweep.
// The loop-carried accumulator keeps the spec's exact ascending operation order,
// so the FP bits are identical to the idiomatic version (exact dyadics anyway).
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 4000000;
    const int R = 25;

    std::vector<double> x(static_cast<size_t>(N));
    std::vector<double> y(static_cast<size_t>(N));
    double* __restrict__ xp = x.data();
    double* __restrict__ yp = y.data();
    for (int i = 0; i < N; ++i) {
        xp[i] = static_cast<double>(i & 1023) * 0.5;
        yp[i] = static_cast<double>(i & 255) * 0.25 + 0.125;
    }

    double total = 0.0;
    const int n4 = N & ~3;
    for (int r = 0; r < R; ++r) {
        int i = 0;
        for (; i < n4; i += 4) {  // same sequential accumulation order, unrolled
            total += xp[i] * yp[i];
            total += xp[i + 1] * yp[i + 1];
            total += xp[i + 2] * yp[i + 2];
            total += xp[i + 3] * yp[i + 3];
        }
        for (; i < N; ++i) {
            total += xp[i] * yp[i];
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
