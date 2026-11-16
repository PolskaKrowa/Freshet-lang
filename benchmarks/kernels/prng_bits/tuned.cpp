// prng_bits — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 08)
// Stresses: integer shift/xor/mul pipeline (xorshift64*), dependency chain.
// Hand-tuned: 4-way unrolled advance/fold loop (the u64 state chain is serial,
// so the win is loop-overhead removal; the operation order is unchanged).
#include <cstdio>
#include <cstdint>
#include <chrono>

__attribute__((noinline)) uint64_t hot() {
    const uint64_t N = 128000000;
    const uint64_t M = 0x2545F4914F6CDD1DULL;

    uint64_t s = 88172645463325252ULL;  // reference seed
    uint64_t acc = 0;
    const uint64_t n4 = N & ~3ULL;
    uint64_t n = 0;
    for (; n < n4; n += 4) {  // same sequential order, unrolled
        s ^= s >> 12; s ^= s << 25; s ^= s >> 27; acc ^= s * M;
        s ^= s >> 12; s ^= s << 25; s ^= s >> 27; acc ^= s * M;
        s ^= s >> 12; s ^= s << 25; s ^= s >> 27; acc ^= s * M;
        s ^= s >> 12; s ^= s << 25; s ^= s >> 27; acc ^= s * M;
    }
    for (; n < N; ++n) {
        s ^= s >> 12;
        s ^= s << 25;
        s ^= s >> 27;
        acc ^= s * M;
    }

    return acc;
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
