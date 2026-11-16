# 08 — numeric-semantics features (fsht-01:01)

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

Status: accepted (target fsht-03:01). Spec: —

Explicit `checked_*` / `saturating_*` / `wrapping_*` operation variants
so overflow policy is written, not assumed; better numeric conversion
facilities alongside.

History:
- fsht-03:01 (accepted) — first accepted (wrapping remains the default
  for the plain operators).

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
