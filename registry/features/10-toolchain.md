# 10 — toolchain & target features (fsht-03:03)

### fsht-01:01-10.01.01 — the LLVM backend matrix

Status: normative (reference implementation). Spec: [ch. 19](../../spec/19-toolchain.md)

Builds and generates code for LLVM 19–23; selection order
(`$LLVM_ROOT` → shipped `tools/llvmNN` → system `/usr/lib/llvm-NN`,
newest first); configure-time smoke test; runtime IR cached per LLVM
major and optimisation level; opaque-pointer IR dialect.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — user attribute groups moved to `#50+` after
  machine-generated runtime groups (`#0`–`#9`) silently overrode them
  by textual concatenation (dropping `noinline`, losing `@strictfp`,
  turning every `export fn` cold-noreturn); the split makes attributes
  take effect exactly as emitted on all supported versions.

### fsht-01:01-10.02.01 — the Freshet runtime

Status: normative (runtime surface). Spec: [ch. 19](../../spec/19-toolchain.md)

libfreshet (frt_rt): memory, SoA planes, the work-stealing worker pool,
parfor dispatch, PGO counters, timing; environment variables
`FRT_THREADS`, `FRT_AFFINITY`, `FRT_CHUNK`, `FRT_SERIAL_CUTOFF`,
`FRT_TIMING`, `FRT_PROF_OUT`, `FRT_SMT_INTERLEAVE`, `FRT_DSTK_RESERVE`.
The C API (libfsh, `include/fsh/*.h`) embeds it.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-10.03.01 — `--target=<triple>` cross-targeting

Status: normative (flag surface); known limitation. Spec: [ch. 19](../../spec/19-toolchain.md)

The flag exists and cross-targets triple + data layout. Known issue:
the runtime LLVM IR compilation does not receive the requested triple;
the runtime relies on POSIX/pthreads; the final link requests
`-lpthread` unconditionally.

History:
- fsht-01:01 — first standardised, with the limitation recorded above.
- fsht-03:03 (planned) — target-aware runtime architecture
  (fsht-03:03-10.03.02) resolves this entry's limitation; this entry
  will carry the update reference.
- fsht-03:03 (ratified 2026-11-19) — the limitation is resolved: the
  `--target` triple now reaches the runtime's own compilation (same-
  target runtime, triple in the runtime cache key), the runtime
  decomposes into `common/` + `platforms/{linux,windows,wasm,
  baremetal}` with POSIX/pthreads confined to the linux layer, and
  the link line requests `-lpthread` only for linux targets. See
  [ch. 25](../../spec/25-portable-runtime.md) and 10.03.02 below.

### fsht-03:03-10.03.02 — portable, target-aware runtime

Status: normative (fsht-03:03). Spec:
[spec/25-portable-runtime.md](../../spec/25-portable-runtime.md).
Reference implementation: Penstock 0.1.0-INDEV (conformance: the
target-matrix workflow `.github/workflows/targets.yml` — the portable
corpus and a runtime smoke per ratified target; corpus
`tests/corpus/22_portable_program.fsht` is the pinned portable
exhibit with one golden output on all five targets).

```
runtime/
    common/     memory, math, diagnostics
    platforms/  linux/ windows/ wasm/ baremetal/
```

The runtime must be compiled for the same target as the application.
Target set: Linux x86-64, Linux AArch64, Windows x86-64, WebAssembly
WASI, WebAssembly standalone/browser. Every target configuration MUST
have suitable runtime tests before support is declared.

**Ratified surface (fsht-03:03):** the decomposition above is
normative (target-independent core + named platform layers);
same-target runtime compilation including the triple in the runtime
cache key; platform-conditional links; the target matrix with its
`parfor` semantics (full worker pool on linux/windows, serialised on
wasm — `@reproducible` output unchanged by construction); the `FRT_*`
portable-acquisition rules (unset/unparsable → documented default,
silently, on every target; embedder globals on standalone wasm;
compile-time defaults on baremetal; `FRT_TIMING`/`FRT_PROF_OUT` no-op
where no filesystem exists); the portable-program contract; and the
tested-before-declared gate — a target without a green runtime-test
row is not supported whatever the compiler accepts. Ratification
recorded the matrix green: Linux x86-64 (native runner), Linux AArch64
(native runner), Windows x86-64 (windows runner), WASI (wasmtime),
standalone wasm (d8/node embedding).

History:
- fsht-03:03 (accepted) — first accepted with the tested-before-declared
  requirement.
- fsht-03:03 (ratified 2026-11-19) — chapter 25 normative; the
  fsht-01:01-10.03.01 limitation is closed (update reference above).
  Shared-memory wasm threads, ratified baremetal targets, dynamic
  wasm library targets and per-target vectorisation cost models are
  deferrals (ch. 25 §7).

### fsht-01:01-10.04.01 — tooling

Status: normative (reference implementation). Spec: [ch. 19](../../spec/19-toolchain.md)

`penstock test` (isolated @test harness), `penstock fmt`
(token-identical safety gate), `penstock lint`, `-g` DWARF debug info,
`freshet-language-server` (LSP 3.18: hover, documentSymbol,
goto-definition, find-references, rename); editor support (VS Code,
Vim). Completions/inlay hints are future work.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the language server's CMake source list
  missed new front-end files (link failure); a single shared
  FRONTEND_SOURCES list now feeds both executables so a future
  front-end file can never land in one target only.

### fsht-01:01-10.04.02 — observability

Status: normative (reference implementation). Spec: [ch. 19](../../spec/19-toolchain.md)

`--report` (static/backend/runtime layers), `--opt-remarks`,
`--emit-final-ir`, `--save-temps`; the annotation-vs-actual
vectorisation distinction (an annotation is a request, not proof).

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the historical blanket
  `vectorize.enable + interleave.count 4` metadata on every simple loop
  overrode LLVM's profitability choice; hints are now opt-in
  (`@vectorize`, `--force-vectorize` as the differential hatch).
