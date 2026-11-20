# 22 — Const generics and const fn (normative in fsht-02:03)

> **Status.** Normative since fsht-02:03 (ratified 2026-11-19; first
> cut implemented in Penstock 0.1.0-INDEV). This chapter is a pure
> extension of fsht-01:01 — `const fn`, `const N: usize` parameters
> and const expressions in type positions did not exist before
> fsht-02:03, so no earlier program changes meaning. Registry entry:
> [fsht-02:03-06.03.01](../registry/features/06-generics.md).
> Everything listed in §5 is a registry-tracked deferral, deliberately
> outside fsht-02:03.

## 1. Const generic parameters

```ebnf
type_param  ::= identifier                                  (* type *)
              | "const" identifier ":" "usize"               (* value *)
array_type  ::= "[" type ";" length "]"
length      ::= integer_literal | const_expr
const_expr  ::= const_operand { ("+"|"-"|"*"|"/"|"%") const_operand }
const_operand ::= integer_literal | identifier
                | identifier "(" const_expr { "," const_expr } ")"
                | "(" const_expr ")"
```

Structs, enums and generic functions may declare `const N: usize`
parameters. The registry's motivating shapes work verbatim:

```
struct Vector<T, const N: usize> { data: [T; N] }
struct Matrix<T, const R: usize, const C: usize> { data: [T; R * C] }
fn sum<T, const N: usize>(v: [T; N]) -> T { ... }
```

* **Instantiation.** `Vector<f64, 3>` — the const argument may be a
  literal, a const expression over other const parameters, or a const
  fn call (`Vector<f64, square(3)>`). Distinct values are distinct
  interned types (`Vector$f64$3` vs `Vector$f64$4`).
* **Inference.** At generic call sites a const parameter is inferred
  from array-typed arguments: `sum(a)` with `a: [i64; 4]` instantiates
  `sum$i64$4`. The array's LENGTH feeds the parameter whose name appears
  in the parameter's length slot.
* Array lengths in type positions (`[T; R * C]`) evaluate at
  instantiation (`F0219` when not const-evaluable).
* Inside an instantiated body the const parameter is a compile-time
  VALUE: it folds to a literal in every expression position and MAY
  drive loop trip counts (constant-trip loops unroll).

## 2. `const fn`

```ebnf
const_fn_decl ::= "const" "fn" identifier "(" params ")" [ "->" type ] block
```

A `const fn` is interpreted at compile time for const-argument
positions and `const_assert` operands, and remains an ordinary runtime
function everywhere else. The interpreter works over the usize (u64)
domain and supports:

* expressions: integer literals, parameters and locals, arithmetic
  (`+ - * / %`), bitwise/shift, comparisons, logical connectives,
  numeric casts (width-truncation model), calls to other const fns,
  `sizeof`/`alignof` (resolved values);
* statements: `let`, assignment (including compound forms), `if`,
  `while`, `for (i in a..b)`, `return`, nested blocks.

Anything else — runtime calls, unknown names, division by zero,
runaway recursion/iteration — fails the evaluation with `F0219`
(budgets: 16384 interpreter steps, 32 recursion levels).

## 3. Compile-time assertions

```
const_assert(square(4) == 16);
```

`const_assert(expr)` MUST const-evaluate its argument; a false result
is a compile error (`F0220`) and generates no runtime code, a
non-evaluable argument is `F0219`.

## 4. Conformance requirements

Distinct interned instantiations per const value, `F0219`/`F0220`
behaviour, const-parameter folding inside instance bodies and the const
fn interpreter's supported subset are MUST-level. The interpreter's
budget values are *quality-of-implementation*; a conforming
implementation MAY raise them but MUST reject non-terminating
evaluation.

## 5. Deferrals (registry-tracked)

* Const parameters of types other than `usize` (i64, bool, enum
  constants).
* Const generic inference from container-typed arguments
  (`fn f<T, const N: usize>(v: Vector<T, N>)`).
* `sizeof(T)` inside const fn BODIES (today only in const_assert/array
  positions via the type binder).
* Compiler-generated specialisations beyond what LLVM derives from
  constant trip counts.
