# 21 — Traits (normative in fsht-02:02)

> **Status.** Normative since fsht-02:02 (ratified 2026-11-19; first
> cut implemented in Penstock 0.1.0-INDEV). This chapter is a pure
> extension of fsht-01:01 — `trait`, `impl` and `Self` did not exist
> before fsht-02:02, so no earlier program changes meaning. Registry
> entry: [fsht-02:02-06.02.01](../registry/features/06-generics.md).
> Everything listed in §6 is a registry-tracked deferral, deliberately
> outside fsht-02:02.

## 1. Declarations

```ebnf
trait_decl   ::= [ "pub" ] "trait" identifier "{"
                 { trait_method } "}"
trait_method ::= "fn" identifier "(" [ trait_param { "," trait_param } ] ")"
                 [ "->" type ] ";"
trait_param  ::= identifier ":" type
impl_decl   ::= [ "pub" ] "impl" identifier "for" type "{"
                { impl_method } "}"
impl_method ::= "fn" identifier "(" [ param { "," param } ] ")"
                [ "->" type ] block
```

A trait is a pure **signature set**: no fields, no bodies, no code of
its own. `Self` inside a method signature (parameter or return type,
including `*Self`, `[Self; N]`, `Span<Self>` positions) is the
placeholder for the implementing type.

```
trait Numeric {
    fn zero() -> Self;
    fn one() -> Self;
    fn add(a: Self, b: Self) -> Self;
    fn mul(a: Self, b: Self) -> Self;
}
impl Numeric for i64 {
    fn zero() -> Self { return 0; }
    fn one() -> Self { return 1; }
    fn add(a: Self, b: Self) -> Self { return a + b; }
    fn mul(a: Self, b: Self) -> Self { return a * b; }
}
```

Inside an impl block, `Self` in member signatures and bodies resolves
to the impl's target type (the compiler substitutes it textually before
the member is checked), and `Self::method(...)` calls a sibling method
of the same trait.

## 2. Semantics: static dispatch through monomorphisation

* An impl target MUST be a **concrete** type: a scalar, a struct, an
  enum type, or a generic-struct *instantiation* (`Vec<i64>`).
  Blanket impls over template parameters (`impl Numeric for Vec<T>`)
  are *deferred* — see the registry entry.
* Every impl member MUST match the trait's declared signature after
  `Self` substitution (`F0217`), and the trait MUST declare it.
* Impl member functions are ordinary functions under a mangled name
  (`Numeric$i64$add`); from sema onward every pass — effects, checks,
  ownership, IRgen, LLVM — sees plain direct calls. **There are no
  vtables and no trait objects: dispatch is static by construction**,
  preserving the HPC philosophy (registry 06.02.01 requirement).
* Dynamic dispatch is a later, explicit opt-in — never the default.

## 3. Method calls

```
call ::= identifier "::" identifier "(" [ args ] ")"
```

* `Trait::method(args)` in **generic code**: the implementing type is
  the bound type parameter (`fn dot<T: Numeric>(a: T, b: T)` calls
  `Numeric::mul` — resolved to the impl for the inferred `T` at every
  instantiation).
* `Trait::method(args)` in **concrete code**: the impl is selected by
  the first argument whose type has an impl of the trait; a
  zero-argument call is legal only when exactly one impl of the trait
  exists (`F0216` otherwise).
* `Rect::area(r)` — a TYPE-qualified call — resolves any impl for that
  type providing the method (`F0216` when two traits provide it).
* `Self::method(...)` inside an impl calls the same trait's method for
  the impl's own target (zero-argument safe).

## 4. Trait bounds

```ebnf
constraint  ::= constraint_part { "+" constraint_part }
constraint_part ::= "Numeric" | "Int" | "Float" | "Signed"
                  | identifier   (* a declared trait *)
```

Generic parameters may be bound by several traits at once
(`fn f<T: Numeric + Scalable>`); every part must hold at instantiation.
A bound by a user trait requires an impl for the inferred type
(`F0218`).

## 5. Conformance requirements

Impl-target concreteness, signature checking with `Self` substitution,
static dispatch with no vtable emitted for a monomorphised trait call,
and `+`-separated bounds are MUST-level. Deferred items — blanket impls,
generic traits, associated types, dynamic dispatch — remain registry
tracked and MUST NOT be added silently.

## 6. Deferrals (registry-tracked)

* Blanket impls (`impl Trait for Vec<T>`) and generic traits.
* Associated types (models like `Iterator` need them; the registry
  example uses plain `Self` methods).
* Dynamic dispatch / trait objects (`dyn Trait`), operator overloading
  through traits, `impl` blocks for builtin constraint semantics.
