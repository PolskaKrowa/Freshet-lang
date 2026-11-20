# 19 — Toolchain & targets (normative in fsht-01:01)

## Compiler surface

```
penstock [options] input.fsht [more.fsht ...]
  -o <file>   -S (emit .ll)  -c (emit .o)  -O<0-4>  -march=<t>
  --run  --report  --profile  --use-profile=<f>  --keep-ir
  --threads=<n>  --soa=warn|auto|aosoa  -I<dir>  --no-loop-opts
  --emit-final-ir[=<f>]  --save-temps  --opt-remarks[=cat]
  --target=<triple>  -g / --debug  --checked / --no-bounds-check
  --strict-performance  --fast-math  --explain <ID>
```

* `-S` emits textual LLVM IR; `--emit-final-ir` writes the final
  **optimised** IR (`<out>.final.ll`); `--save-temps` keeps every
  intermediate (pp, .ll, opt-remarks YAML).
* Subcommands: `penstock build/test/fmt/lint/run`; `penstock fmt` is
  token-identical gated (it can never change what a program means);
  `penstock lint` is front-end only; `penstock test` runs zero-arg void
  `@test fn`s through a generated harness with per-test isolation.

## Backend matrix (fsht-01:01-10.01.01)

Freshet's reference compiler emits textual LLVM IR and drives Clang; it
builds and generates code for **LLVM 19 through 23**. Selection order:
`$LLVM_ROOT`, then shipped `tools/llvmNN` prefixes newest first, then
system `/usr/lib/llvm-NN` (23→19); `-DLLVM_ROOT=` pins it. The generated
IR uses the opaque-pointer dialect. The runtime IR is cached per LLVM
major AND runtime optimisation level, so a runtime produced by one
toolchain is never reused after a switch.

**`--target=<triple>`** cross-targets the whole pipeline (triple + data
layout). fsht-01:01's target story was honest about its limitation: the
runtime's own IR compilation did not receive the triple, the runtime
relied on POSIX/pthreads, and the final link requested `-lpthread`
unconditionally. The fsht-03:03 update resolved all three
([chapter 25](25-portable-runtime.md), registry
`fsht-03:03-10.03.02`): the runtime is decomposed into
`common/` + `platforms/{linux,windows,wasm,baremetal}`, compiled for
the requested target, with platform-conditional links — ratifying the
target set Linux x86-64, Linux AArch64, Windows x86-64, WebAssembly
WASI and standalone browser wasm, each declared only with green
per-target runtime tests.

## Runtime environment

| variable | effect |
|---|---|
| `FRT_THREADS` | worker-pool size (default all cores) |
| `FRT_AFFINITY=1` | pin workers to distinct cores (best effort) |
| `FRT_CHUNK` | default parfor chunk |
| `FRT_SERIAL_CUTOFF` | run small parfor regions inline (default 256) |
| `FRT_TIMING=1` | write `<exe>.frtiming` |
| `FRT_PROF_OUT` | PGO profile path |
| `FRT_SMT_INTERLEAVE=1` | SMT memory/compute lane pairing |
| `FRT_DSTK_RESERVE` | data-stack reservation (default 1 GiB, guard page) |

## Observability

* `--report` merges [static]/[backend]/[runtime] layers: layout tables,
  vectorisation annotation vs actual results (parsed from
  `--opt-remarks` records — an annotation is a request, not proof),
  runtime timing.
* `--opt-remarks`, `--emit-final-ir`, `--save-temps` expose exactly what
  the backend did.
* `-g`/`--debug` emits DWARF: line tables + per-function symbols;
  `gdb`/`addr2line` resolve Freshet source lines.
* LSP: `freshet-language-server` speaks LSP 3.18 over stdio — hover,
  documentSymbol, goto-definition, find-references, rename. Completions
  and inlay hints are future work.

## Compiler capabilities (SHOULD-level, reference-implementation specific)

Superoptimisation (`-O3`/`-O4`: embedded Freshet/Z3/Alive2 loop with
verified candidate acceptance), PGO (`--profile`/`--use-profile`),
finite-domain precomputation, source-level loop transforms (fusion,
unrolling, cross-lane specialisation, mem & vectorisation stage,
Goose-ported BCE/data-stacks/sum-reduction/basecase with `--proof-log`
premises), the opt plugin and the Lean proof kernel are documented
capabilities of Penstock — informative for the standard, exercised by
the benchmark suite's annotation reports. Their guarantees never change
program output (configuration equivalence, chapter 00).

## Conformance requirements

MUST-level: the `-O`/`-S`/`-o`/`--run` surface, checked/unchecked build
switches, `--explain`, and configuration equivalence across optimisation
levels. Everything else in this chapter is the reference
implementation's surface and SHOULD-level for independent compilers.
