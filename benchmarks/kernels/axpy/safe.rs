// safe.rs — Kernel 02 "axpy": y = y + a*x streaming read-modify-write. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 4_000_000;
const R: usize = 25;
const A: f64 = 0.5;

#[inline(never)]
fn hot() -> i64 {
    let mut x: Vec<f64> = vec![0.0; N];
    let mut y: Vec<f64> = vec![0.0; N];
    for i in 0..N {
        x[i] = (i & 511) as f64 * 0.5;
        y[i] = (i & 255) as f64 * 0.25;
    }
    for _r in 0..R {
        for i in 0..N {
            y[i] += A * x[i];
        }
    }
    let mut s: f64 = 0.0;
    for i in 0..N {
        s += y[i];
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
