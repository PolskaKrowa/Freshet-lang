# 00 — Introduction (normative in fsht-01:01)

## What Freshet is

Freshet is a strictly-typed, strictly-checked high-performance language.
Its surface syntax is C++/Rust-like; its data-layout control is C-level;
and its compilers treat *predictable* performance bugs as compile-time
diagnostics rather than folklore. Source files use the `.fsht` extension.

The reference compiler, **Penstock**, lowers Freshet to textual LLVM IR
and drives a Clang backend; this specification is written so that any
conforming compiler may implement the language independently.

## The layer architecture

The standard assumes — and requires — a strict separation between the
language and the scientific software built on it:

```
Layer 3 - Applications
    physics, engineering, simulation, data processing, WebAssembly, ...
        |
        v
Layer 2 - Scientific standard library (layer 2 is NOT part of this standard)
    linear algebra, numerics, statistics, physics primitives, datasets
        |
        v
Layer 1 - Freshet language and runtime  <-- THIS DOCUMENT (fsht-03:03)
    types, generics, ownership, collections, memory, parallelism, I/O
        |
        v
Compilers (Penstock is the reference)
    LLVM, optimisation, superoptimisation, diagnostics, code generation
```

A conforming implementation MUST keep Layer 1 independent of any
scientific library: it MUST be possible to write a plain command-line
program without importing a physics framework, and conversely a numerical
library MUST be expressible without compiler changes. As of fsht-03:01
the shipped library is the decomposed module set of chapter 23
(`core/alloc/collections/string/math/io/numeric/time/bits/random`, the
`fsh` façade kept); everything beyond it is out of scope of this
standard.

## Design principles

1. **Correctness diagnostics are always errors; performance diagnostics
   are warnings by default** (and hard errors under a strict switch).
   "Your program is incorrect" and "your program may be slow" are
   different messages (chapter 15).
2. **Layout is the programmer's** — C struct layout, `align(N)` control,
   AoS/SoA choice, fixed-size arrays and borrowed spans; the compiler
   advises (`F0408`) but never silently reshapes memory, except under an
   explicit, provably-safe automatic transformation.
3. **Floating-point is strict IEEE-754 per operation by default**;
   fast-math is an explicit, greppable opt-in per function or build
   (chapter 13).
4. **Parallelism is data-parallel `parfor` with deterministic
   reductions**; race-prone shapes are rejected at compile time, and
   `@reproducible` buys bitwise thread-count independence (chapter 12).
5. **The escape hatch is explicit.** `unsafe { }` scopes and `@unsafe fn`
   are greppable; the safe path is the default (chapter 6).

## Terminology

* **Observable behaviour**: the program's exit code and complete stdout,
  plus traps (runtime aborts) the standard mandates. Optimisation passes
  of a conforming compiler MUST NOT change observable behaviour
  (configuration equivalence).
* **Checked build**: a build in which span/array indexing bounds are
  verified at runtime (`-O0`/`-O1`, or an explicit switch); a conforming
  compiler MUST provide both checked and unchecked builds.
* **Trap**: a deterministic runtime abort (e.g. out-of-bounds access in a
  checked build, or division by zero). The conditions that trap are part
  of the semantics (chapter 14).

## Status keywords

Chapters use RFC-2119 keywords. The grammar is normative in-chapter; the
consolidated appendix ([grammar.md](grammar.md)) is informative — in case
of conflict, the per-chapter productions and the prose rules win.
