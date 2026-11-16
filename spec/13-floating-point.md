# 13 — The floating-point contract (normative in fsht-01:01)

## The default is strict

Freshet's default floating-point semantics are **strict, IEEE-754-like
per operation**: no reassociation, no contraction (FMA), NaN and signed
zero preserved. Fast-math is an explicit opt-in for the HPC throughput
workflow. This is a *language-level contract*, not an optimiser hint — it
affects program correctness, not just performance.

```ebnf
fp_mode ::= "strict" (default) | "@strictfp" | "@fastmath" | "--fast-math"
```

| mode | spelling | effect |
|---|---|---|
| strict | (default, no annotation) | every operation matches the IEEE-754 reference for its type; reductions are bit-reproducible |
| strict-FP | `@strictfp` on the fn | the same per-operation semantics plus the strict rounding-environment attribute |
| fast-math | `@fastmath` on the fn, or `--fast-math` build-wide | reassociation, contraction and NaN/signed-zero relaxation are permitted; reduction order may vary run to run |

## Consequential rules

* The mode is **per-function**; one program may mix strict and fast-math
  functions. `@strictfp` always wins over `@fastmath` on the same
  function.
* `sin/cos/tan/log2/log10` call libm under the strict default (their
  errno-visible memory is not hidden behind an intrinsic) and lower to
  LLVM intrinsics (vectorisable) only under fast-math; `--veclib=libmvec`
  replaces them with vector routines.
* FMA contraction happens **only** under fast-math; explicit
  `fma`-style library calls are always available.
* `@reproducible` regions (chapter 12) override fast-math for the
  reduction: strict order, bitwise thread-count independence.

## Conformance requirements

MUST-level: the strict default with no reassociation/contraction, the
per-function opt-in family, `@strictfp` precedence, and configuration
equivalence — a conforming compiler's optimisation passes must not change
FP-observable output between build modes unless the source opted into
`@fastmath`/`--fast-math`. The distinction between measured and
guaranteed behaviour is part of this contract: `@reproducible` is a
guarantee; everything about fast-math is documented relaxation.
