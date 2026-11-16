// soa_sweep — tuned C++17 reference implementation (spec: ../KERNELS.md, fsht-01:01 §Kernel 07)
// Stresses: AoS vs SoA layout on an 8-field struct with 2 hot fields.
// Hand-tuned: SoA — 8 flat double planes, all initialised per the spec, but
// the hot sweep touches only the two hot planes (x and vy) through
// __restrict__ pointers, so each field strides memory alone.
#include <cstdio>
#include <cstdint>
#include <chrono>
#include <vector>

__attribute__((noinline)) int64_t hot() {
    const int N = 4000000;
    const int R = 10;
    const size_t NN = static_cast<size_t>(N);

    // 8 flat double planes
    std::vector<double> px(NN), py(NN), pz(NN), pw(NN);
    std::vector<double> pvx(NN), pvy(NN), pvz(NN), pvw(NN);
    double* __restrict__ x = px.data();
    double* __restrict__ y = py.data();
    double* __restrict__ z = pz.data();
    double* __restrict__ w = pw.data();
    double* __restrict__ vx = pvx.data();
    double* __restrict__ vy = pvy.data();
    double* __restrict__ vz = pvz.data();
    double* __restrict__ vw = pvw.data();

    for (int i = 0; i < N; ++i) {
        const size_t ii = static_cast<size_t>(i);
        x[ii] = 1.5;
        y[ii] = 0.0;
        z[ii] = 0.0;
        w[ii] = 0.0;
        vx[ii] = 0.0;
        vy[ii] = 2.5;
        vz[ii] = 0.0;
        vw[ii] = 0.0;
    }

    // hot sweep: only the two hot planes are touched
    double s = 0.0;
    const int n4 = N & ~3;
    for (int r = 0; r < R; ++r) {
        int i = 0;
        for (; i < n4; i += 4) {  // same sequential accumulation order, unrolled
            s += x[i] + vy[i];
            s += x[i + 1] + vy[i + 1];
            s += x[i + 2] + vy[i + 2];
            s += x[i + 3] + vy[i + 3];
        }
        for (; i < N; ++i) {
            s += x[i] + vy[i];
        }
    }

    return static_cast<int64_t>(s * 65536.0);  // truncate toward zero
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
