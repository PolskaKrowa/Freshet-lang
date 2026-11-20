# Freshet-lang benchmark kernels — normative specification (fsht-03:03)

This file is the **single source of truth** for the 12 benchmark kernels of the
Freshet-lang suite. Every implementation (`freshet.fsht`, `idiomatic.cpp`,
`tuned.cpp`, `safe.rs`) must follow it exactly, so that all four produce
**bit-identical checksums** on the same machine. The kernels target the
fsht-01:01 feature surface, which remains valid under fsht-03:03.

Companion files per kernel directory: `kernel.json` (machine-readable summary),
`freshet.fsht`, `idiomatic.cpp`, `tuned.cpp`, `safe.rs`.

## 1. Global output contract

Every program, in every language, writes **exactly two lines** to stdout and
nothing else, then exits with code 0:

```
TIME <uint64 decimal>
CS <cs-type decimal>
```

* `TIME` — nanoseconds of the hot region, measured with a **monotonic clock
  inside the program** (`freshet.time_ns()`, `std::chrono::steady_clock`,
  `std::time::Instant`). The value varies between runs; it is only used for
  timing, never for correctness.
* `CS` — the checksum. Its decimal spelling must be **identical across all
  four implementations, all optimisation levels and all repeat runs**.
  The type is per-kernel (`u64` or `i64`), declared in `kernel.json`.

stderr must stay empty. Any diagnostic text on stderr is an implementation
error.

## 2. Hot-function contract

The whole computation (setup + hot loops + checksum) lives in one function
`hot()`, called from `main()`:

| language | spelling |
|---|---|
| Freshet | `@noinline fn hot() -> u64` (or `-> i64` for the i64 checksums) |
| C++ (both) | `__attribute__((noinline)) uint64_t hot()` / `int64_t` |
| Rust | `#[inline(never)] fn hot() -> u64` / `i64` |

`main()` does nothing except: call `hot()` under the monotonic clock, print
the two lines. The **timed region includes the O(N) setup**, identically in
every language — this is deliberate and documented in the methodology.

## 3. Floating-point determinism rules

1. No fast-math anywhere. The C++ harness compiles with `-O2
   -ffp-contract=off`; implementations may add `#pragma STDC FP_CONTRACT OFF`.
2. Write every floating-point expression in **exactly the order** given in
   the kernel spec — no algebraic refactors, no constant distribution, no
   FMA rewrites. Rust must **never** use `mul_add` (it breaks bit-identity).
3. Most checksum accumulations are deliberately **exact dyadic** arithmetic
   (multiples of 0.25/0.5 with magnitudes below 2^53), so any reduction
   grouping yields the same bits; the non-dyadic kernels (`stencil`, `nbody`)
   rely on identical per-operation IEEE-754 evaluation order instead.
4. Integer checksum chains use **unsigned 64-bit arithmetic** (wrapping is
   defined in C++, C++, Rust release and Freshet alike). Never use signed
   overflow.

## 4. Reference PRNG (kernels `prng_bits`, `radix_sort`, `statemachine`)

xorshift64\*, one draw per advance, state seeded with `88172645463325252`:

```
s ^= s >> 12;   s ^= s << 25;   s ^= s >> 27;   draw = s * 0x2545F4914F6CDD1D
```

All state is `u64`. The PRNG stream is **continuous** across phases and
rounds (never re-seeded).

---

## Kernel 01 — `dot`

* Stresses: unit-stride f64 multiply-add sweep, loop-carried accumulation.
* Layout: Freshet `*f64` malloc buffers; every language uses flat
  contiguous arrays. **Serial.**
* Constants: `N = 4 000 000`, `R = 25`.
* Init (untimed semantics — inside `hot()`, timed like everything else):
  `x[i] = f64(i & 1023) * 0.5`, `y[i] = f64(i & 255) * 0.25 + 0.125`.
* Hot loops: `total = 0.0; for r in 0..R: for i in 0..N ascending:
  total += x[i] * y[i];`
* Checksum: `CS = i64(total * 65536.0)` — truncate toward zero on the
  f64→int cast. All terms are exact dyadics; the sum is exact (< 2^53).

## Kernel 02 — `axpy`

* Stresses: read-modify-write streaming (y = y + a·x). **Serial.**
* Constants: `N = 4 000 000`, `R = 25`, `a = 0.5`.
* Init: `x[i] = f64(i & 511) * 0.5`, `y[i] = f64(i & 255) * 0.25`.
* Hot: `for r in 0..R: for i ascending: y[i] += a * x[i];`
* Checksum: `s = Σ y[i]` (ascending i); `CS = i64(s * 65536.0)`. Exact
  dyadic throughout.

## Kernel 03 — `matmul`

* Stresses: dense f64 triple loop with the i-k-j (vectorisable) order,
  repeated accumulation into C. **Serial.**
* Constants: `N = 256` (N×N matrices, flat row-major), `R = 50`.
* Init: `A[i*N+j] = f64((i*7 + j*13) & 63) * 0.25`,
  `B[i*N+j] = f64((i*11 + j*3) & 15) * 0.5`, `C` zero-filled.
* Hot (exact loop order):
  `for r in 0..R: for i in 0..N: for k in 0..N: { aik = A[i*N+k];
  for j in 0..N: C[i*N+j] += aik * B[k*N+j]; } }`
* Checksum: `s = Σ_{idx=0..N*N-1} C[idx]` ascending; `CS = i64(s * 65536.0)`.
  Exact dyadic.

## Kernel 04 — `stencil`

* Stresses: 2-D 5-point Jacobi with double buffering, non-dyadic rounding
  (0.2 factors). **Serial.**
* Constants: `G = 1024` (G×G grids, flat), `T = 60` iterations.
* Init: both buffers `A[idx] = B[idx] = f64(idx & 63) * 0.25`.
* Hot: for `t in 0..T`: for `i in 1..G-1`, `j in 1..G-1` (row-major):

  ```
  B[i*G+j] = 0.2*A[(i-1)*G+j] + 0.2*A[(i+1)*G+j] + 0.2*A[i*G+j-1]
           + 0.2*A[i*G+j+1] + 0.2*A[i*G+j];
  ```

  (order: up, down, left, right, centre — exactly this expression tree.)
  Then swap the two buffers.
* Checksum: after the loop, `s1 = Σ A[idx]`, `s2 = Σ B[idx]` (both flat,
  ascending over `0..G*G-1`); `CS = i64((s1 + s2) * 65536.0)`.

## Kernel 05 — `nbody`

* Stresses: sqrt/div-heavy pairwise physics, per-body inner reduction,
  struct layout. **Serial in every implementation.** Freshet uses
  `soa(Body)`; idiomatic C++/Rust use an array of structs; tuned C++ uses
  flat planes — the layout story is the comparison point, and the checksum
  is layout-independent because every language evaluates the same
  per-operation order.
* Constants: `B = 2048` bodies, `S = 10` steps, `dt = 0.00001`,
  `eps2 = 0.0625`.
* Body state: `x, y, z, vx, vy, vz, m` (f64 planes/fields) plus three
  scratch planes `ax, ay, az`.
* Init: `x[i] = f64(i & 63) * 0.25`, `y[i] = f64(i & 31) * 0.5`,
  `z[i] = f64(i & 15) * 0.125`, `vx = vy = vz = 0.0`,
  `m[i] = 1.0 + f64(i & 7) * 0.125`.
* Per step, two phases (self-interaction j == i included — dx=dy=dz=0,
  no special case, no NaNs because r2 ≥ eps2):

  ```
  phase 1 (forces): for i in 0..B:
      ax = ay = az = 0.0
      for j in 0..B:
          dx = x[j] - x[i];  dy = y[j] - y[i];  dz = z[j] - z[i]
          r2  = dx*dx + dy*dy + dz*dz + eps2
          inv = 1.0 / sqrt(r2)
          inv3 = inv * inv * inv
          mm  = m[j] * inv3
          ax = ax + dx*mm;  ay = ay + dy*mm;  az = az + dz*mm
      store axv[i] = ax; ayv[i] = ay; azv[i] = az
  phase 2 (integrate): for i in 0..B:
      vx[i] = vx[i] + axv[i]*dt;  vy[i] = vy[i] + ayv[i]*dt;  vz[i] = vz[i] + azv[i]*dt
      x[i]  = x[i]  + vx[i]*dt;   y[i]  = y[i]  + vy[i]*dt;   z[i]  = z[i]  + vz[i]*dt
  ```
* Checksum: `s = Σ_i ascending (x[i] + y[i] + z[i] + vx[i] + vy[i] + vz[i]
  + m[i])`; `CS = i64(s * 65536.0)`.

## Kernel 06 — `sumreduce`

* Stresses: parallel f64 reduction. Freshet uses
  `@reproducible parfor [reduction(+:acc)]`; idiomatic C++/Rust are serial;
  **tuned C++ is the only other parallel version** (16 `std::thread`
  chunks, per-chunk partials combined in ascending chunk order — bit-wise
  the serial fold, and the data is exact dyadic anyway).
* Constants: `N = 32 000 000`, `R = 4`.
* Init: `d[i] = f64(i & 1023) * 0.5 + 0.25` — exact dyadics make the sum
  grouping-independent (this kernel is about reduction *speed*, not
  reproducibility; the reproducibility property itself is tested in
  `tests/props/`).
* Hot: `total = 0.0; for r in 0..R: { acc = Σ d[i] over [0,N);
  total = total + acc; }`
* Checksum: `CS = i64(total * 65536.0)`.

## Kernel 07 — `soa_sweep`

* Stresses: AoS vs SoA layout on an 8-field struct with 2 hot fields.
  Freshet uses `soa(P8)`; idiomatic C++/Rust use a vector of structs;
  tuned C++ uses 8 flat `double` planes (touching only the two hot ones).
  Freshet's hot sweep is `parfor [reduction(+:s)]` inside a serial reps
  loop (the README hello-world shape); the C++/Rust sweeps are serial.
* Constants: `N = 4 000 000`, `R = 10`.
* Struct: `P8 { x, y, z, w, vx, vy, vz, vw : f64 }`.
* Init: `x[i] = 1.5`, `vy[i] = 2.5`, everything else 0.
* Hot: `s = 0.0; for r in 0..R: s += Σ_i (x[i] + vy[i]);`
* Checksum: `CS = i64(s * 65536.0)`.

## Kernel 08 — `prng_bits`

* Stresses: integer pipeline (shift/xor/mul chains), no memory traffic
  beyond the accumulator. **Serial.**
* Constants: `N = 128 000 000` draws.
* Hot: `s = 88172645463325252; acc = 0;` repeat N times: advance the PRNG
  (section 4); `acc ^= draw`.
* Checksum: `CS = acc` (`u64`).

## Kernel 09 — `radix_sort`

* Stresses: memory-bound bucket pass over u64 keys. Freshet and tuned C++
  implement the same LSB radix sort (4 passes × 8 bits, 256 buckets,
  counting + prefix + scatter); **idiomatic C++ uses `std::sort`; safe Rust
  uses `sort_unstable`** — the honest "what does the language give you"
  comparison the suite exists for.
* Constants: `N = 2 000 000` keys per round, `ROUNDS = 4`, `PASSES = 4`
  (radix 8 bits). Keys are `u64` with value < 2^32 (draw >> 32), so four
  passes fully sort them.
* Per round: regenerate keys from the continuous PRNG (`key[i] = draw >>
  32`), sort ascending, then fold into the running checksum:

  ```
  for i ascending: cs = (cs ^ key[i]) * 0x100000001b3
  ```

  with `cs` initialised to `0xcbf29ce484222325` before round 0 and
  **persisting across rounds**.
* Checksum: `CS = cs` (`u64`).

## Kernel 10 — `statemachine`

* Stresses: enum/tagged-union dispatch (`match` in Freshet/Rust, `switch`
  in C++) over a 32M-opcode interpreter loop. The opcode stream is
  generated **untimed**, before the hot loop, from the continuous PRNG:
  `tags[i] = u8((draw >> 61) & 7)` (the Freshet implementation keeps the
  tags as `u64` to avoid a narrowing cast — the in-memory tag type is an
  implementation detail), `args[i] = draw`.
* Constants: `N = 32 000 000` ops. Memory note: the Rust `Vec<Op>` shape
  needs ~800 MB (ops + args + tags); the C++/Freshet tag-array shapes need
  ~288 MB.
* Hot loop — machine state: `pc = 0`, `acc = 0x9E3779B97F4A7C15` (`u64`),
  `flag = false`, `steps = 0` (`u64`). The opcode stream is generated inside
  `hot()` (so it is timed like every setup loop in this suite) but strictly
  before the interpreter loop.

| t | op | action |
|---|---|---|
| 0 | Add | `acc = acc + a` |
| 1 | Mul | `acc = acc * (a \| 1)` |
| 2 | Xor | `acc = acc ^ a` |
| 3 | Rot | `k = a & 63; if k != 0: acc = (acc << k) \| (acc >> (64 - k))` |
| 4 | Cmp | `flag = (acc < a)` |
| 5 | Jmp | `pc = pc + 1 + (a & 7); steps += 1; continue` |
| 6 | Nop | nothing |
| 7 | Sub | `acc = acc - a` |

  For every op **except Jmp**: perform the action, then
  `pc = pc + 1; steps = steps + 1;`
* Checksum: `CS = acc ^ (steps * 0x9E3779B97F4A7C15) ^ (flag ? 1 : 0)`
  (`u64`; in Freshet, `let f: u64 = 0; if (flag) { f = 1; }`).
* Enum naming (payload types as in the table): Freshet/Rust
  `enum Op { Add(u64), Mul(u64), Xor(u64), Rot, Cmp(u64), Jmp(u64), Nop,
  Sub(u64) }`. Freshet converts each tag per step through a `to_op` helper
  (`if (c == 0) { return Add(a); } ...`); Rust builds a `Vec<Op>` untimed
  (the idiomatic shape); C++ switches on the integer tag. The asymmetry is
  deliberate and documented: it measures how each language's *idiomatic*
  dispatch compiles.
* `steps` ends at 22 255 005 on the reference stream (sanity anchor for
  implementations).

## Kernel 11 — `fmt_pipeline`

* Stresses: integer/float formatting + owned-string append/scan churn.
  `fmt_i64`/`fmt_f64` in Freshet; `std::to_string` + `ostringstream` in
  idiomatic C++; manual `itoa`/fixed-point emitter in tuned C++;
  `format!`/`push_str` in safe Rust. **Serial.**
* Constants: `N = 200 000` iterations, FNV basis
  `0xcbf29ce484222325`, FNV prime `0x100000001b3`.
* Per iteration `i`: `q = f64(i & 1023) * 0.25` (exact dyadic, ≤ 255.75);
  build the string `S = "<i decimal>-" "<q with exactly 3 decimals>" ";"`
  (e.g. `i = 7` → `"7-1.750;"`); then for each byte `b` of `S` in order:
  `cs = (cs ^ b) * prime`. `cs` persists across iterations.
* Byte iteration covers exactly the bytes of `S` (no NUL terminator).
* Checksum: `CS = cs` (`u64`).

## Kernel 12 — `calls`

* Stresses: call overhead — three `@noinline`/`noinline`/`#[inline(never)]`
  helper calls per element plus an **indirect** call through a function
  pointer, with a per-16 branchy selector. **Serial.**
* Constants: `N = 10 000 000`;
  `C1 = 0x9E3779B97F4A7C15`, `C2 = 0xBF58476D1CE4E5B9`,
  `C3 = 0x94D049BB133111EF`, `C4 = 0x2545F4914F6CDD1D`,
  `C5 = 0x9E3779B1`, `C6 = 0x85EBCA77`, `C7 = 0xC2B2AE3D`.
* Helpers (all u64, wrapping): `add64(a,b) = a + b`,
  `mul64(a,b) = a * b`, `xor64(a,b) = a ^ b`.
* Hot loop: `acc = 0` (u64); per element `i`: `x = (u64(i) * C1) + 7`
  (wrapping);
  every 16th element (`(i & 15) == 0`) re-select the indirect target:
  `sel = ((i >> 4) & 1) == 0 ? add64 : xor64` (a `fn(u64,u64)->u64`
  pointer variable);
  then — if `(i & 1) == 0`: `r = dispatch(sel, x)` where
  `dispatch(f: fn(u64,u64)->u64, x: u64) -> u64 { a = f(x, C5);
  b = mul64(a, C6); return add64(b, C7); }`;
  else: `r = direct3(x)` where
  `direct3(x: u64) -> u64 { a = add64(x, C2); b = mul64(a, C3);
  return xor64(b, C4); }`.
  Finally `acc ^= r`.
* Checksum: `CS = acc` (`u64`).

---

## 5. Per-kernel implementation notes (what "idiomatic" and "tuned" mean)

* **idiomatic.cpp** — clean C++17: `std::vector`, indexed loops or
  range-for, no pragmas, no `restrict`, no manual alignment, no threads
  (except: none of the 12 kernels require them), the sort kernel uses
  `std::sort`. It is the code a competent C++ programmer writes first.
* **tuned.cpp** — hand-tuned C++17: the expert version — flat planes /
  SoA layouts where the kernel says so, `__restrict__`, loop unrolling,
  prefetch-friendly access, `std::thread` where the kernel policy says
  parallel (only `sumreduce`), manual radix sort and manual fixed-point
  formatting. No intrinsics and no OpenMP: the comparison target is
  *source-level tuning*, the thing Penstock claims to do for you.
* **safe.rs** — safe Rust, std-only, no `unsafe`, no external crates:
  `Vec`, iterators or indexed loops as idiomatic, `sort_unstable` for the
  sort kernel, `std::thread` where the kernel policy says parallel
  (`sumreduce`: scoped threads with ascending-chunk combine).
* **freshet.fsht** — natural Freshet: `parfor` + `@reproducible` where the
  kernel policy says parallel, `soa(Body)`/`soa(P8)` layouts, `malloc`
  buffers, `fmt_*` formatting. `@noinline` on `hot`.

Parallelism policy summary: `sumreduce` — Freshet `@reproducible parfor`,
tuned C++ threads, Rust scoped threads, idiomatic C++ serial; `soa_sweep` —
Freshet `parfor` reduction only, everything else serial; **all other
kernels serial in every language** (their story is codegen and layout, not
thread count — and the annotation workflow needs single-threaded
instruction-level comparison).
