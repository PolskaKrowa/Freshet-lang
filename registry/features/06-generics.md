# 06 — generics features (fsht-03:03)

### fsht-01:01-06.01.01 — monomorphised generics

Status: normative. Spec: [ch. 09](../../spec/09-generics.md)

Generic functions/structs/enums as templates: type-checked per
instantiation, never emitted themselves, mangled concrete instances
(`clamp$i64`), call-site inference from `T`/`*T`/`Span<T>`/
`Container<T,...>` arguments, no runtime dispatch.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-06.01.02 — built-in constraints

Status: normative. Spec: [ch. 09](../../spec/09-generics.md)

Exactly `Numeric`, `Int`, `Float`, `Signed`, checked at instantiation
(`F0203`). The deliberately small set: user-defined interfaces for
generic algorithms did not exist in fsht-01:01 — user traits landed in
fsht-02:02 (06.02.01) and extend the bound syntax without touching the
four built-ins, which remain reserved names with fixed meanings.

History:
- fsht-01:01 — first standardised.
- fsht-02:02 — user-defined traits standardised (06.02.01); this
  entry's surface is unchanged (the four built-ins stay reserved).

### fsht-02:02-06.02.01 — user-defined traits

Status: normative (fsht-02:02). Spec:
[ch. 21](../../spec/21-traits.md). Reference implementation: Penstock
0.1.0-INDEV (conformance: `tests/pos_traits.fsht` /
`tests/neg_traits_*.fsht` in the compiler tree; corpus
`tests/corpus/18_traits_static_dispatch.fsht` and negatives
`tests/negative/n20..n22` here).

```
trait Numeric {
    fn zero() -> Self;
    fn one() -> Self;
    fn add(a: Self, b: Self) -> Self;
    fn mul(a: Self, b: Self) -> Self;
}
```

User-defined traits with `impl` blocks, multiple trait bounds,
associated types, and **static dispatch through monomorphisation** (the
HPC philosophy preserved). This enables numerical algorithms over
different representations — f32/f64, complex numbers, fixed-point,
double-double, arbitrary precision, automatic differentiation — without
one implementation per representation. Dynamic dispatch is an explicit,
later opt-in, never the default.

**Ratified surface (fsht-02:02).** Trait declarations are pure
signature sets (`Self` the implementing-type placeholder); `impl Trait
for Type` members are ordinary functions under mangled names
(`Numeric$i64$add`) so every downstream pass sees direct calls — no
vtables, no trait objects. Calls: `Trait::method(args)` inside generic
fns (resolved per instantiation against the bound tparam), by first
argument type in concrete code (`F0216` when undetermined),
`Type::method` qualified calls, and `Self::method` inside impls.
Bounds compose with `+` (`T: Numeric + Scalable`, `F0218` for a
missing impl). New diagnostics: `F0216`, `F0217` (signature mismatch
after Self substitution), `F0218`.

**Deferrals carried forward:** blanket impls over template parameters,
generic traits, associated types, dynamic dispatch / trait objects,
operator overloading through traits.

History:
- fsht-02:02 (accepted) — first accepted with the static-dispatch
  default requirement stated.
- fsht-02:02 (in development) — first cut implemented in Penstock
  0.1.0-INDEV: declarations/impls with concrete targets, signature
  checking, `+`-bounds, static-dispatch call resolution, conformance
  tests in both repositories, draft chapter spec/21-traits.md
  (non-normative until ratification). Deferrals above carried forward.
- fsht-02:02 (ratified 2026-11-19) — chapter 21 promoted to
  normative; the deferrals above stay tracked (blanket impls,
  generic traits, associated types, dynamic dispatch, operator
  overloading through traits).

### fsht-02:03-06.03.01 — const generics

Status: normative (fsht-02:03). Spec:
[ch. 22](../../spec/22-const-generics.md). Reference implementation:
Penstock 0.1.0-INDEV (conformance: `tests/pos_constgen.fsht` /
`tests/neg_constgen_*.fsht` in the compiler tree; corpus
`tests/corpus/19_const_generics.fsht` and negatives
`tests/negative/n23..n25` here).

Compile-time array sizes beyond integer literals:

```
struct Vector<T, const N: usize> { data: [T; N] }
struct Matrix<T, const R: usize, const C: usize> { data: [T; R * C] }
```

Const generic parameters, general `const fn` evaluation, compile-time
assertions, compile-time type and size evaluation, and
compiler-generated specialisations for known dimensions —
tremendously useful for small fixed-size matrices, SIMD operations,
geometry and physics. The existing finite-domain precomputation is not
a replacement: these are different capabilities.

**Ratified surface (fsht-02:03).** `const N: usize` parameters
on structs/enums/fns; const arguments accept literals, const
expressions over other const parameters and const fn calls
(`Vector<f64, square(3)>`); distinct values are distinct interned
types (`Vector$f64$3`). Array lengths accept const expressions
(`[T; R * C]`, `F0219`). Const parameters are inferred from
array-typed call arguments and fold to literals inside instance
bodies (constant-trip loops unroll). `const fn` is interpreted at
compile time (literals, arithmetic, comparisons, casts, let, if,
while, for-in, return, assignment, calls to other const fns,
sizeof/alignof values; budgeted) while staying an ordinary runtime
function; `const_assert(expr)` is a compile-time assertion
(`F0219`/`F0220`). New diagnostics: `F0219`, `F0220`.

**Deferrals carried forward:** const parameters of types other than
usize, const inference from container-typed arguments, sizeof(T)
inside const fn bodies, specialisations beyond constant-trip unroll.

History:
- fsht-02:03 (accepted) — first accepted.
- fsht-02:03 (in development) — first cut implemented in Penstock
  0.1.0-INDEV per the surface above; conformance tests in both
  repositories, draft chapter spec/22-const-generics.md (non-normative
  until ratification). Deferrals above carried forward.
- fsht-02:03 (ratified 2026-11-19) — chapter 22 promoted to normative;
  the deferrals above stay tracked (non-usize const params, container
  inference, sizeof in const fn bodies, further specialisations).

### fsht-04:01-06.04.01 — closures

Status: proposed (not scheduled).

Generic callbacks and data transformations; needs the trait model of
fsht-02:02 first.

### A large object-oriented class system — deliberately rejected

Status: rejected for the foreseeable future.

Traits, generic structures and methods should give sufficient
abstraction without compromising the performance-oriented design. The
registry records the rejection so it is a decision, not an omission.
