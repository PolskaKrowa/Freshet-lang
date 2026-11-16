# The Freshet Language Specification — fsht-01:01

This directory is the normative specification of the **Freshet**
programming language, ratified as version `fsht-01:01`. It documents
exactly what the language *is* today — a strictly-typed, strictly-checked
HPC language with C-level control over data layout — not what it may
become: accepted-but-unimplemented work (dynamic containers, user traits,
const generics, the expanded standard library, the portable runtime) lives
in the [feature registry](../registry/) as entries with target versions,
not in these chapters.

## Reading the specification

* Chapters are numbered `00`–`19` and are ordered from lexical structure
  to toolchain requirements; each carries normative grammar (EBNF) inside
  the chapter and prose rules using RFC-2119 keywords.
* **MUST / MUST NOT / SHALL** — a conforming implementation has no choice.
* **SHOULD / SHOULD NOT** — strong default; deviations must be justified
  and documented in the implementation's conformance statement.
* **MAY** — genuinely optional.
* `fsht-01:01-aa.bb.cc` references (e.g. `fsht-01:01-04.02.01`) point at
  the registry entry that tracks the feature; see
  [versions.md](../versions.md) for the numbering scheme.

## Conformance

A **conforming Freshet compiler** for fsht-01:01:

1. accepts every program the grammar and semantic rules of these chapters
   define, with the observable behaviour the chapters specify;
2. rejects programs that violate a MUST-level rule, ideally with the
   diagnostic registry of [chapter 15](15-diagnostics.md) (the IDs
   themselves are normative for Penstock, the reference implementation);
3. produces configuration-equivalent output: optimisation passes,
   thread counts (outside documented `@reproducible` guarantees) and
   diagnostic severities do not change program output;
4. passes the [stress & conformance suite](../tests/).

The reference implementation of fsht-01:01 is **Penstock 0.1.0-INDEV**
(LLVM 19–23 backend). Where a chapter notes an implementation caveat
(e.g. `String` allocations are not yet ownership-tracked), that caveat is
part of the standard's honest surface, and the corresponding registry
entry carries an update target.

## Chapter index

| # | Chapter | Covers |
|---|---|---|
| 00 | [Introduction](00-introduction.md) | goals, layer architecture, terminology |
| 01 | [Lexical structure](01-lexical.md) | tokens, literals, preprocessor |
| 02 | [Types](02-types.md) | scalars, pointers, aggregates, representation |
| 03 | [Declarations](03-declarations.md) | bindings, functions, attributes, entry point |
| 04 | [Structs](04-structs.md) | C layout, alignment, value semantics |
| 05 | [Statements](05-statements.md) | control flow, loops, `defer`, `match` |
| 06 | [Memory & ownership](06-memory-ownership.md) | malloc/free/give, modes, `unsafe`, data stacks |
| 07 | [Arrays, spans & SoA](07-arrays-spans-soa.md) | `[T; N]`, `Span<T>`, `soa(S)` |
| 08 | [Enums & tagged unions](08-enums.md) | variants, construction, exhaustiveness |
| 09 | [Generics](09-generics.md) | monomorphisation, constraints, inference |
| 10 | [Strings](10-strings.md) | `str` views, `String`, formatting |
| 11 | [Option & Result](11-option-result.md) | prelude enums, `?` propagation |
| 12 | [Parallelism: parfor](12-parfor.md) | worker pool, reductions, `@reproducible` |
| 13 | [Floating-point contract](13-floating-point.md) | strict default, `@fastmath`, `@strictfp` |
| 14 | [Numeric semantics](14-numeric-semantics.md) | wrapping, division, shifts, operator families |
| 15 | [Diagnostics](15-diagnostics.md) | the `Fnnnn` registry, severities, strict mode |
| 16 | [Modules](16-modules.md) | `module`/`import`/`pub`, project manifest |
| 17 | [FFI & function pointers](17-ffi.md) | `extern fn`, callbacks, C ABI |
| 18 | [The `fsh` module](18-stdlib.md) | argv, environment, file I/O, test helpers |
| 19 | [Toolchain & targets](19-toolchain.md) | LLVM matrix, runtime, environment variables |
| — | [Grammar (consolidated EBNF)](grammar.md) | single-page grammar appendix |

## Draft chapters (fsht-02:01 in development)

Chapters beyond 19 are **drafts for fsht-02:01** — they document the
first cut shipped in the reference compiler but are NOT normative until
fsht-02:01 ratifies. They are listed here so the draft is discoverable;
the ratified fsht-01:01 surface is exactly chapters 00–19 above.

| # | Chapter | Covers |
|---|---|---|
| 20 | [Dynamic collections (DRAFT)](20-dynamic-collections.md) | `Vec<T>`, moves/drop, views |
