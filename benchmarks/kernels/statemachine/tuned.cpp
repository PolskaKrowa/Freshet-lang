// statemachine — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 10)
// Stresses: enum/tag dispatch over a 32M-opcode interpreter loop.
// Hand-tuned: __restrict__ raw pointers into the opcode planes, local register
// state, same integer switch dispatch and identical operation order.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) uint64_t hot() {
    const uint64_t N = 32000000;
    const uint64_t M = 0x2545F4914F6CDD1DULL;
    const uint64_t K = 0x9E3779B97F4A7C15ULL;

    // opcode stream (one draw per op, continuous PRNG)
    const size_t NN = static_cast<size_t>(N);
    std::vector<uint8_t> tags(NN);
    std::vector<uint64_t> args(NN);
    uint64_t s = 88172645463325252ULL;
    {
        uint8_t* __restrict__ tp = tags.data();
        uint64_t* __restrict__ ap = args.data();
        for (size_t i = 0; i < NN; ++i) {
            s ^= s >> 12;
            s ^= s << 25;
            s ^= s >> 27;
            uint64_t draw = s * M;
            tp[i] = static_cast<uint8_t>((draw >> 61) & 7u);
            ap[i] = draw;
        }
    }

    // interpreter
    const uint8_t* __restrict__ tp = tags.data();
    const uint64_t* __restrict__ ap = args.data();
    uint64_t pc = 0;
    uint64_t acc = K;
    uint64_t flag = 0;  // 0 = false, 1 = true
    uint64_t steps = 0;
    while (pc < N) {
        const uint8_t t = tp[pc];
        const uint64_t a = ap[pc];
        switch (t) {
            case 0:  // Add
                acc = acc + a;
                break;
            case 1:  // Mul
                acc = acc * (a | 1u);
                break;
            case 2:  // Xor
                acc = acc ^ a;
                break;
            case 3: {  // Rot
                const uint64_t k = a & 63u;
                if (k != 0) {
                    acc = (acc << k) | (acc >> (64u - k));
                }
                break;
            }
            case 4:  // Cmp
                flag = (acc < a) ? 1u : 0u;
                break;
            case 5:  // Jmp
                pc = pc + 1u + (a & 7u);
                steps = steps + 1u;
                continue;
            case 6:  // Nop
                break;
            case 7:  // Sub
                acc = acc - a;
                break;
            default:
                break;
        }
        pc = pc + 1u;
        steps = steps + 1u;
    }

    return acc ^ (steps * K) ^ flag;
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
