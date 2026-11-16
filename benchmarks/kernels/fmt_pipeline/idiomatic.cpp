// fmt_pipeline — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 11)
// Stresses: integer/float formatting + owned-string append/scan churn.
// Clean idiomatic style: std::to_string for the integer, std::ostringstream
// with std::fixed << std::setprecision(3) for the 3-decimal float, then a
// byte-scan FNV-style fold.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <string>
#include <sstream>
#include <iomanip>

__attribute__((noinline)) uint64_t hot() {
    const uint64_t N = 200000;
    const uint64_t PRIME = 0x100000001B3ULL;

    uint64_t cs = 0xCBF29CE484222325ULL;  // FNV basis, persists across iterations

    for (uint64_t i = 0; i < N; ++i) {
        double q = static_cast<double>(i & 1023u) * 0.25;  // exact dyadic
        std::ostringstream oss;
        oss << std::fixed << std::setprecision(3) << q;
        std::string S = std::to_string(i) + "-" + oss.str() + ";";
        for (unsigned char b : S) {
            cs = (cs ^ static_cast<uint64_t>(b)) * PRIME;
        }
    }

    return cs;
}

int main() {
    auto t0 = std::chrono::steady_clock::now();
    uint64_t cs = hot();
    auto t1 = std::chrono::steady_clock::now();
    uint64_t ns = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::nanoseconds>(t1 - t0).count());
    std::printf("TIME %llu\nCS %llu\n", static_cast<unsigned long long>(ns),
                static_cast<unsigned long long>(cs));
    return 0;
}
