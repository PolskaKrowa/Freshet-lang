// sumreduce — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 06)
// Stresses: parallel f64 reduction. This is the only parallel C++ kernel in the
// suite: exactly 16 std::thread chunks, per-chunk partials combined in
// ASCENDING chunk order (bit-wise the serial fold; the data is exact dyadic
// anyway, so the grouping is checksum-neutral by construction).
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <thread>

static const int kChunks = 16;

__attribute__((noinline)) int64_t hot() {
    const int N = 32000000;
    const int R = 4;
    const int C = kChunks;             // 16 chunks
    const int chunk = N / C;            // divides exactly: 2,000,000

    std::vector<double> d(static_cast<size_t>(N));
    const double* __restrict__ dp = d.data();
    for (int i = 0; i < N; ++i) {
        d[static_cast<size_t>(i)] = static_cast<double>(i & 1023) * 0.5 + 0.25;
    }

    double total = 0.0;
    std::vector<double> partial(static_cast<size_t>(C));
    for (int r = 0; r < R; ++r) {
        // one thread per chunk, serial ascending summation inside the chunk
        std::vector<std::thread> pool;
        pool.reserve(static_cast<size_t>(C));
        for (int c = 0; c < C; ++c) {
            const long long lo = static_cast<long long>(c) * chunk;
            const long long hi = lo + chunk;  // [lo, hi) slice of d
            double* out = &partial[static_cast<size_t>(c)];
            pool.emplace_back([dp, lo, hi, out]() {
                double acc = 0.0;
                for (long long i = lo; i < hi; ++i) {
                    acc += dp[i];
                }
                *out = acc;
            });
        }
        for (auto& th : pool) {
            th.join();
        }
        // combine per-chunk partials in ascending chunk order
        double acc = partial[0];
        for (int c = 1; c < C; ++c) {
            acc = acc + partial[static_cast<size_t>(c)];
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
