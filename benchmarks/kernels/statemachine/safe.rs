// safe.rs — Kernel 10 "statemachine": enum/match dispatch interpreter.
// The Vec<Op> stream is built (untimed, before the hot loop) from the
// continuous PRNG. Op::Rot and Op::Nop carry no payload per the spec's enum,
// so the interpreter reads args[pc] for Rot. Serial. CS type: u64.
// Normative spec: ../KERNELS.md (fsht-01:01), PRNG per section 4.
// Build: rustc -O safe.rs. stdout: "TIME <ns>" then "CS <cs>", exit 0.

const N: usize = 32_000_000;
const SEED: u64 = 88172645463325252;
const MUL: u64 = 0x2545F4914F6CDD1D;
const ACC0: u64 = 0x9E3779B97F4A7C15;

#[derive(Clone, Copy)]
enum Op {
    Add(u64),
    Mul(u64),
    Xor(u64),
    Rot,
    Cmp(u64),
    Jmp(u64),
    Nop,
    Sub(u64),
}

#[inline(never)]
fn hot() -> u64 {
    // opcode stream from the continuous PRNG (before the hot loop)
    let mut s: u64 = SEED;
    let mut tags: Vec<u8> = vec![0u8; N];
    let mut args: Vec<u64> = vec![0u64; N];
    for i in 0..N {
        s ^= s >> 12;
        s ^= s << 25;
        s ^= s >> 27;
        let draw: u64 = s.wrapping_mul(MUL);
        tags[i] = ((draw >> 61) & 7) as u8;
        args[i] = draw;
    }
    // build the Vec<Op> (idiomatic Rust dispatch shape)
    let mut ops: Vec<Op> = Vec::with_capacity(N);
    for i in 0..N {
        let op: Op = match tags[i] {
            0 => Op::Add(args[i]),
            1 => Op::Mul(args[i]),
            2 => Op::Xor(args[i]),
            3 => Op::Rot,
            4 => Op::Cmp(args[i]),
            5 => Op::Jmp(args[i]),
            6 => Op::Nop,
            _ => Op::Sub(args[i]),
        };
        ops.push(op);
    }
    // hot interpreter loop
    let mut pc: usize = 0;
    let mut acc: u64 = ACC0;
    let mut flag: bool = false;
    let mut steps: u64 = 0;
    while pc < N {
        let op: Op = ops[pc];
        match op {
            Op::Add(v) => {
                acc = acc.wrapping_add(v);
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Mul(v) => {
                acc = acc.wrapping_mul(v | 1);
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Xor(v) => {
                acc = acc ^ v;
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Rot => {
                let k: u64 = args[pc] & 63;
                if k != 0 {
                    acc = (acc << k) | (acc >> (64 - k));
                }
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Cmp(v) => {
                flag = acc < v;
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Jmp(v) => {
                pc = pc.wrapping_add(1).wrapping_add((v & 7) as usize);
                steps = steps.wrapping_add(1);
            }
            Op::Nop => {
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
            Op::Sub(v) => {
                acc = acc.wrapping_sub(v);
                pc = pc.wrapping_add(1);
                steps = steps.wrapping_add(1);
            }
        }
    }
    let f: u64 = if flag { 1 } else { 0 };
    acc ^ steps.wrapping_mul(ACC0) ^ f
}

fn main() {
    let t0 = std::time::Instant::now();
    let cs = hot();
    let ns = t0.elapsed().as_nanos() as u64;
    println!("TIME {}", ns);
    println!("CS {}", cs);
}
