# 10 — toolchain & target features (fsht-01:01)

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

### fsht-03:03-10.03.02 — portable, target-aware runtime

Status: accepted (target fsht-03:03). Spec: —

```
runtime/
    common/     memory, math, diagnostics
    platforms/  linux/ windows/ wasm/ baremetal/
```

The runtime must be compiled for the same target as the application.
Target set: Linux x86-64, Linux AArch64, Windows x86-64, WebAssembly
WASI, WebAssembly standalone/browser. Every target configuration MUST
have suitable runtime tests before support is declared.

History:
- fsht-03:03 (accepted) — first accepted with the tested-before-declared
  requirement.

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
