# 09 — Generics (normative in fsht-01:01)

## Declaration

```ebnf
generic_decl ::= "<" type_param { "," type_param } ">"
type_param   ::= identifier [ ":" constraint ]
constraint   ::= "Numeric" | "Int" | "Float" | "Signed"
```

Generic functions, structs and enums all exist:

```
fn clamp<T: Numeric>(x: T, low: T, high: T) -> T { ... }
struct Pair<T, U> { a: T, b: U }
enum ReadResult<T> { Value(T), EndOfFile, Error(i32) }
fn first<T, U>(p: Pair<T, U>) -> T { return p.a; }
```

## Semantics: templates, monomorphised (fsht-01:01-06.01.01)

* Generic declarations are **templates**: they are type-checked per
  instantiation and never emitted themselves.
* Each distinct argument set creates a concrete instance with a mangled
  name (`clamp$i64`, `Pair$f64$i64`). No runtime dispatch exists.
* **Call-site inference**: a `T`-typed parameter, `*T`, `Span<T>` or
  `Container<T, ...>` argument determines `T`. Literals adopt the
  inferred instantiation; explicit casts (`9 as i64`) and suffixed
  literals (`0.5f32`) pin it.
* Constraints are checked at instantiation (`F0203`): the fsht-01:01 set
  is exactly `Numeric`, `Int`, `Float`, `Signed`.
* Generic struct literals adopt the annotated instantiation:
  `let p: Pair<f64, i64> = Pair { a: 1.5, b: 7 };`.
* Nested instantiation (`Pair<Pair<i64,i64>, f64>`) works; a zero-value
  for a generic `T` may be written `0 as T` (only meaningful for numeric
  instantiations).

## Why the constraint set is deliberately small

User-defined traits landed in **fsht-02:02** ([chapter 21](21-traits.md),
registry [fsht-02:02-06.02.01](../registry/features/06-generics.md)):
`T: SomeTrait` bounds and `+`-composition extend this chapter's set
without touching the four built-ins, which remain reserved names with
fixed meanings. Associated types and dynamic dispatch still do not
exist — they are registry-tracked deferrals of fsht-02:02. The four
built-in concepts cover the numeric-kernel space the language targets;
the design constraint the registry records is that static dispatch
(monomorphisation) remains the default even with user traits.

## Conformance requirements

Monomorphisation semantics, mangled distinct instances, inference rules,
constraint checking at instantiation and never-emitted templates are
MUST-level. Static dispatch as the only dispatch form is MUST-level in
fsht-01:01 (later versions may add opt-in dynamic dispatch — tracked in
the registry, never silently).
