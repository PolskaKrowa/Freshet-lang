// safe.rs — Kernel 01 "dot": f64 dot product sweep, unit stride. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 4_000_000;
const R: usize = 25;

#[inline(never)]
fn hot() -> i64 {
    let mut x: Vec<f64> = vec![0.0; N];
    let mut y: Vec<f64> = vec![0.0; N];
    for i in 0..N {
        x[i] = (i & 1023) as f64 * 0.5;
        y[i] = (i & 255) as f64 * 0.25 + 0.125;
    }
    let mut total: f64 = 0.0;
    for _r in 0..R {
        for i in 0..N {
            total += x[i] * y[i];
        }
    }
    (total * 65536.0) as i64
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
