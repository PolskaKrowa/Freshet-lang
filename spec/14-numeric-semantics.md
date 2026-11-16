# 14 — Numeric semantics (normative in fsht-01:01)

These rules are the contract every backend MUST honour.

## Integer arithmetic

* **Overflow wraps.** `add`, `sub`, `mul` on signed and unsigned
  operands are two's-complement modular arithmetic — wrapping is the
  *specified* behaviour, never undefined behaviour (no `nsw`/`nuw`
  semantics are assumed by the source language). Checked, saturating and
  explicitly-wrapping operator variants are a recorded fsht-02 update
  target (`fsht-03:01-08.01.04`).
* Unsigned overflow likewise wraps (mod 2^N).

## Division and remainder

* Signed division **truncates toward zero**; the remainder takes the
  dividend's sign: `-7 / 2 == -3`, `-7 % 8 == -7`.
* Constant power-of-two divisors are strength-reduced with a
  rounding-correction sequence that preserves exactly these semantics;
  the unsigned forms keep the plain shift/mask.
* **Division by zero and `INT_MIN / -1` trap at runtime.** Division by
  the literal `0` is the compile-time `F0214`.

## Shifts

* `<<` is a logical shift; `>>` is arithmetic for signed operands and
  logical for unsigned.
* Shift counts greater than or equal to the operand width are avoided,
  not defined — a conforming compiler must not construct them from
  user code it cannot prove safe.

## Promotion and literals

* **Mixed-width arithmetic** promotes both operands to the common type
  first. A bare INT literal adopts the other operand's integer type —
  signedness AND width — so `i32var / 4` is 32-bit signed arithmetic.

## Comparisons and pointers

* Comparisons on pointers are defined for `==`/`!=` only (including
  against `nil`); ordering comparisons on pointers are a type error.
* Aggregate values (structs, enums, arrays, spans, str) are not
  comparable with `==` — `str` uses `str_eq`.
* `nil` is a `*void` null constant converting to any pointer type for
  equality tests.

## Operator families (checked in sema)

`+ - * /` numeric; `% & | ^ << >>` integers only; `== != < <= > >=`
numeric and pointer-equality; `&& || !` bool only; `ptr ± int` pointer
arithmetic; `ptr - ptr` (same pointee) element distance as `i64`.

## ABIs

Bool values are `i1` registers; bool parameters use the `i8` C ABI at
call boundaries (the zext at the boundary is generated).

## Conformance requirements

Every rule above is MUST-level; they are pinned by the corpus goldens
(two's-complement wrap, truncating division, remainder sign) and the
differential fuzz suite (configuration equivalence over mixed-width
casts, extreme constants, zero-trip loops).
