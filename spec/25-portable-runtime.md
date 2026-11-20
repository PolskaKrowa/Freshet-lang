# 25 — The portable, target-aware runtime (normative in fsht-03:03)

> **Status.** Normative since fsht-03:03 (ratified 2026-11-19; first cut
> implemented in Penstock 0.1.0-INDEV). Registry entry:
> [fsht-03:03-10.03.02](../registry/features/10-toolchain.md) — with the
> tested-before-declared requirement it carried from acceptance. This
> chapter resolves the recorded limitation of fsht-01:01-10.03.01 (the
> `--target` triple reached the program pipeline but not the runtime;
> the runtime assumed POSIX/pthreads; `-lpthread` was linked
> unconditionally) — that entry carries the update reference in its
> history. Everything listed in §7 is a registry-tracked deferral, not
> a silent omission.

## 1. Runtime decomposition (fsht-03:03-10.03.02)

The runtime is architecture, not folklore. A conforming implementation
MUST split its runtime into a target-independent core and per-platform
layers:

```
runtime/
    common/     memory, math, diagnostics
    platforms/  linux/ windows/ wasm/ baremetal/
```

* `common/` carries everything with no target surface: the allocator
  core, the `Vec`/`String` container operations, SoA plane helpers,
  the reduction shaping entry points, the diagnostic printing policy
  and the `FRT_*` parsing logic (§4). It MUST compile for every
  ratified target unchanged.
* `platforms/` implements exactly the surface `common/` calls: thread
  creation and joining, work-stealing worker pool primitives, mutex
  equivalents, monotonic time, file and stream primitives, and the
  program argument/environment accessors. `linux/` uses
  pthreads/POSIX; `windows/` uses the Windows thread/file API; `wasm/`
  implements the WASI and standalone/browser shims; `baremetal/` is the
  freestanding fallback (§2).
* **Same-target compilation (MUST):** the runtime object code linked
  into a program MUST have been compiled for the program's exact
  target. The reference implementation compiles `runtime/` with the
  requested `--target` triple and data layout — the fsht-01:01 gap
  (the runtime IR never received the triple) is closed — and the
  runtime cache key includes the target (chapter 19's per-LLVM-major
  caching gains the triple).
* Link lines are platform-conditional: `-lpthread` is requested by the
  linux platform layer only; no unconditional POSIX assumption exists
  anywhere in `common/`.

## 2. The target matrix

| target | runtime layer | parallelism surface |
|---|---|---|
| Linux x86-64 | `platforms/linux` | full worker pool (pthreads, work stealing, affinity) |
| Linux AArch64 | `platforms/linux` | full worker pool |
| Windows x86-64 | `platforms/windows` | full worker pool (Windows threads; `FRT_AFFINITY` best effort) |
| WebAssembly WASI (`wasm32-wasi`) | `platforms/wasm` | single-threaded: pool of one, `@reproducible` trivially holds |
| WebAssembly standalone/browser (`wasm32-unknown-unknown`) | `platforms/wasm` | single-threaded; time from the embedder import, else monotonic counter |

* **32-bit wasm.** wasm32 is a ratified target precisely because the
  `usize` model is settled: `usize` stays 64-bit (chapter 24 §6), so
  indices and lengths behave identically to every other target; the
  32-bit address space affects pointers only, which the language never
  lets programs observe beyond `sizeof` of pointer-holding shapes
  (documented per-target in the implementation's conformance
  statement).
* **`parfor` on single-threaded targets** serialises: the language
  semantics (chapter 12) hold — reductions still compute, and
  `@reproducible` output is unchanged by construction.
* `stack_alloc` data stacks and their guard pages are `linux` /
  `windows` facilities; on wasm the data-stack reservation is plain
  linear memory and `FRT_DSTK_RESERVE` is accepted and clamped
  (SHOULD-level).

## 3. Tested before declared

**Every target configuration MUST have suitable runtime tests before
support is declared** (the acceptance requirement, now normative). The
reference implementation's gate is the target-matrix workflow
(`.github/workflows/targets.yml` in the standards repository): each
ratified target runs the portable corpus and a runtime smoke (worker
pool under `FRT_THREADS` variation, container drop accounting, stream
round-trip) on that target's execution environment. A target whose row
is not green is not supported, whatever the compiler accepts — and
declaring it anyway is a conformance defect against this chapter. The
fsht-03:03 ratification recorded the matrix green: Linux x86-64 (native
runner), Linux AArch64 (native runner), Windows x86-64 (windows
runner), WASI (wasmtime) and standalone wasm (d8/node embedding).

## 4. The `FRT_*` environment, portably

The knobs of chapter 19 keep their names and meanings; their
*acquisition* is platform-layer work:

* Unset or unparsable values fall back to the documented default
  silently on every target — a knob must never abort a program.
* Linux/Windows read the process environment; WASI reads it through
  the WASI args/environ surface; standalone wasm receives knobs
  through the embedder-provided globals module (`frt_config`) and
  defaults otherwise; baremetal uses compile-time defaults only.
* `FRT_TIMING`/`FRT_PROF_OUT` write files where the platform has a
  filesystem and become no-ops (parsed, ignored, timing omitted)
  where it does not — wasm standalone included. Timing output is never
  part of observable program behaviour (chapter 00).

## 5. The portable program contract

A program is portable across the §2 matrix when it: uses no `extern fn`
beyond the C ABI of the target it names; performs file I/O only
through chapters 18/23 surfaces (or none); relies on `usize` being
64-bit (always true) and on no address-size assumption; and does not
read `freshet.threads`/`freshet.cycles` into program output. Every
`corpus/` program in the conformance suite is portable by construction;
`tests/corpus/22_portable_program.fsht` is the pinned exhibit, run by
the target matrix on all five targets with one golden output.

## 6. Conformance requirements

The decomposition (a target-independent core plus the named platform
layers), same-target runtime compilation (including the triple in the
runtime cache key), the platform-conditional link surface, the §2
matrix semantics (serialised `parfor`, unchanged `@reproducible`
output), the silent-default `FRT_*` rule and the tested-before-declared
gate are MUST-level. Which targets an implementation *declares* is
implementer choice — a one-target implementation conforms by declaring
exactly that target with its green row; it MUST reject `--target`
values it cannot build with a diagnostic naming the unsupported triple
(`F0008` is the internal-error family; an unsupported-triple message is
a driver diagnostic, ID allocation per chapter 15).

## 7. Deferrals (registry-tracked)

* Shared-memory wasm threads (`wasm32` + threads proposal) — the
  multi-threaded wasm pool.
* `baremetal` beyond the freestanding fallback: no ratified
  baremetal *target*, only the layer's existence contract.
* Dynamic library targets on wasm (relocatable modules).
* Per-target `@vectorize` cost models beyond the LLVM defaults.
