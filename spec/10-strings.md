# 10 — Strings (normative in fsht-01:01)

## `str` — the immutable view

```ebnf
str_type   ::= "str"
str_ops    ::= identifier "." "len" | identifier "[" expr "]"
             | identifier "[" expr ".." expr "]"
```

```
let s: str = "hello";            // UTF-8 view (ptr, len)
s.len                           // 5 (bytes)
s[0]                            // 104 (u8 — BYTE indexing)
let w: str = s[1..4];            // "ell" view, no copy
```

* `str` is an immutable, non-owning UTF-8 view as a `(ptr, i64)` pair.
  Literals are `str` **values** (NUL-terminated in the constant pool for
  C interop), not just print arguments.
* **Indexing is byte-based** — `s[i]` yields the i-th byte as `u8`.
  UTF-8-aware iteration/decoding is explicit user code. This is the
  documented rule, not an accident (fsht-01:01-05.02.01).
* Slicing `s[a..b]` produces a sub-view (no copy), validated in checked
  builds.
* `print` accepts any `str` value.
* String literals may appear as struct fields: `struct Named { name:
  str, value: i64 }`.

## `String` — the owned growable buffer (fsht-01:01-02.06.01)

```
let mut out: String = string_new();
string_append(&out, "abc");           // grows in place
let full: String = str_cat(a, b);     // concatenation allocates
str_of(&out)                          // -> str view over the buffer
string_free(&full);                   // releases it
```

The builtins: `string_new`, `string_from(literal)`, `string_append(&s,
more)`, `str_cat(a, b)`, `str_of(&s)`, `string_free(&s)`,
`str_eq(a, b)`, `str_to_cstr(s)` (NUL-terminated copy; caller frees),
`fmt_i64(x) -> String`, `fmt_f64(x, digits) -> String`.

`String` is `{ data: *u8, len, cap }`. Since fsht-03:02 the ownership
state machine tracks `String` ([chapter 24 §4](24-borrows-lifetimes.md)):
scope-exit drops, move-out invalidation and the pre-emptive
`string_free` — the fsht-01:01 manual-free caveat is closed. Dynamic
containers joined the checked model in fsht-02:01 (`Vec<T>`,
[chapter 20](20-dynamic-collections.md), registry `fsht-02:01-02.09.*`).
Numeric text parsing (`parse_i64`/`parse_u64`/`parse_f64`) landed in
fsht-03:01 ([chapter 23](23-stdlib-expansion.md), registry
`fsht-03:01-05.04.01`).

`String` was the *only* growable buffer type in fsht-01:01 — `Vec<T>`
joined in fsht-02:01 (chapter 20) and the ownership-tracking gap closed
in fsht-03:02 (chapter 24). Numeric text parsing existed in no version
before fsht-03:01 — both facts are recorded in the registry with their
update references.

## Conformance requirements

Byte-based indexing, `(ptr, len)` view semantics, slicing-as-view,
literal-as-value, and the `String` builtin surface are MUST-level.
Since fsht-03:02 the ownership-tracked `String` lifecycle of chapter 24
(auto-drop, moves, pre-emptive `string_free`, the `str_of` borrow
discipline) is MUST-level too — an implementation that leaves `String`
untracked is non-conforming to fsht-03:02+ (it conformed to fsht-02:03
and earlier, which is the intended per-version gating).
