// nbody — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 05)
// Stresses: sqrt/div-heavy pairwise physics, per-body inner reduction, layout.
// Hand-tuned: SoA flat planes — 10 __restrict__ double arrays (x,y,z,vx,vy,vz,m
// + scratch axv,ayv,azv), hoisted per-i body values, 2-way unrolled j sweep
// keeping the spec's exact sequential accumulation order (no FP refactors).
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <cmath>

__attribute__((noinline)) int64_t hot() {
    const int B = 2048;
    const int S = 10;
    const double dt = 0.00001;
    const double eps2 = 0.0625;
    const size_t BN = static_cast<size_t>(B);

    // 10 flat planes: body state + scratch accelerations
    std::vector<double> px(BN), py(BN), pz(BN);
    std::vector<double> pvx(BN), pvy(BN), pvz(BN), pm(BN);
    std::vector<double> axv(BN), ayv(BN), azv(BN);
    double* __restrict__ xs = px.data();
    double* __restrict__ ys = py.data();
    double* __restrict__ zs = pz.data();
    double* __restrict__ vxs = pvx.data();
    double* __restrict__ vys = pvy.data();
    double* __restrict__ vzs = pvz.data();
    double* __restrict__ ms = pm.data();
    double* __restrict__ axs = axv.data();
    double* __restrict__ ays = ayv.data();
    double* __restrict__ azs = azv.data();

    for (int i = 0; i < B; ++i) {
        xs[i] = static_cast<double>(i & 63) * 0.25;
        ys[i] = static_cast<double>(i & 31) * 0.5;
        zs[i] = static_cast<double>(i & 15) * 0.125;
        vxs[i] = 0.0;
        vys[i] = 0.0;
        vzs[i] = 0.0;
        ms[i] = 1.0 + static_cast<double>(i & 7) * 0.125;
    }

    const int b2 = B & ~1;
    for (int s = 0; s < S; ++s) {
        // phase 1 (forces): self-interaction j == i included
        for (int i = 0; i < B; ++i) {
            const double xi = xs[i];
            const double yi = ys[i];
            const double zi = zs[i];
            double ax = 0.0;
            double ay = 0.0;
            double az = 0.0;
            int j = 0;
            for (; j < b2; j += 2) {  // same sequential order, unrolled
                {
                    const double dx = xs[j] - xi;
                    const double dy = ys[j] - yi;
                    const double dz = zs[j] - zi;
                    const double r2 = dx * dx + dy * dy + dz * dz + eps2;
                    const double inv = 1.0 / std::sqrt(r2);
                    const double inv3 = inv * inv * inv;
                    const double mm = ms[j] * inv3;
                    ax = ax + dx * mm;
                    ay = ay + dy * mm;
                    az = az + dz * mm;
                }
                {
                    const double dx = xs[j + 1] - xi;
                    const double dy = ys[j + 1] - yi;
                    const double dz = zs[j + 1] - zi;
                    const double r2 = dx * dx + dy * dy + dz * dz + eps2;
                    const double inv = 1.0 / std::sqrt(r2);
                    const double inv3 = inv * inv * inv;
                    const double mm = ms[j + 1] * inv3;
                    ax = ax + dx * mm;
                    ay = ay + dy * mm;
                    az = az + dz * mm;
                }
            }
            for (; j < B; ++j) {
                const double dx = xs[j] - xi;
                const double dy = ys[j] - yi;
                const double dz = zs[j] - zi;
                const double r2 = dx * dx + dy * dy + dz * dz + eps2;
                const double inv = 1.0 / std::sqrt(r2);
                const double inv3 = inv * inv * inv;
                const double mm = ms[j] * inv3;
                ax = ax + dx * mm;
                ay = ay + dy * mm;
                az = az + dz * mm;
            }
            axs[i] = ax;
            ays[i] = ay;
            azs[i] = az;
        }
        // phase 2 (integrate)
        for (int i = 0; i < B; ++i) {
            vxs[i] = vxs[i] + axs[i] * dt;
            vys[i] = vys[i] + ays[i] * dt;
            vzs[i] = vzs[i] + azs[i] * dt;
            xs[i] = xs[i] + vxs[i] * dt;
            ys[i] = ys[i] + vys[i] * dt;
            zs[i] = zs[i] + vzs[i] * dt;
        }
    }

    double sum = 0.0;
    for (int i = 0; i < B; ++i) {
        sum = sum + (xs[i] + ys[i] + zs[i] + vxs[i] + vys[i] + vzs[i] + ms[i]);
    }

    return static_cast<int64_t>(sum * 65536.0);  // truncate toward zero
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
