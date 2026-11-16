// radix_sort — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 09)
// Stresses: memory-bound bucket pass over u64 keys — but idiomatic C++ just
// uses std::sort (the honest "what does the language give you" comparison).
// PRNG stream is continuous across rounds, never re-seeded.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <algorithm>

__attribute__((noinline)) uint64_t hot() {
    const int N = 2000000;
    const int ROUNDS = 4;
    const uint64_t M = 0x2545F4914F6CDD1DULL;
    const uint64_t PRIME = 0x100000001B3ULL;

    uint64_t s = 88172645463325252ULL;  // reference seed
    uint64_t cs = 0xCBF29CE484222325ULL; // FNV basis, persists across rounds

    std::vector<uint64_t> keys(static_cast<size_t>(N));
    for (int round = 0; round < ROUNDS; ++round) {
        // regenerate keys from the continuous PRNG (one draw per key)
        for (int i = 0; i < N; ++i) {
            s ^= s >> 12;
            s ^= s << 25;
            s ^= s >> 27;
            keys[static_cast<size_t>(i)] = (s * M) >> 32;  // value < 2^32
        }
        std::sort(keys.begin(), keys.end());
        for (int i = 0; i < N; ++i) {  // fold ascending
            cs = (cs ^ keys[static_cast<size_t>(i)]) * PRIME;
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
