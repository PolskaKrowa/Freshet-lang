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

`String` is `{ data: *u8, len, cap }`. **The ownership state machine does
not track String allocations in fsht-01:01** — they must be freed
explicitly or via `defer` (chapter 06). General dynamic containers and
bringing `String` under the ownership checker are the fsht-02:01 update
(registry `fsht-02:01-02.09.*`).

`String` is the *only* growable buffer type in fsht-01:01; numeric text
parsing (`parse_i64`/`parse_f64`) does not exist yet either — both facts
are honest limitations recorded in the registry with their update
targets.

## Conformance requirements

Byte-based indexing, `(ptr, len)` view semantics, slicing-as-view,
literal-as-value, the `String` builtin surface and its manual-free
caveat are MUST-level (the caveat included — an implementation that
silently GCs Strings would be non-conforming until the fsht-02:01 update
ratifies tracked containers).
