# 02 — Types (normative in fsht-01:01)

## The type grammar

```ebnf
type ::= scalar | pointer_type | array_type | span_type | soa_type
       | str_type | enum_type | fn_ptr_type | struct_type
scalar ::= "u8"|"u16"|"u32"|"u64"|"usize"
         | "i8"|"i16"|"i32"|"i64"
         | "f32"|"f64" | "bool"
pointer_type ::= "*" type
array_type   ::= "[" type ";" int_literal "]"
span_type    ::= "Span" "<" type ">"
soa_type     ::= "soa" "(" struct_type ")"
str_type     ::= "str"
fn_ptr_type  ::= "fn" "(" [ type_list ] ")" [ "->" type ]
struct_type  ::= identifier
enum_type    ::= identifier
```

## Scalars

| scalar | width | notes |
|---|---|---|
| `u8 u16 u32 u64` | 8/16/32/64 | unsigned, wrapping arithmetic |
| `usize` | 64 | unsigned index/length type; **same representation as `u64`** (distinct spelling) |
| `i8 i16 i32 i64` | 8/16/32/64 | signed two's complement, wrapping arithmetic |
| `f32 f64` | 32/64 | IEEE-754 binary32/64 |
| `bool` | 1 byte (i1 registers; i8 at C-ABI boundaries) |

`usize` and `u64` are distinct spellings with identical representation
(fsht-01:01-02.01.05). The open representation question was resolved
by fsht-03:02 (chapter 24 §6): `usize` is **permanently the fixed
64-bit unsigned integer on every target** — including 32-bit
WebAssembly — so indices, lengths and `sizeof` results never change
with `--target`. The two names are interchangeable in representation
and MUST both exist.

## Aggregates and views

| type | nature |
|---|---|
| `T` (struct name) | struct value — C layout, copy semantics (chapter 04) |
| `soa(S)` | descriptor handle `{ i32 nf, i64 n, ptr planes[nf] }` over planes of S's fields (chapter 07) |
| `[T; N]` | fixed-size array — the length is part of the type (chapter 07) |
| `Span<T>` | borrowed `(ptr, len)` view over contiguous `T` (chapter 07) |
| `str` | immutable UTF-8 string view, byte-indexed (chapter 10) |
| enum name | tagged union `{ i64 tag, payload }` (chapter 08) |
| `Option<T>` / `Result<T,E>` | prelude generic enums (chapter 11) |
| `fn(P1, P2) -> R` | first-class function pointer, pointer-sized (chapter 17) |

## Conversions

Implicit conversions are permitted ONLY for:

1. **literal type adoption** — a literal initialises a binding of any
   compatible numeric annotation;
2. **widening int→int of the same signedness**;
3. **`f32`→`f64`**.

Everything else requires an explicit cast `expr as T`. Narrowing casts
warn (`F0211`). Pointer↔number casts are forbidden (`F0201`). A bare INT
literal in a mixed operation adopts the other operand's integer type —
signedness AND width — so `i32var / 4` is 32-bit signed arithmetic
(chapter 14).

`nil` is a `*void` null constant that converts to any pointer type for
equality tests. `sizeof(T)` and `alignof(T)` are compile-time constants
usable in `let` bindings for scalars, structs, enums, arrays and
`soa(S)`.

## Conformance requirements

* Widths, signedness and the `usize`≡`u64` representation rule are
  MUST-level.
* The conversion matrix above is MUST-level: an implicit conversion
  outside the three listed families is a conformance violation.
* `F0211` (narrowing), `F0201` (type error, including ptr↔number casts)
  are the expected diagnostics.
