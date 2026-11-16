// safe.rs — Kernel 09 "radix_sort": u64 key sort + FNV fold. safe Rust uses
// sort_unstable — the "what the language gives you" comparison. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01), PRNG per section 4. CS type: u64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 2_000_000;
const ROUNDS: usize = 4;
const SEED: u64 = 88172645463325252;
const MUL: u64 = 0x2545F4914F6CDD1D;
const FNV_BASIS: u64 = 0xcbf29ce484222325;
const FNV_PRIME: u64 = 0x100000001b3;

#[inline(never)]
fn hot() -> u64 {
    let mut s: u64 = SEED;
    let mut cs: u64 = FNV_BASIS;
    let mut keys: Vec<u64> = vec![0u64; N];
    for _r in 0..ROUNDS {
        // regenerate keys from the continuous (never re-seeded) PRNG
        for i in 0..N {
            s ^= s >> 12;
            s ^= s << 25;
            s ^= s >> 27;
            let draw: u64 = s.wrapping_mul(MUL);
            keys[i] = draw >> 32;
        }
        keys.sort_unstable();
        // fold the sorted keys into the persistent checksum
        for i in 0..N {
            cs = (cs ^ keys[i]).wrapping_mul(FNV_PRIME);
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
