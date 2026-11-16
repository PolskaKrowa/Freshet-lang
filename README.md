# Freshet-lang — the Freshet programming language standard

**Current standard: `fsht-01:01`**

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
Layer 1 - Freshet language and runtime  <-- THIS REPOSITORY (fsht-01:01)
    types, generics, ownership, collections, memory, parallelism, I/O
        |
        v
Compilers (Penstock is the reference)
    LLVM, optimisation, superoptimisation, diagnostics, code generation
```

The language stays independent of the scientific libraries; the
scientific libraries evolve without compiler changes (spec ch. 00).

> **fsht-02:01 work has started** (2026-11-16): the first cut of
> [fsht-02:01-02.09.01](registry/features/02-data-types.md) (dynamic
> collections — `Vec<T>`) and
> [fsht-02:01-02.09.02](registry/features/02-data-types.md) (container
> move semantics: drop on scope exit, move-out invalidation) is
> implemented in the reference compiler and tracked as `in development`
> in the registry, with the draft spec chapter
> [spec/20-dynamic-collections.md](spec/20-dynamic-collections.md) and
> conformance tests (`tests/corpus/13`, `tests/negative/n18–n22`).
> Traits (fsht-02:02) and const generics (fsht-02:03) remain accepted
> targets.

## Repository map

| directory | contents |
|---|---|
| [`spec/`](spec/README.md) | the fsht-01:01 normative specification — 20 chapters, per-chapter EBNF, consolidated grammar appendix |
| [`registry/`](registry/README.md) | the feature registry: permanent `fsht-xx:yy-aa.bb.cc` identifiers, statuses, histories and update references; the fsht-02/03 roadmap lives here |
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
  ratified snapshot.
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
