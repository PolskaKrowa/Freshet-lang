<div align=center>
  <img width="730" height="411" alt="freshet logo" src="https://github.com/user-attachments/assets/930e9c07-4517-476c-a494-bd82b2694e46" />
</div>

# Freshet-lang — the Freshet programming language standard

**Current standard: `fsht-03:03`** · Reference implementation:
[Penstock](https://github.com/PolskaKrowa/Penstock) `0.1.0-INDEV`

This repository is the home of the **Freshet language standard**: the
normative specification developers can read, the feature registry that
tracks every feature's identity and history across versions, and the
stress & benchmark suites that keep Freshet compilers honest against
idiomatic C++, hand-tuned C++ and safe Rust.

```
Layer 3 - Applications
    physics, engineering, simulation, data processing, WebAssembly, ...
        |
        v
Layer 2 - Scientific standard library (NOT this repository)
    linear algebra, numerics, statistics, physics primitives, datasets
        |
        v
Layer 1 - Freshet language and runtime  <-- THIS REPOSITORY (fsht-03:03)
    types, generics, ownership, collections, memory, parallelism, I/O
        |
        v
Compilers (Penstock is the reference)
    LLVM, optimisation, superoptimisation, diagnostics, code generation
```

The language stays independent of the scientific libraries; the
scientific libraries evolve without compiler changes (spec ch. 00).

> **fsht-03 ratified** (2026-11-19): the three increments of the fsht-03
> milestone are now normative —
> [fsht-03:01](registry/features/05-io.md) (the expanded standard
> library: `parse_i64/u64/f64` over `Result`, streaming `Reader`/
> `Writer` with `IoError`, the module decomposition `core / alloc /
> collections / string / math / io / numeric / time / bits / random`,
> checked/saturating/wrapping variants and `checked_cast`/
> `saturating_cast` — registry 05.04.01/05.05.01/05.06.01/08.01.04),
> [fsht-03:02](registry/features/03-memory.md) (mutable borrows with
> exclusivity `F0310`, the lifetime/escape refinement `F0311`, the
> ownership-tracked `String` migration, drop elaboration through user
> shapes, `usize` resolved fixed 64-bit — registry 03.02.09/03.02.10)
> and [fsht-03:03](registry/features/10-toolchain.md) (the portable,
> target-aware runtime: `runtime/common + platforms/{linux,windows,
> wasm,baremetal}`, the five-target matrix, tested-before-declared —
> registry 10.03.02, closing the fsht-01:01 `--target` limitation).
> Spec chapters [23](spec/23-stdlib-expansion.md)–[25](spec/25-portable-runtime.md)
> are normative; the consolidated grammar, the registry histories and the
> suite (corpus 20/21/22, negatives n26–n31, props p08–p09, fuzz
> blocks, the targets.yml matrix) grew with them. Every fsht-03
> increment preserves defined behaviour; the newly diagnosed shapes
> were already undefined (dangling views, use-after-free Strings).

## Repository map

| directory | contents |
|---|---|
| [`spec/`](spec/README.md) | the fsht-03:03 normative specification — 26 chapters (00–25), per-chapter EBNF, consolidated grammar appendix |
| [`registry/`](registry/README.md) | the feature registry: permanent `fsht-xx:yy-aa.bb.cc` identifiers, statuses, histories and update references; the fsht-04 roadmap and fsht-03:04 proposals live here |
| [`versions.md`](versions.md) | the versioning scheme: `fsht-xx:yy` versions, feature IDs, the update-reference rule (with a worked example) |
| [`tests/`](tests/README.md) | the stress & conformance suite: curated corpus with goldens, negative tests, property checks, differential fuzz |
| [`benchmarks/`](benchmarks/README.md) | 12 HPC kernels × 4 implementations (Freshet, idiomatic C++, hand-tuned C++, safe Rust) + the benchmark driver and the loss-annotation tool |

## Quick start

```sh
# conformance + stress against your Freshet compiler
FSHC=/path/to/penstock tests/run_suite.sh

# benchmarks (Freshet vs C++ vs Rust), checksum-gated
benchmarks/bench.py --penstock /path/to/penstock

# annotate every kernel where another language beat Freshet:
# final LLVM IR + source-annotated disassembly of BOTH implementations,
# measured instruction census, and perf cycle attribution when available
benchmarks/annotate.py --results results.json
```

The loss annotation is what makes this repository a compiler tool, not
just a scoreboard: for every losing kernel it puts Freshet's generated
code next to the rival's and says, in measured instruction counts, why.

## The standard's numbering (short form)

* Versions: `fsht-xx:yy` (major.minor). `fsht-01:01` is the first
  ratified snapshot; the current standard is `fsht-03:03`
  (fsht-02:01–03: dynamic collections, traits, const generics;
  fsht-03:01–03: the expanded library, mutable borrows & lifetimes,
  the portable runtime — all ratified 2026-11-19).
* Features: `fsht-xx:yy-aa.bb.cc` — the version that first shipped the
  feature, then major subset, minor subset, exact feature.
* **A feature that changed in a later version must carry a reference for
  every version in which it changed.** See
  [`versions.md`](versions.md) for the full rules and a worked example.

## Contributing

Developers are meant to view, add to and modify this standard —
[CONTRIBUTING.md](CONTRIBUTING.md) describes the feature lifecycle
(proposed → accepted with target version → normative → updated with
history references), the grammar conventions, and the rule that every
new feature lands with its registry entry, its spec text and its suite
coverage in the same change.

## Licence

The specification prose is licensed
[CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/); the code
(tests, benchmarks, harnesses, workflows) is licensed
[Apache-2.0](LICENSE-APACHE-2.0.txt). See [LICENSE.md](LICENSE.md).
