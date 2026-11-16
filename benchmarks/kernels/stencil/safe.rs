// safe.rs — Kernel 04 "stencil": 2-D 5-point Jacobi, double buffered. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const G: usize = 1024; // G x G grid, flat
const T: usize = 60;

#[inline(never)]
fn hot() -> i64 {
    let n: usize = G * G;
    let mut a: Vec<f64> = vec![0.0; n];
    let mut b: Vec<f64> = vec![0.0; n];
    for idx in 0..n {
        let v: f64 = (idx & 63) as f64 * 0.25;
        a[idx] = v;
        b[idx] = v;
    }
    for _t in 0..T {
        for i in 1..G - 1 {
            for j in 1..G - 1 {
                b[i * G + j] = 0.2 * a[(i - 1) * G + j]
                    + 0.2 * a[(i + 1) * G + j]
                    + 0.2 * a[i * G + j - 1]
                    + 0.2 * a[i * G + j + 1]
                    + 0.2 * a[i * G + j];
            }
        }
        std::mem::swap(&mut a, &mut b);
    }
    let mut s1: f64 = 0.0;
    let mut s2: f64 = 0.0;
    for idx in 0..n {
        s1 += a[idx];
        s2 += b[idx];
    }
    ((s1 + s2) * 65536.0) as i64
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
