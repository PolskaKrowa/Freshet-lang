// radix_sort — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 09)
// Stresses: memory-bound LSB radix sort — 4 passes x 8 bits, 256 buckets,
// counting + prefix + scatter, exactly as the spec describes. Keys are u64
// with value < 2^32 (draw >> 32), so four passes fully sort them. PRNG stream
// is continuous across rounds, never re-seeded.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <cstring>

__attribute__((noinline)) uint64_t hot() {
    const int N = 2000000;
    const int ROUNDS = 4;
    const int PASSES = 4;  // radix 8 bits
    const uint64_t M = 0x2545F4914F6CDD1DULL;
    const uint64_t PRIME = 0x100000001B3ULL;

    uint64_t s = 88172645463325252ULL;  // reference seed
    uint64_t cs = 0xCBF29CE484222325ULL; // FNV basis, persists across rounds

    const size_t NN = static_cast<size_t>(N);
    std::vector<uint64_t> bufA(NN);
    std::vector<uint64_t> bufB(NN);
    uint64_t* __restrict__ src = bufA.data();
    uint64_t* __restrict__ dst = bufB.data();
    size_t cnt[256];

    for (int round = 0; round < ROUNDS; ++round) {
        // regenerate keys from the continuous PRNG (one draw per key)
        for (size_t i = 0; i < NN; ++i) {
            s ^= s >> 12;
            s ^= s << 25;
            s ^= s >> 27;
            src[i] = (s * M) >> 32;  // value < 2^32
        }
        // LSB radix: PASSES passes of 8 bits each, 256 buckets
        for (int p = 0; p < PASSES; ++p) {
            const unsigned sh = static_cast<unsigned>(p) * 8u;
            // counting
            std::memset(cnt, 0, sizeof(cnt));
            for (size_t i = 0; i < NN; ++i) {
                ++cnt[(src[i] >> sh) & 0xFFu];
            }
            // prefix (exclusive)
            size_t total = 0;
            for (int b = 0; b < 256; ++b) {
                size_t c = cnt[b];
                cnt[b] = total;
                total += c;
            }
            // scatter
            for (size_t i = 0; i < NN; ++i) {
                dst[cnt[(src[i] >> sh) & 0xFFu]++] = src[i];
            }
            uint64_t* tmp = src;  // swap src/dst
            src = dst;
            dst = tmp;
        }
        // after 4 (even) passes src holds the fully sorted keys
        for (size_t i = 0; i < NN; ++i) {  // fold ascending
            cs = (cs ^ src[i]) * PRIME;
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
