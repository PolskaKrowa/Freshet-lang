# 06 — generics features (fsht-01:01)

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
generic algorithms do not exist yet (fsht-02:02).

History:
- fsht-01:01 — first standardised.

### fsht-02:02-06.02.01 — user-defined traits

Status: accepted (target fsht-02:02). Spec: —

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

History:
- fsht-02:02 (accepted) — first accepted with the static-dispatch
  default requirement stated.

### fsht-02:03-06.03.01 — const generics

Status: accepted (target fsht-02:03). Spec: —

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

History:
- fsht-02:03 (accepted) — first accepted.

### fsht-04:01-06.04.01 — closures

Status: proposed (not scheduled).

Generic callbacks and data transformations; needs the trait model of
fsht-02:02 first.

### A large object-oriented class system — deliberately rejected

Status: rejected for the foreseeable future.

Traits, generic structures and methods should give sufficient
abstraction without compromising the performance-oriented design. The
registry records the rejection so it is a decision, not an omission.
