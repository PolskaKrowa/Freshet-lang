# 20 — Dynamic collections (DRAFT — fsht-02:01 in development)

> **Status.** This chapter is a DRAFT for the fsht-02:01 increment
> (registry entries [fsht-02:01-02.09.01](../registry/features/02-data-types.md)
> and [fsht-02:01-02.09.02](../registry/features/02-data-types.md)).
> It documents the first cut implemented in the reference compiler
> (Penstock 0.1.0-INDEV) and is NOT normative until fsht-02:01
> ratifies. Items marked *open* are design questions to settle at
> ratification. Nothing here alters fsht-01:01 programs: the types and
> builtins of this chapter did not exist in fsht-01:01.

## 1. `Vec<T>` — the dynamic container (fsht-02:01-02.09.01)

```ebnf
vec_type   ::= "Vec" "<" type ">"
vec_ctor   ::= "vec_new" "(" type [ "," expr ] ")"
             | "vec_from_span" "(" expr ")"
             | "vec_from_array" "(" expr ")"
             | "vec_clone" "(" expr ")"
vec_mut    ::= ("vec_push" | "vec_insert" | "vec_reserve"
             |  "vec_truncate" | "vec_resize" | "vec_clear"
             |  "vec_pop" | "vec_remove" | "vec_free")
               "(" "&" identifier "," … ")"
vec_read   ::= ("vec_get" | "vec_slice" | "vec_len"
             |  "vec_capacity" | "vec_is_empty") "(" expr { "," expr } ")"
vec_index  ::= identifier "[" expr "]"
vec_slice  ::= identifier "[" expr ".." expr "]"
```

A `Vec<T>` is a prelude **generic struct** monomorphised per element
type through the ordinary generic machinery:

```
Vec<T> = { data: *T, len: u64, cap: u64 }
```

* **Construction.** `vec_new(T, cap?)` (the element type is the first
  argument, the `malloc(T, n)` precedent; capacity 0 means the first
  push allocates), `vec_from_span(Span<T>)`, `vec_from_array([T; N])`,
  and `vec_clone(v)` — an owned deep copy (bytewise; elements are POD).
* **Mutation** takes the address of a `let mut` binding (`&v`, the
  `string_append(&s, …)` style): `vec_push(&v, x)`,
  `vec_pop(&v) -> Option<T>`, `vec_insert(&v, i, x)`,
  `vec_remove(&v, i) -> Option<T>`, `vec_reserve(&v, n)`,
  `vec_truncate(&v, n)`, `vec_resize(&v, n, fill)`,
  `vec_clear(&v)`, `vec_free(&v)`.
* **Reads** borrow by value: `v[i]` (an lvalue, bounds-checked against
  the runtime `len`; constant-folded and proven-safe indices are not
  checked), `vec_get(v, i) -> Option<T>`,
  `v.len` / `v.cap` (plain struct fields) and
  `vec_len` / `vec_capacity` / `vec_is_empty`.
* **Views without copying** (the `Slice`/`SliceMut` role — *open*:
  whether those names exist or views fold into `Span<T>`):
  `v[lo..hi]` and `vec_slice(v, lo, hi)` yield `Span<T>`;
  slicing validates `0 <= lo <= hi <= v.len`.
* A `Vec<u8>` is the dynamic byte buffer (`ByteBuffer`).

**Element types (first cut).** Elements MUST be non-owning: scalars,
`str` views, POD structs, enums, fixed arrays, spans. Owning elements
(`Vec<String>`, `Vec<Vec<T>>`) are rejected (`F0201`) until drop
elaboration through nested shapes lands.

**Parallelism.** Container mutation inside a `parfor` body is rejected
(`F0307`): growth reallocates (allocator contention) and the header
updates race across lanes. The supported shape takes the view first —
`let view: Span<T> = vec_slice(v, 0, v.len);` — and reads `view[i]`
inside the loop. Container reads through views are legal parfor
operations exactly like any other shared read.

## 2. Representation and ABI

* `sizeof(Vec<T>) = 24`, alignment 8; `{ data, len }` prefix matches a
  `Span<T>` view, so slicing is two loads.
* Monomorphisation names the instantiation `Vec$<T>` internally; the
  runtime operations are shared C functions taking the element size
  (`frt_vec_push(ptr, ptr, i64 esz)` …), so every element type shares
  one tested implementation.
* Capacity growth doubles from 8 elements (or the requested capacity)
  and reallocates; requests that would overflow `INT64_MAX / 2` bytes
  abort with a diagnostic rather than wrap.
* `vec_pop` / `vec_get` / `vec_remove` return `Option<T>`: the runtime
  writes the element through an out pointer and reports a found-flag;
  the `None` payload is never read (exhaustive `match` guarantees it).

## 3. Ownership: moves, invalidation, drop (fsht-02:01-02.09.02)

The binding rule of the registry entry: **container allocations are
inside the ownership analysis.** For `Vec<T>` bindings:

* **Move-out invalidation.** `let b = a;`, assignment `b = a;`,
  by-value arguments (plain or `give(v)`), and `return v;` transfer
  ownership. The source binding is invalidated — any later use is
  `F0301` (use-after-move). At runtime the transfer nulls the source's
  `data` field, which is what makes a pending drop on the source a
  no-op: **transfers are exactly-once by construction.**
* **Drop on scope exit.** The compiler emits a drop for every owned
  container binding at its scope's closing brace, in reverse
  declaration order, **after** that scope's `defer`s. By-value
  parameters drop at callee exit; `break` / `continue` flush the loop
  body's drops before branching; every return path drops what it still
  owns. Drops are idempotent (the runtime frees only a non-null data
  pointer).
* **Manual release.** `vec_free(&v)` frees immediately and pre-empts
  the scope-exit drop; the binding is invalidated (`F0301` on later
  use). Double free, use-after-free, `give()` of a non-owned container
  and rebinding a container that still owns its allocation (would
  leak the old buffer) are all `F0301`.
* **No container leaks.** Because every scope exit drops, an owned
  `Vec<T>` cannot leak; the pointer leak diagnostic does not apply to
  containers (their lifetime is the compiler's job, not a program
  obligation).

**First-cut restrictions** (tracked by the registry; the lifetime /
escape analysis planned as fsht-03:02-03.02.10 lifts them):

1. Owned containers stay at value level: a `Vec<T>` inside a user
   struct, an enum payload or a fixed array is rejected (`F0201`) —
   drop elaboration would have to walk user shapes.
2. Returning a borrowed view of a **local** container is rejected
   (`F0301`): the drop at fn exit would dangle the view. Views of
   *parameters* stay legal — the caller owns them. Returning the
   container itself is a move and legal.
3. The prelude `String` keeps its fsht-01:01 manual `string_free`
   model: `str_of(&s)` views routinely escape, so auto-drop for
   `String` waits for the same lifetime analysis.

## 4. Effects and optimisation

* Constructors (`vec_new`, `vec_from_*`, `vec_clone`) and growth
  mutators allocate; `vec_free` frees; reads classify through the
  argument root exactly like `soa_len` — `@pure` functions cannot
  touch containers.
* A function with container bindings or parameters emits hidden
  scope-exit drops, so its effect summary can never claim
  `memory(none)`.
* Indexing participates in the bounds machinery: constant indices fold,
  the BCE pass proves what it can (loop-trip induction, entry facts),
  and checked builds trap on the rest.
