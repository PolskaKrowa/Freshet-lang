// fmt_pipeline — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 11)
// Stresses: integer/float formatting + owned-string append/scan churn.
// Hand-tuned: manual char-buffer formatting — the integer via repeated /10,
// the fixed 3-decimal fraction via exact integer math (q*100 = (i&1023)*25 is
// an exact integer because every q is a dyadic multiple of 0.25; int part =
// q100/100, fraction = q100%100), then a byte-scan FNV-style fold over the
// emitted buffer. No ostringstream, no std::string allocation in the loop.
#include <cstdio>
#include <cstdint>
#include <chrono>

__attribute__((noinline)) uint64_t hot() {
    const uint64_t N = 200000;
    const uint64_t PRIME = 0x100000001B3ULL;

    uint64_t cs = 0xCBF29CE484222325ULL;  // FNV basis, persists across iterations

    char buf[32];
    for (uint64_t i = 0; i < N; ++i) {
        int len = 0;

        // <i decimal> via repeated /10
        {
            char tmp[24];
            int tl = 0;
            uint64_t v = i;
            do {
                tmp[tl++] = static_cast<char>('0' + (v % 10u));
                v /= 10u;
            } while (v != 0u);
            while (tl > 0) {
                buf[len++] = tmp[--tl];
            }
        }
        buf[len++] = '-';

        // <q with exactly 3 decimals>: q = (i & 1023) * 0.25, so q*100 is the
        // exact integer (i & 1023) * 25 — int part /100, fraction %100.
        const uint64_t q100 = (i & 1023u) * 25u;
        {
            char tmp[8];
            int tl = 0;
            uint64_t v = q100 / 100u;  // integer part of q
            do {
                tmp[tl++] = static_cast<char>('0' + (v % 10u));
                v /= 10u;
            } while (v != 0u);
            while (tl > 0) {
                buf[len++] = tmp[--tl];
            }
        }
        buf[len++] = '.';
        const uint64_t fr = q100 % 100u;  // fraction in hundredths (0, 25, 50, 75)
        buf[len++] = static_cast<char>('0' + (fr / 10u));  // tenths
        buf[len++] = static_cast<char>('0' + (fr % 10u));  // hundredths
        buf[len++] = '0';  // thousandths: always 0 — q is a dyadic multiple of 0.25
        buf[len++] = ';';

        // fold every byte of S in order
        for (int b = 0; b < len; ++b) {
            cs = (cs ^ static_cast<uint64_t>(static_cast<unsigned char>(buf[b]))) * PRIME;
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
