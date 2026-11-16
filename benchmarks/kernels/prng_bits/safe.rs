// safe.rs — Kernel 08 "prng_bits": xorshift64* integer PRNG stream. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01), PRNG per section 4. CS type: u64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 128_000_000;
const SEED: u64 = 88172645463325252;
const MUL: u64 = 0x2545F4914F6CDD1D;

#[inline(never)]
fn hot() -> u64 {
    let mut s: u64 = SEED;
    let mut acc: u64 = 0;
    for _ in 0..N {
        s ^= s >> 12;
        s ^= s << 25;
        s ^= s >> 27;
        acc ^= s.wrapping_mul(MUL);
    }
    acc
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
