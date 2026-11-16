// soa_sweep — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 07)
// Stresses: AoS vs SoA layout on an 8-field struct with 2 hot fields.
// Clean idiomatic style: std::vector<P8> (array of structs), plain loops —
// the hot sweep drags all 8 fields through the cache: that is the point.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

struct P8 {
    double x, y, z, w, vx, vy, vz, vw;
};

__attribute__((noinline)) int64_t hot() {
    const int N = 4000000;
    const int R = 10;

    std::vector<P8> p(static_cast<size_t>(N));
    for (int i = 0; i < N; ++i) {
        P8 rec{0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
        rec.x = 1.5;
        rec.vy = 2.5;
        p[static_cast<size_t>(i)] = rec;
    }

    double s = 0.0;
    for (int r = 0; r < R; ++r) {
        for (int i = 0; i < N; ++i) {
            s += p[static_cast<size_t>(i)].x + p[static_cast<size_t>(i)].vy;
        }
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
