// nbody — idiomatic C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 05)
// Stresses: sqrt/div-heavy pairwise physics, per-body inner reduction, AoS layout.
// Clean idiomatic style: array of structs (Body) + scratch vector, exact spec
// per-operation FP order (no refactors, no FMA).
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>
#include <cmath>

struct Body {
    double x, y, z, vx, vy, vz, m;
};

struct Acc {
    double ax, ay, az;
};

__attribute__((noinline)) int64_t hot() {
    const int B = 2048;
    const int S = 10;
    const double dt = 0.00001;
    const double eps2 = 0.0625;

    std::vector<Body> bodies(static_cast<size_t>(B));
    for (int i = 0; i < B; ++i) {
        bodies[static_cast<size_t>(i)].x = static_cast<double>(i & 63) * 0.25;
        bodies[static_cast<size_t>(i)].y = static_cast<double>(i & 31) * 0.5;
        bodies[static_cast<size_t>(i)].z = static_cast<double>(i & 15) * 0.125;
        bodies[static_cast<size_t>(i)].vx = 0.0;
        bodies[static_cast<size_t>(i)].vy = 0.0;
        bodies[static_cast<size_t>(i)].vz = 0.0;
        bodies[static_cast<size_t>(i)].m = 1.0 + static_cast<double>(i & 7) * 0.125;
    }
    std::vector<Acc> accs(static_cast<size_t>(B));

    for (int s = 0; s < S; ++s) {
        // phase 1 (forces): self-interaction j == i included
        for (int i = 0; i < B; ++i) {
            double ax = 0.0;
            double ay = 0.0;
            double az = 0.0;
            for (int j = 0; j < B; ++j) {
                double dx = bodies[static_cast<size_t>(j)].x -
                            bodies[static_cast<size_t>(i)].x;
                double dy = bodies[static_cast<size_t>(j)].y -
                            bodies[static_cast<size_t>(i)].y;
                double dz = bodies[static_cast<size_t>(j)].z -
                            bodies[static_cast<size_t>(i)].z;
                double r2 = dx * dx + dy * dy + dz * dz + eps2;
                double inv = 1.0 / std::sqrt(r2);
                double inv3 = inv * inv * inv;
                double mm = bodies[static_cast<size_t>(j)].m * inv3;
                ax = ax + dx * mm;
                ay = ay + dy * mm;
                az = az + dz * mm;
            }
            accs[static_cast<size_t>(i)].ax = ax;
            accs[static_cast<size_t>(i)].ay = ay;
            accs[static_cast<size_t>(i)].az = az;
        }
        // phase 2 (integrate)
        for (int i = 0; i < B; ++i) {
            bodies[static_cast<size_t>(i)].vx =
                bodies[static_cast<size_t>(i)].vx + accs[static_cast<size_t>(i)].ax * dt;
            bodies[static_cast<size_t>(i)].vy =
                bodies[static_cast<size_t>(i)].vy + accs[static_cast<size_t>(i)].ay * dt;
            bodies[static_cast<size_t>(i)].vz =
                bodies[static_cast<size_t>(i)].vz + accs[static_cast<size_t>(i)].az * dt;
            bodies[static_cast<size_t>(i)].x =
                bodies[static_cast<size_t>(i)].x + bodies[static_cast<size_t>(i)].vx * dt;
            bodies[static_cast<size_t>(i)].y =
                bodies[static_cast<size_t>(i)].y + bodies[static_cast<size_t>(i)].vy * dt;
            bodies[static_cast<size_t>(i)].z =
                bodies[static_cast<size_t>(i)].z + bodies[static_cast<size_t>(i)].vz * dt;
        }
    }

    double sum = 0.0;
    for (int i = 0; i < B; ++i) {
        const Body& b = bodies[static_cast<size_t>(i)];
        sum = sum + (b.x + b.y + b.z + b.vx + b.vy + b.vz + b.m);
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
