# Freshet-lang benchmark suite (fsht-03:03)

> Version note: the 12 kernels exercise the fsht-01:01 feature surface,
> which remains valid under fsht-03:03. Kernels using `Vec<T>`, traits or
> const generics are a fsht-03 planning item — the kernel set is
> normative in [KERNELS.md](KERNELS.md) and changes only through it.

Twelve HPC kernels, each implemented four times — **Freshet**,
**idiomatic C++** (the clean first-draft version), **hand-tuned C++**
(the expert version: manual layout, `__restrict__`, unrolling,
threads where the kernel policy says so), and **safe Rust** (std-only,
zero `unsafe`, zero crates). The suite exists to answer one question
honestly: *how close does Freshet's compiled code get to the best
version a C++ expert and a safe-Rust programmer write for the same
kernel?*

## Layout

```
benchmarks/
  KERNELS.md    the normative kernel specification (single source of truth)
  bench.py      the driver: builds, checksum-gates, times, tabulates
  annotate.py   the loss-annotation tool (LLVM IR + disassembly + perf)
  kernels/<name>/
    freshet.fsht    idiomatic.cpp    tuned.cpp    safe.rs    kernel.json
```

## Methodology

* **Correctness gate before timing.** Every implementation prints
  exactly `TIME <ns>` and `CS <decimal>`; all built implementations of
  a kernel must produce the identical `CS` string or the kernel FAILs
  and is excluded from the verdict. Checksum arithmetic is deliberately
  exact-dyadic (or per-operation-order-identical for the non-dyadic
  kernels) so the gate is bit-precise, not tolerant.
* **Hot-region timing.** Programs measure the hot region with a
  monotonic clock themselves; `bench.py` takes the best of N
  repetitions (default 5) of the reported `TIME`. Process startup is
  excluded from the measurement.
* **The timed region includes O(N) setup** — identically in every
  language (documented in KERNELS.md §2). This keeps programs dead
  simple and the comparison fair.
* **No fast-math.** C++ is compiled `-O2 -std=c++17 -ffp-contract=off`;
  Rust with `-C opt-level=3`; Freshet with its default (strict) FP
  contract. FP expressions follow KERNELS.md's exact order everywhere —
  that is what makes four independent implementations bit-identical.
* **Parallelism policy per kernel**: only `sumreduce` compares parallel
  implementations (Freshet `@reproducible parfor`, tuned C++
  `std::thread` with ascending-chunk combine, Rust scoped threads);
  `soa_sweep` gives Freshet its native `parfor` while C++/Rust stay
  serial (the layout story); everything else is serial everywhere so
  the annotation compares codegen, not thread counts.
* Runtime notes: `statemachine` needs ~800 MB in its Rust shape (~288
  MB in the C++/Freshet shapes); the full run takes ~2–4 minutes per
  implementation set on a desktop-class machine.

## Running

```sh
benchmarks/bench.py --penstock /path/to/penstock     # results.json + results.md
benchmarks/bench.py --kernels dot,matmul --reps 9    # subset, more reps
benchmarks/annotate.py --results results.json        # annotate the losses
```

Toolchains are discovered from flags / `PENSTOCK`, `CXX`, `RUSTC`
environment variables / `PATH` / a sibling Penstock checkout. Missing
toolchains skip that language with a note; checksum disagreements and
crashes fail the run.

## Loss annotation (`annotate.py`)

For every kernel where another language beat Freshet beyond the
threshold (default 1.05×), `annotate.py` produces
`reports/losses/<kernel>-vs-<lang>.md` containing:

* the **final optimised LLVM IR** of `hot` from both implementations
  (`penstock --emit-final-ir` / `clang++ -S -emit-llvm` /
  `rustc --emit=llvm-ir`);
* **source-annotated disassembly** of both hot functions;
* a **measured instruction census** (vector FP, scalar FP, integer SIMD,
  div, mul, calls, branches, ...) computed from the disassembly, and
  derived observations in numbers ("the rival emits 14 vector-FP
  instructions while Freshet emits none — vectorisation missed");
* **perf cycle attribution** for both binaries when `perf` and hardware
  counters are available — this is the mode the self-hosted
  `perf`-capable runner uses; hosted runners get the static sections
  and a clear note that cycle data is absent, never fabricated.

The index lands in `reports/INDEX.md`. The design rule throughout:
**measured data is labelled measured, static estimates labelled static.**

## Adding a kernel

1. Append the kernel spec to `KERNELS.md` (sizes, init, hot loop,
   checksum formula, parallel policy, what it stresses).
2. Write the four implementations, all checksum-identical.
3. Add `kernel.json` (mirror an existing one).
4. Verify: `bench.py --kernels <new>` — every built pair must agree on
   `CS`, and the C++ pair should be cross-checked against an
   independent arithmetic model at reduced size.
