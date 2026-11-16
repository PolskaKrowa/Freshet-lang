# 04 — Structs (normative in fsht-01:01)

## Declaration and layout

```ebnf
struct_decl ::= "struct" identifier [ "align" "(" int_literal ")" ]
                "{" field { "," field } "}"
field       ::= identifier ":" type
```

Structs use **C layout**: fields sit in declaration order with natural
alignment; the struct's alignment is the maximum field alignment unless
`align(N)` overrides it; `sizeof` follows the C padding rules. `align(64)`
is the idiomatic way to pin a hot struct into one cache line (the
`F0404` straddle diagnostic measures exactly this, chapter 15).

```
struct V3 { x: f64, y: f64, z: f64 }
struct Cell align(64) { p: V3, v: V3, m: f64 }   // one cache line
```

## Literals and field access

```ebnf
struct_literal ::= struct_type "{" field_init { "," field_init } "}"
field_init     ::= identifier ":" expr
```

A struct literal MUST initialise **all** fields — no partial
initialisation in strict mode (`F0201`). Field access is postfix:
`c.p.x` (nested paths resolve left to right); `p.f` auto-dereferences on
`*Struct` values; `&x` takes the address of any lvalue.

```
let c = Cell { p: V3 { x: 1.0, y: 2.0, z: 3.0 },
               v: V3 { x: 0.5, y: 0.5, z: 0.5 }, m: 2.0 };
fn f(c: *Cell) { ... c.m }        // auto-deref
let r = f(&c);
```

## Value semantics

Structs are memory values:

* assignment **copies** (a `memcpy` of the whole aggregate);
* parameters pass by address and the callee sees its own **copy** (the
  by-value ABI) — a conforming compiler must honour this on both the
  definition and the call site (the reference implementation once
  miscompiled this: `sum2(P{1.5, 2.5})` returning `1.5`; the ABI contract
  is now pinned by corpus tests);
* field access lowers to `getelementptr`-style address computation;
* aggregate equality with `==` is NOT defined (chapter 14) — compare
  fields, or wrap in an enum with `match`.

`sizeof(T)` / `alignof(T)` are compile-time constants for structs
(fsht-01:01-02.02.02); layout tables for every struct are part of the
compiler's report surface (chapter 19).

## Conformance requirements

* C layout, `align(N)`, full-field literals and copy semantics are
  MUST-level.
* The cache-layout advisories (`F0407` padding, `F0404` straddle) are
  SHOULD-level diagnostics — a conforming compiler should detect the
  documented shapes and MAY apply them only as warnings by default
  (chapter 15's severity rules).
