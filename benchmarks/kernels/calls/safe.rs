// safe.rs — Kernel 12 "calls": call overhead — noinline direct helpers plus
// an indirect call through a fn pointer with a per-16 selector. Serial.
// Normative spec: ../KERNELS.md (fsht-01:01). CS type: u64.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 10_000_000;
const C1: u64 = 0x9E3779B97F4A7C15;
const C2: u64 = 0xBF58476D1CE4E5B9;
const C3: u64 = 0x94D049BB133111EF;
const C4: u64 = 0x2545F4914F6CDD1D;
const C5: u64 = 0x9E3779B1;
const C6: u64 = 0x85EBCA77;
const C7: u64 = 0xC2B2AE3D;

#[inline(never)]
fn add64(a: u64, b: u64) -> u64 {
    a.wrapping_add(b)
}

#[inline(never)]
fn mul64(a: u64, b: u64) -> u64 {
    a.wrapping_mul(b)
}

#[inline(never)]
fn xor64(a: u64, b: u64) -> u64 {
    a ^ b
}

#[inline(never)]
fn dispatch(f: fn(u64, u64) -> u64, x: u64) -> u64 {
    let a: u64 = f(x, C5);
    let b: u64 = mul64(a, C6);
    add64(b, C7)
}

#[inline(never)]
fn direct3(x: u64) -> u64 {
    let a: u64 = add64(x, C2);
    let b: u64 = mul64(a, C3);
    xor64(b, C4)
}

#[inline(never)]
fn hot() -> u64 {
    let mut acc: u64 = 0;
    let mut sel: fn(u64, u64) -> u64 = add64;
    for i in 0..N {
        let x: u64 = (i as u64).wrapping_mul(C1).wrapping_add(7);
        if (i & 15) == 0 {
            // re-select the indirect target every 16th element
            if ((i >> 4) & 1) == 0 {
                sel = add64;
            } else {
                sel = xor64;
            }
        }
        let r: u64 = if (i & 1) == 0 {
            dispatch(sel, x)
        } else {
            direct3(x)
        };
        acc ^= r;
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
