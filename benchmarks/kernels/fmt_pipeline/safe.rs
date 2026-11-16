// safe.rs — Kernel 11 "fmt_pipeline": integer/float formatting + owned-string
// append/scan churn with an FNV byte fold. Serial. CS type: u64.
// Normative spec: ../KERNELS.md (fsht-01:01).
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 200_000;
const FNV_BASIS: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

#[inline(never)]
fn hot() -> u64 {
    let mut cs: u64 = FNV_BASIS;
    for i in 0..N {
        let q: f64 = (i & 1023) as f64 * 0.25;
        let mut s: String = String::new();
        s.push_str(&i.to_string());
        s.push('-');
        s.push_str(&format!("{:.3}", q));
        s.push(';');
        for &b in s.as_bytes() {
            cs = (cs ^ (b as u64)).wrapping_mul(FNV_PRIME);
        }
    }
    cs
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
