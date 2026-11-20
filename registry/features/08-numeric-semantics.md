# 08 — numeric-semantics features (fsht-03:03)

### fsht-01:01-08.01.01 — integer wrapping arithmetic

Status: normative. Spec: [ch. 14](../../spec/14-numeric-semantics.md)

`add`/`sub`/`mul` are two's-complement modular arithmetic on signed and
unsigned operands — wrapping is the specified behaviour, never
undefined behaviour.

History:
- fsht-01:01 — first standardised (codified from the audit: no
  `nsw`/`nuw` semantics assumed, deliberately).
- fsht-01:01 (correction) — mixed-width arithmetic used to leave the
  lhs register at its narrow width (malformed IR); both operands now
  promote to the common type first, and mixed-width comparisons pick
  the predicate from the correct type.

### fsht-01:01-08.01.02 — division and remainder

Status: normative. Spec: [ch. 14](../../spec/14-numeric-semantics.md)

Signed division truncates toward zero; the remainder takes the
dividend's sign (`-7 / 2 == -3`, `-7 % 8 == -7`); div-by-zero and
`INT_MIN / -1` trap; the literal `0` divisor is compile-time `F0214`.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the signed power-of-two strength reduction
  miscompiled negative dividends; the rounding-correction sequence now
  preserves exactly these semantics, verified across i8/i16/i32/i64.

### fsht-01:01-08.01.03 — shifts

Status: normative. Spec: [ch. 14](../../spec/14-numeric-semantics.md)

`<<` logical; `>>` arithmetic for signed, logical for unsigned;
out-of-range shift counts are avoided, not defined.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-08.01.04 — checked / saturating / wrapping operator variants

Status: normative (fsht-03:01). Spec:
[spec/23-stdlib-expansion.md](../../spec/23-stdlib-expansion.md) §2–§3.
Reference implementation: Penstock 0.1.0-INDEV (conformance: corpus
`tests/corpus/20_stdlib_parsing_streaming.fsht`, props
`tests/props/p08_stdlib_numeric.fsht`, fuzz `b_checked` block here;
negatives `n30_checked_mixed_width` and `n31_parse_not_str` for the
type rules).

Explicit `checked_*` / `saturating_*` / `wrapping_*` operation variants
so overflow policy is written, not assumed; better numeric conversion
facilities alongside. **Ratified surface (fsht-03:01):** for every
integer scalar `T` — `checked_add/sub/mul/div/rem(a: T, b: T) ->
Option<T>` (`checked_div`/`rem` return `None` exactly where the plain
operators trap), `saturating_add/sub/mul(a: T, b: T) -> T`,
`wrapping_add/sub/mul(a: T, b: T) -> T` (equal to the plain
operators — explicit, not different), `int_min`/`int_max` type-bound
queries, plus the conversion pair `checked_cast<T, U>(x: T) ->
Option<U>` (representable only; NaN and out-of-range magnitudes are
`None` on float→int) and `saturating_cast<T, U>(x: T) -> U` (clamps;
NaN→0). Both operands of a variant MUST share the identical type —
no mixed-width promotion, no float operands (`F0201`); `U` is
inferred from context (`F0201` when unresolved). The conversion
facilities listed under fsht-03:02-03.02.10 landed here, with that
entry's history recording the cross-reference.

History:
- fsht-03:01 (accepted) — first accepted (wrapping remains the default
  for the plain operators).
- fsht-03:01 (ratified 2026-11-19) — chapter 23 §2/§3 normative;
  `checked_div`'s trap-equivalence (None exactly where the plain
  operator traps) and the identical-operand-type rule are part of the
  ratified surface. Int→float and float→float conversions stay with
  the truncating/rounding `as` of ch. 14 — deliberately unchanged.

### fsht-01:01-08.02.01 — the strict floating-point default

Status: normative. Spec: [ch. 13](../../spec/13-floating-point.md)

Strict, IEEE-754-like per-operation semantics by default: no
reassociation, no contraction, NaN and signed zero preserved; fast-math
is an explicit per-function or per-build opt-in.

History:
- fsht-01:01 — first standardised (the Option A policy).

### fsht-01:01-08.02.02 — transcendental lowering policy

Status: normative. Spec: [ch. 13](../../spec/13-floating-point.md)

`sqrt fabs floor ceil round fmin fmax pow exp log` map to intrinsics;
`sin cos tan log2 log10` call libm under strict (errno visible) and
lower to vectorisable intrinsics under fast-math (`--veclib=libmvec`
for vector routines); FMA contraction only under fast-math.

History:
- fsht-01:01 — first standardised.
