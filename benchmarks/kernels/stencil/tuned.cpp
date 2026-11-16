// stencil — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 04)
// Stresses: 2-D 5-point Jacobi with double buffering, non-dyadic rounding (0.2).
// Hand-tuned: raw swapped pointers, __restrict__ on both buffers, hoisted row
// bases, 2-way unrolled j sweep. The FP expression tree per output element is
// character-for-character the spec's (up, down, left, right, centre); the two
// buffers never alias, so __restrict__ is sound.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int G = 1024;
    const int T = 60;
    const size_t GG = static_cast<size_t>(G) * static_cast<size_t>(G);

    std::vector<double> bufA(GG);
    std::vector<double> bufB(GG);
    double* __restrict__ a = bufA.data();
    double* __restrict__ b = bufB.data();
    for (size_t idx = 0; idx < GG; ++idx) {
        double v = static_cast<double>(idx & 63) * 0.25;
        a[idx] = v;
        b[idx] = v;
    }

    const size_t g = static_cast<size_t>(G);
    const int inner = G - 1;
    const int inner2 = (G - 2) & ~1;  // even count of j-steps for the unrolled body
    for (int t = 0; t < T; ++t) {
        for (int i = 1; i < inner; ++i) {
            const size_t row = static_cast<size_t>(i) * g;
            const double* __restrict__ up = a + row - g;
            const double* __restrict__ dn = a + row + g;
            const double* __restrict__ lf = a + row;
            double* __restrict__ out = b + row;
            int j = 1;
            for (; j <= inner2; j += 2) {
                const size_t jj = static_cast<size_t>(j);
                out[jj] = 0.2 * up[jj] + 0.2 * dn[jj] + 0.2 * lf[jj - 1] +
                          0.2 * lf[jj + 1] + 0.2 * lf[jj];
                const size_t jj1 = jj + 1;
                out[jj1] = 0.2 * up[jj1] + 0.2 * dn[jj1] + 0.2 * lf[jj1 - 1] +
                           0.2 * lf[jj1 + 1] + 0.2 * lf[jj1];
            }
            for (; j < inner; ++j) {
                const size_t jj = static_cast<size_t>(j);
                out[jj] = 0.2 * up[jj] + 0.2 * dn[jj] + 0.2 * lf[jj - 1] +
                          0.2 * lf[jj + 1] + 0.2 * lf[jj];
            }
        }
        double* tmp = a;  // swap the two buffers
        a = b;
        b = tmp;
    }

    double s1 = 0.0;
    for (size_t idx = 0; idx < GG; ++idx) {
        s1 += a[idx];
    }
    double s2 = 0.0;
    for (size_t idx = 0; idx < GG; ++idx) {
        s2 += b[idx];
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
