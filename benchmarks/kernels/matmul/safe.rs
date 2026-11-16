// safe.rs — Kernel 03 "matmul": dense f64 matrix multiply, i-k-j order. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 256; // N x N matrices, flat row-major
const R: usize = 50;

#[inline(never)]
fn hot() -> i64 {
    let nn: usize = N * N;
    let mut a: Vec<f64> = vec![0.0; nn];
    let mut b: Vec<f64> = vec![0.0; nn];
    let mut c: Vec<f64> = vec![0.0; nn];
    for i in 0..N {
        for j in 0..N {
            a[i * N + j] = ((i * 7 + j * 13) & 63) as f64 * 0.25;
            b[i * N + j] = ((i * 11 + j * 3) & 15) as f64 * 0.5;
        }
    }
    for _r in 0..R {
        for i in 0..N {
            for k in 0..N {
                let aik: f64 = a[i * N + k];
                for j in 0..N {
                    c[i * N + j] += aik * b[k * N + j];
                }
            }
        }
    }
    let mut s: f64 = 0.0;
    for idx in 0..nn {
        s += c[idx];
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
