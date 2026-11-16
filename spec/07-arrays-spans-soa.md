# 07 — Arrays, spans & SoA (normative in fsht-01:01)

## Fixed-size arrays `[T; N]` (fsht-01:01-02.03.01)

```ebnf
array_type    ::= "[" type ";" int_literal "]"
array_literal ::= "[" expr { "," expr } "]"
```

* The length is part of the type; `sizeof([T; N]) = N * sizeof(T)`.
* `.len` is a **compile-time constant** (`a.len`).
* Arrays are values: assignment and parameter passing copy (`memcpy`),
  the callee sees its own copy.
* Constant indices outside `0..N-1` are `F0212` at compile time;
  non-constant indices are bounds-checked in checked builds and trap
  otherwise; a proven-safe index is never checked.
* An array literal adopts its annotation; without one it is inferred from
  its elements. Nesting (`[[i64; 2]; 2]`), arrays of structs and
  arrays-in-structs are all valid.

## Spans `Span<T>` (fsht-01:01-02.04.01)

```ebnf
span_ctor ::= "span" "(" expr "," expr ")" | "span" "(" identifier ")"
slice     ::= postfix "[" expr ".." expr "]"
span_ops  ::= identifier "." ("len" | "ptr") | identifier "[" expr "]"
```

* A span is a borrowed `(ptr, len)` pair passed **by value** — the
  signature carries the valid range instead of a separate count argument.
* `span(p, n)` views raw memory; `span(arr)` views a fixed array;
  `v[a..b]` is a sub-view with **no copy**.
* Indexing is bounds-checked in checked builds; slicing validates
  `0 <= a <= b <= len`.
* Mutation through a span writes the underlying storage;
  `borrowed` parameters (chapter 03) make view read-onlyness a checked
  contract. `v.ptr` hands the raw pointer out (FFI).

## SoA arrays `soa(S)` (fsht-01:01-02.05.01)

```ebnf
soa_type  ::= "soa" "(" struct_type ")"
soa_ctor ::= "soa_new" "(" struct_type "," expr ")"
soa_free  ::= "soa_free" "(" expr ")"
soa_len   ::= "soa_len" "(" expr ")"
```

* A `soa(S)` value is a descriptor handle:
  `{ i32 nf, i64 n, ptr planes[nf] }` — one 64-byte-aligned plane per
  field of S.
* `s[i].f` lowers to `planes[f_idx][i]` — **unit-stride** loads that
  vectorise; nested field paths (`s[i].f.g`) resolve the inner struct's
  plane.
* Access shape is identical to AoS source — `b[i].x = 1.0` — which is the
  point: switching `malloc(Body, n)` to `soa_new(Body, n)` changes only
  the declaration and the free call.

The AoS→SoA advisories and the provably-safe automatic transform are
compiler capabilities documented in chapter 15/19 (`F0408`, `F0903`);
the `soa(S)` language surface above is what the standard fixes.

## Conformance requirements

Array value semantics, compile-time `.len`, checked-build bounds rules,
span `(ptr, len)` pair semantics, slicing validation and the SoA plane
addressing are MUST-level. The descriptor's exact field layout
(`{i32 nf, i64 n, ptr planes}`) is normative for interop with the runtime
C ABI (libfsh).
