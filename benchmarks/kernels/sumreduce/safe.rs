// safe.rs — Kernel 06 "sumreduce": f64 reduction. The ONLY parallel kernel:
// 16 std::thread::scope chunks, per-chunk partials joined in ascending chunk
// order (0,1,...,15). Data is exact dyadic, so the combine is bit-stable.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: i64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 32_000_000;
const R: usize = 4;
const CHUNKS: usize = 16;

#[inline(never)]
fn hot() -> i64 {
    let mut d: Vec<f64> = vec![0.0; N];
    for i in 0..N {
        d[i] = (i & 1023) as f64 * 0.5 + 0.25;
    }
    let mut total: f64 = 0.0;
    for _r in 0..R {
        let acc: f64 = std::thread::scope(|scope| {
            let chunk: usize = N / CHUNKS;
            let dref: &Vec<f64> = &d;
            let mut handles = Vec::with_capacity(CHUNKS);
            for c in 0..CHUNKS {
                let lo: usize = c * chunk;
                let hi: usize = if c + 1 == CHUNKS { N } else { (c + 1) * chunk };
                handles.push(scope.spawn(move || {
                    let mut s: f64 = 0.0;
                    for k in lo..hi {
                        s += dref[k];
                    }
                    s
                }));
            }
            // combine per-chunk partials in ascending chunk order
            let mut sum: f64 = 0.0;
            for h in handles {
                if let Ok(v) = h.join() {
                    sum += v;
                }
            }
            sum
        });
        total = total + acc;
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
