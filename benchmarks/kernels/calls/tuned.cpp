// calls — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 12)
// Stresses: call overhead — noinline helper calls plus an indirect call
// through a function pointer, with a per-16 branchy selector.
// Hand-tuned: same noinline helper / dispatch structure (the calls ARE the
// benchmark), but with lean local state and the selector branch shaped so the
// common path falls through. Integer semantics identical to the idiomatic file.
#include <cstdio>
#include <cstdint>
#include <chrono>

static const uint64_t C1 = 0x9E3779B97F4A7C15ULL;
static const uint64_t C2 = 0xBF58476D1CE4E5B9ULL;
static const uint64_t C3 = 0x94D049BB133111EFULL;
static const uint64_t C4 = 0x2545F4914F6CDD1DULL;
static const uint64_t C5 = 0x9E3779B1ULL;
static const uint64_t C6 = 0x85EBCA77ULL;
static const uint64_t C7 = 0xC2B2AE3DULL;

__attribute__((noinline)) uint64_t add64(uint64_t a, uint64_t b) { return a + b; }
__attribute__((noinline)) uint64_t mul64(uint64_t a, uint64_t b) { return a * b; }
__attribute__((noinline)) uint64_t xor64(uint64_t a, uint64_t b) { return a ^ b; }

using binfn = uint64_t (*)(uint64_t, uint64_t);

__attribute__((noinline)) uint64_t dispatch(binfn f, uint64_t x) {
    uint64_t a = f(x, C5);
    uint64_t b = mul64(a, C6);
    return add64(b, C7);
}

__attribute__((noinline)) uint64_t direct3(uint64_t x) {
    uint64_t a = add64(x, C2);
    uint64_t b = mul64(a, C3);
    return xor64(b, C4);
}

__attribute__((noinline)) uint64_t hot() {
    const uint64_t N = 10000000;

    uint64_t acc = 0;
    binfn sel = add64;
    for (uint64_t i = 0; i < N; ++i) {
        const uint64_t x = (i * C1) + 7u;  // wrapping u64
        if ((i & 15u) == 0u) {             // re-select the indirect target
            const uint64_t parity = (i >> 4) & 1u;
            sel = (parity == 0u) ? add64 : xor64;
        }
        const uint64_t r = ((i & 1u) == 0u) ? dispatch(sel, x) : direct3(x);
        acc ^= r;
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
