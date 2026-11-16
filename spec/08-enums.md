# 08 — Enums & tagged unions (normative in fsht-01:01)

## Declaration

```ebnf
enum_decl ::= "enum" identifier "{" variant { "," variant } "}"
variant   ::= identifier [ "(" type { "," type } ")" ]
```

```
enum Color { Red, Green, Blue }
enum Shape { Circle(f64), Rect(f64, f64), Point }
```

## Representation

`{ i64 tag, payload }` — the payload area is the largest variant's field
set, laid out per-variant like a mini-struct. Enums are values: assignment
and parameter passing copy.

## Construction

* **contextual** — `let c: Color = Red;` (variants resolve against the
  expected type);
* **qualified** — `Color.Green`;
* **with payload** — `Ok(v)`, `Circle(2.0)` (constructor form resolves
  against the expected enum type, including argument position of a call
  whose parameter is that enum type).

## `match`

```ebnf
match_stmt ::= "match" "(" expr ")" "{" arm { "," arm } "}"
arm        ::= ( variant [ "(" binder { "," binder } ")" ] | "_" ) "=>" block
```

* dispatches on the enum's tag; arms are blocks; payload bindings are
  **positional** and immutable copies;
* exhaustiveness is enforced — every variant covered or `_` present
  (`F0204`); a `match` in a value-returning function satisfies
  definite-return when every arm returns;
* `match` is a statement (chapter 05).

## Conformance requirements

Representation, the three construction forms, positional payload
bindings and exhaustiveness checking are MUST-level. Equality is NOT
defined for enum values — comparison lives in `match` arms (a SHOULD
diagnostic if an implementation silently accepts `enum == enum`).
Enums are usable in every value position: arrays, fields, parameters,
returns, generic instantiation payloads.
