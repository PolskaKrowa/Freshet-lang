# 15 — Diagnostics (normative in fsht-01:01)

## Correctness vs performance (fsht-01:01-09.01.01)

Correctness diagnostics are always **errors**. Performance diagnostics
are **warnings by default** — a slow-but-correct program compiles; "your
program is incorrect" and "your program may be slow" are different
messages. `--strict-performance` (or `@hpc_strict` per function) raises
the performance family to hard errors for the HPC workflow.

| diagnostic | default | strict mode |
|---|---|---|
| type, cast, arity, mutability errors (`F0201`,`F0202`,`F0208`) | error | error |
| ownership: leak / UAF / double free / bad give (`F0301`) | error | error |
| `F0212`, `F0204`, `F0209`, `F0203`, `F0303` | error | error |
| division by the literal zero (`F0214`) | error | error |
| int div by non-power-of-2 const (`F0401`) / runtime value (`F0402`) | warning | error |
| strided access burning whole cache lines (`F0403`) | warning | error (sub-cache-line strides stay warnings) |
| hot field straddling a cache line (`F0404`) | warning | error |
| non-unit loop stride (`F0405`) / IV written in body (`F0406`) | warning | error |
| AoS→SoA advice, layout padding, narrowing casts (`F0408`,`F0407`,`F0211`) | warning | warning |

## The `Fnnnn` registry (fsht-01:01-09.02.01)

Every diagnostic has a stable ID of the form `Fnnnn`, printed as
`error[F0402]` / `warning[F0402]`. The ID names the *rule*, not its
severity. **IDs are never reused or renumbered; a diagnostic split later
gets new IDs.** The registry is normative for the reference
implementation; other conforming compilers SHOULD map their diagnostics
onto the registry (the stress suite's `negative/` directory asserts
rejection, and additionally the ID when the compiler is Penstock).

**Driver and project**

| ID | name | meaning |
|---|---|---|
| `F0001` | `io` | file could not be read or written |
| `F0002` | `proj` | project manifest error |
| `F0003` | `mod` | module declaration error |
| `F0004` | `import` | import could not be resolved or is not visible |
| `F0005` | `test` | invalid @test function |
| `F0006` | `fmt` | formatter refused to rewrite the file |
| `F0007` | `pgo` | profile data could not be used |
| `F0008` | `ir` | internal error while generating IR |

**Syntax**

| ID | name | meaning |
|---|---|---|
| `F0101` | `lex` | unexpected character |
| `F0102` | `parse` | syntax error |
| `F0103` | `preproc` | preprocessor error |
| `F0104` | `preproc-directive` | unknown preprocessor directive |
| `F0105` | `attr` | unknown or conflicting attribute |
| `F0106` | `parfor` | invalid parfor syntax or clause |

**Semantics**

| ID | name | meaning |
|---|---|---|
| `F0201` | `type` | type error (incl. ptr↔number casts, aggregate `==`, pointer ordering) |
| `F0202` | `args` | wrong arguments to a call or builtin |
| `F0203` | `generic` | generic instantiation error |
| `F0204` | `match` | invalid / non-exhaustive match |
| `F0205` | `dup` | duplicate definition |
| `F0206` | `main` | no entry point |
| `F0207` | `global` | global initializer must be constant |
| `F0208` | `mut` | assignment through an immutable binding |
| `F0209` | `ret` | missing or invalid return |
| `F0210` | `ret-main-implicit` | main returns implicitly |
| `F0211` | `cast-narrowing` | narrowing numeric cast |
| `F0212` | `bound` | constant index out of bounds |
| `F0213` | `loop-break-outside` | break/continue outside a loop |
| `F0214` | `arith-div-zero` | division by zero |
| `F0215` | `arith-neg-unsigned` | negation of an unsigned value |

**Safety (ownership, aliasing, purity, parfor)**

| ID | name | meaning |
|---|---|---|
| `F0301` | `own` | ownership violation (leak/UAF/double free/bad give) |
| `F0302` | `own-suspicious` | suspicious ownership operation |
| `F0303` | `own-call` | argument passing-mode mismatch |
| `F0304` | `pure` | @pure function has side effects |
| `F0305` | `alias-violation` | aliased arguments to noalias parameters |
| `F0306` | `alias-lie` | call breaks an @alias no-overlap promise |
| `F0307` | `thread` | unsafe construct inside a parfor body |
| `F0308` | `red-add-init` | reduction(+) not initialised to 0 |
| `F0309` | `red-mul-init` | reduction(*) not initialised to 1 |

**Performance**

| ID | name | meaning |
|---|---|---|
| `F0401` | `arith-div-const` | division by a non-power-of-2 constant |
| `F0402` | `arith-div-runtime` | division by a runtime value |
| `F0403` | `cache-stride` | strided access wastes cache lines |
| `F0404` | `cache-line-straddle` | hot field straddles a cache line |
| `F0405` | `loop-stride` | for-loop stride is not constant 1 |
| `F0406` | `loop-iv-written` | loop induction variable modified in body |
| `F0407` | `layout-pad` | struct layout wastes bytes on padding |
| `F0408` | `soa` | AoS access would benefit from SoA layout |

**Optimisation remarks (notes)**

| ID | name | meaning |
|---|---|---|
| `F0901` | `lane` | cross-lane optimisation applied |
| `F0902` | `lane-skip` | cross-lane optimisation skipped (cost gate) |
| `F0903` | `soa-auto` | automatic AoS→SoA conversion |
| `F0904` | `soa-aosoa` | AoSoA layout cost report |
| `F0905` | `par-advise` | loop appears safe to parallelise |
| `F0906` | `nested-ws` | nested parfor inner chunks become stealable tasks |
| `F0907` | `collapse` | rectangular nested parfor collapsed |
| `F0908` | `fuse` | adjacent loops fused |
| `F0909` | `unroll` | constant-trip loop fully unrolled |
| `F0910` | `partial-unroll` | loop partially unrolled |
| `F0911` | `peel` | first loop iteration peeled |
| `F0912` | `licm` | loop-invariant binding hoisted |
| `F0913` | `interchange` | loop nest interchanged |
| `F0914` | `tile` | loop nest tiled |
| `F0915` | `distribute` | loop distributed |
| `F0916` | `unroll-jam` | loop nest unrolled and jammed |
| `F0917` | `const-fold` | constants folded at exact source width |
| `F0918`–`F0922` | mem & vectorisation stage | redundant-mov elimination, allocation-churn elimination, separable-routine/SLP batching, vector plan reports, SMT memory/compute interleave |
| `F0923`–`F0929` | Goose-ported passes | bounds-check elimination + `@checkfree`, data-stack model, sum-reduction shaping, base-case inlining |

## `--explain` and long-form pages

`penstock --explain F0402` (or its slug) prints the registry entry and
the long-form page when one exists; the same pages are the canonical
documentation URLs. Call sites reference diagnostics by registry *name*
so a misspelt diagnostic does not compile.

## Conformance requirements

The ID registry, the never-reuse/never-renumber rule and the severity
policy table are MUST-level for the reference implementation and
SHOULD-level for independent implementations. Several IDs still cover a
family of related failures (`F0201`, `F0301`); splits create new IDs —
that process is itself the rule.
