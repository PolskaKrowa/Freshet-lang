# 02 — data-type features (fsht-01:01)

### fsht-01:01-02.01.01 — scalar integer types

Status: normative. Spec: [ch. 02](../../spec/02-types.md)

`u8 u16 u32 u64 usize` / `i8 i16 i32 i64`; two's-complement, wrapping
arithmetic (ch. 08 subset).

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.01.02 — floating-point types

Status: normative. Spec: [ch. 02](../../spec/02-types.md) · [ch. 13](../../spec/13-floating-point.md)

`f32`/`f64` as IEEE-754 binary32/64 with the strict default contract.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.01.03 — `bool`

Status: normative. Spec: [ch. 02](../../spec/02-types.md)

1-byte storage, i1 registers, i8 at C-ABI call boundaries.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — bool parameters were uncallable (i1
  argument vs i8 signature); the boundary zext is generated.

### fsht-01:01-02.01.05 — `usize` representation

Status: normative, with an open question targeted at fsht-03:02.

`usize` and `u64` are distinct spellings with identical representation.
Whether `usize` should instead be target-pointer-sized must be resolved
before 32-bit WebAssembly support (fsht-03:03's wasm targets).

History:
- fsht-01:01 — first standardised (identical to `u64`, documented).
- fsht-03:02 (planned) — decide target-pointer-sized `usize` vs the
  fixed 64-bit representation; whichever way, the decision lands here
  with migration notes.

### fsht-01:01-02.02.01 — structs and C layout

Status: normative. Spec: [ch. 04](../../spec/04-structs.md)

C layout: declaration order, natural alignment, `align(N)` override;
full-field literals only (`F0201`); value (copy) semantics; nested
field access; `sizeof`/`alignof` as compile-time constants.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.02.03 — by-value struct parameters

Status: normative. Spec: [ch. 04](../../spec/04-structs.md)

Parameters pass by address; the callee sees its own copy.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the historical IR emitted `%struct.X
  %param` at the definition while call sites passed `ptr`, silently
  miscompiling by-value struct parameters (a `sum2(P{1.5,2.5})`
  returned `1.5`). The ABI contract is honoured on both sides and pinned
  by corpus tests.

### fsht-01:01-02.03.01 — fixed-size arrays `[T; N]`

Status: normative. Spec: [ch. 07](../../spec/07-arrays-spans-soa.md)

Length part of the type; compile-time `.len`; value copies; `F0212`
constant bounds; checked-build runtime bounds with traps.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — constant expressions stored into narrower
  slots skipped the width cast (malformed IR); fixed.

### fsht-01:01-02.04.01 — spans `Span<T>`

Status: normative. Spec: [ch. 07](../../spec/07-arrays-spans-soa.md)

Borrowed `(ptr, len)` pair, by-value parameter passing, slicing
`v[a..b]` as a no-copy sub-view validated in checked builds, `.ptr` for
FFI, mutation through the view.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.05.01 — SoA arrays `soa(S)`

Status: normative. Spec: [ch. 07](../../spec/07-arrays-spans-soa.md)

Descriptor handle `{ i32 nf, i64 n, ptr planes[nf] }`; `s[i].f` lowers
to `planes[f][i]` unit-stride; nested field paths resolve the inner
struct's plane.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.06.01 — `String` (owned growable buffer)

Status: normative, with a documented ownership gap. Spec: [ch. 10](../../spec/10-strings.md)

`{ data: *u8, len, cap }` with `string_new/from/append/free`,
`str_cat`, `str_of`. The ownership state machine does NOT track String
allocations yet — frees are explicit or deferred.

History:
- fsht-01:01 — first standardised.
- fsht-02:01 (planned) — String joins the ownership-checked container
  model together with Vec/Slice/SliceMut/ByteBuffer
  (fsht-02:01-02.09.01); the manual-free caveat is removed and the
  update is recorded here.

### fsht-01:01-02.06.02 — `str` (immutable UTF-8 view)

Status: normative. Spec: [ch. 10](../../spec/10-strings.md)

`(ptr, len)` view; byte-based indexing (the documented rule, not an
accident); slicing as views; literals as NUL-terminated values for C
interop; `str_eq` comparison.

History:
- fsht-01:01 — first standardised (maintainer decision: byte indexing).

### fsht-01:01-02.07.01 — `Option<T>` / `Result<T, E>`

Status: normative. Spec: [ch. 11](../../spec/11-option-result.md)

Prelude generic enums with the exact shapes; `Option<T>` is the
deliberate representation for absent values.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.07.02 — the `?` operator

Status: normative. Spec: [ch. 11](../../spec/11-option-result.md)

Early-return propagation with family/payload checks; defers run on the
early-exit path.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-02.08.01 — enums and tagged unions

Status: normative. Spec: [ch. 08](../../spec/08-enums.md)

`{ i64 tag, payload }`; contextual/qualified/payload construction;
`match` dispatch; copy semantics; usable in every value position.

History:
- fsht-01:01 — first standardised.

### fsht-02:01-02.09.01 — dynamic collections

Status: accepted → in development (target fsht-02:01). Spec: draft —
[spec/20-dynamic-collections.md](../../spec/20-dynamic-collections.md)
(not yet normative). Reference implementation: Penstock 0.1.0-INDEV
(conformance: `tests/pos_vec_*.fsht` / `tests/neg_vec_*.fsht` in the
compiler tree; corpus `tests/corpus/13_vec_containers.fsht` and
negative `tests/negative/n18..n22` here).

`Vec<T>` (dynamically growing array), `Slice<T>` / `SliceMut<T>`
(borrowed views), `ByteBuffer` (dynamic byte storage), and a properly
managed UTF-8 `String`. Surface: `push/pop/insert/remove`,
`reserve/resize/truncate`, `capacity/len/is_empty`, slicing without
copying, efficient bulk copying, custom allocators.

**The binding requirement:** container allocations MUST be integrated
with the ownership analysis. A language with sophisticated memory
checking MUST NOT ship containers that fall outside that system — a
proper ownership/move/destruction model for container types is the
prerequisite for a reliable standard library. This is the single
largest immediate omission in fsht-01:01.

**First cut (in development, Penstock).** `Vec<T>` is a prelude
generic struct `{ data: *T, len: u64, cap: u64 }` monomorphised per
element type through the ordinary generic machinery; the surface
follows the String free-function style:

- construction — `vec_new(T, cap?)`, `vec_from_span`,
  `vec_from_array`, `vec_clone` (owned deep copy);
- mutation (`&mut v`, the binding must be `let mut`) — `vec_push`,
  `vec_pop -> Option<T>`, `vec_insert`, `vec_remove -> Option<T>`,
  `vec_reserve`, `vec_truncate`, `vec_resize`, `vec_clear`,
  `vec_free` (manual release);
- reads — checked indexing `v[i]` (lvalue; bounds-checked against the
  runtime `len`), `vec_get(v, i) -> Option<T>`, `vec_len` /
  `vec_capacity` / `vec_is_empty` (the `v.len` / `v.cap` fields remain
  direct struct reads);
- borrowed views without copying — `v[lo..hi]` and
  `vec_slice(v, lo, hi)` yield `Span<T>`; a `Vec<u8>` is the
  ByteBuffer shape.

Elements are restricted to non-owning types (scalars, `str`, POD
structs, enums, arrays, spans); owning elements (`Vec<String>`,
`Vec<Vec<T>>`) are rejected with a diagnostic until drop elaboration
through nested shapes lands (tracked with 02.09.02). Container
mutation inside `parfor` bodies is rejected (race on the header /
allocator contention); the supported parallel shape is a `Span<T>`
view taken before the loop. Custom allocators and bulk-copy APIs are
NOT in the first cut.

**Open design question for fsht-02:01 ratification:** distinct
`Slice<T>` / `SliceMut<T>` types versus absorbing borrowed views into
the existing `Span<T>` (the first cut delivers views through
`Span<T>`; `Slice`/`SliceMut` may be resolved as aliases or dropped
at ratification). The `String` migration onto the container model is
deferred to fsht-03:02 (see below).

History:
- fsht-02:01 (accepted) — first accepted for fsht-02:01 with the
  ownership-integration requirement stated above.
- fsht-02:01 (in development) — first cut implemented in Penstock
  0.1.0-INDEV: `Vec<T>` with the surface above, ownership/move/drop
  integration per 02.09.02, monomorphised per element type; positive
  and negative conformance tests added to both this repository and
  the compiler tree. Spec text exists as the draft chapter
  spec/20-dynamic-collections.md and stays non-normative until
  fsht-02:01 ratifies. Deferrals carried forward: custom allocators,
  bulk copying, `Slice`/`SliceMut` naming, owning element types,
  String migration.

### fsht-02:01-02.09.02 — container move semantics

Status: accepted → in development (target fsht-02:01). Spec: draft —
[spec/20-dynamic-collections.md](../../spec/20-dynamic-collections.md)
§3 (not yet normative). Reference implementation: Penstock
0.1.0-INDEV.

Move semantics and destruction for owned containers (drop on scope
exit, move-out invalidation) as part of fsht-02:01-02.09.01's model.

**First cut (in development, Penstock).** For `Vec<T>` bindings:

- **drop on scope exit** — the compiler emits scope-exit drops in
  reverse declaration order, after the scope's `defer`s; a by-value
  container parameter drops at callee exit; `break`/`continue` flush
  the loop body's drops; every return path drops what it still owns.
  Drops are idempotent: the runtime frees only a non-null data pointer
  and nulls it after every transfer or release.
- **move-out invalidation** — `let b = a;`, assignment, by-value
  arguments (with or without `give()`), and `return v;` transfer
  ownership; the source binding is invalidated (use-after-move is
  F0301) and left inert at runtime.
- **manual release** — `vec_free(&v)` pre-empts the drop; double free,
  use-after-free and `give()` of a non-owned container are F0301;
  rebinding a container that still owns its allocation is an error
  (no silent leak).
- **first-cut restrictions** (all tracked here): owned containers stay
  at value level — containers inside user structs/enums/arrays and
  owning element types are rejected (drop elaboration through user
  shapes is the follow-up); returning a borrowed view of a *local*
  container is rejected because it would dangle after the drop (views
  of parameters stay legal — the caller owns them). The lifetime /
  escape analysis of fsht-03:02-03.02.10 is the tracked path to
  lifting these. The prelude `String` deliberately keeps its
  fsht-01:01 manual `string_free` model in the first cut: `str_of`
  views routinely escape, so auto-drop for String waits for that same
  lifetime analysis.

History:
- fsht-02:01 (accepted) — first accepted.
- fsht-02:01 (in development) — first cut implemented in Penstock
  0.1.0-INDEV together with 02.09.01 (the ownership analysis tracks
  container bindings: alive/freed/moved states, rebinding rule, leak
  exclusion under the drop guarantee).
