// safe.rs — Kernel 07 "soa_sweep": 8-field struct, 2 hot fields. Idiomatic
// Rust shape: Vec<P8> (array of structs); the SoA comparison is the tuned
// C++ story. Serial. Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 4_000_000;
const R: usize = 10;

// Only x and vy are ever read; the six cold fields are the point of the
// AoS-vs-SoA layout comparison, so the never-read lint is silenced here.
#[allow(dead_code)]
struct P8 {
    x: f64,
    y: f64,
    z: f64,
    w: f64,
    vx: f64,
    vy: f64,
    vz: f64,
    vw: f64,
}

#[inline(never)]
fn hot() -> i64 {
    let v: Vec<P8> = (0..N)
        .map(|_| P8 {
            x: 1.5,
            y: 0.0,
            z: 0.0,
            w: 0.0,
            vx: 0.0,
            vy: 2.5,
            vz: 0.0,
            vw: 0.0,
        })
        .collect();
    let mut s: f64 = 0.0;
    for _r in 0..R {
        let mut t: f64 = 0.0;
        for i in 0..N {
            t += v[i].x + v[i].vy;
        }
        s += t;
    }
    (s * 65536.0) as i64
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
