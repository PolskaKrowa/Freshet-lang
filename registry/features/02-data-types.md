# 02 — data-type features (fsht-03:03)

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

Status: normative; the open question was resolved in fsht-03:02. Spec:
[ch. 02](../../spec/02-types.md) · [ch. 24 §6](../../spec/24-borrows-lifetimes.md)

`usize` and `u64` are distinct spellings with identical representation.
Whether `usize` should instead be target-pointer-sized had to be
resolved before 32-bit WebAssembly support — and it was, by fsht-03:02,
before fsht-03:03 ratified the wasm32 targets.

History:
- fsht-01:01 — first standardised (identical to `u64`, documented).
- fsht-03:02 (planned) — decide target-pointer-sized `usize` vs the
  fixed 64-bit representation; whichever way, the decision lands here
  with migration notes.
- fsht-03:02 (ratified 2026-11-19) — **resolved: `usize` is permanently
  the fixed 64-bit unsigned integer on every target, wasm32 included**
  (ch. 24 §6's integer representation model). Migration notes: none
  required — the representation matches fsht-01:01 on every ratified
  target; indices, lengths and `sizeof` never change with `--target`.

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

Status: normative; the ownership gap was closed by the fsht-03:02
migration. Spec: [ch. 10](../../spec/10-strings.md) ·
[ch. 24 §4](../../spec/24-borrows-lifetimes.md)

`{ data: *u8, len, cap }` with `string_new/from/append/free`,
`str_cat`, `str_of`.

History:
- fsht-01:01 — first standardised; the ownership state machine did
  NOT track String allocations — frees were explicit or deferred
  (the documented gap).
- fsht-02:01 (deferral, corrected at ratification) — the
  ownership-checked container model landed for `Vec<T>` only
  (02.09.01/02.09.02; views resolved to `Span<T>`, so no
  Slice/SliceMut). The String migration onto it is deferred to
  fsht-03:02 with the lifetime/escape analysis (03.02.10):
  `str_of` views routinely escape their owner, so auto-drop would
  dangle them. String keeps the manual `string_free` model and the
  caveat above until then.
- fsht-03:02 (ratified 2026-11-19) — **migration delivered** (03.02.10,
  ch. 24 §4): `String` is ownership-tracked — scope-exit auto-drop,
  move-out invalidation, pre-emptive `string_free` (binding
  invalidated), `string_clone`/`string_clear` added; `str_of` views
  are shared borrows under the `F0310`/`F0311` discipline. Layout
  unchanged (`{ data, len, cap }`); programs relying on the untracked
  gap (use-after-`string_free`) were already undefined at runtime in
  every prior version and are now diagnosed `F0301`.

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

Status: normative (fsht-02:01). Spec:
[spec/20-dynamic-collections.md](../../spec/20-dynamic-collections.md)
Reference implementation: Penstock 0.1.0-INDEV (conformance:
`tests/pos_vec_*.fsht` / `tests/neg_vec_*.fsht` in the compiler tree;
corpus `tests/corpus/14_vec_containers.fsht` and negative
`tests/negative/n15..n19` here).

`Vec<T>` (dynamically growing array), borrowed views (ratified as
`Span<T>` — no separate slice types), `ByteBuffer` (dynamic byte
storage, = `Vec<u8>`), and a properly managed UTF-8 `String`
(migrated onto this model in fsht-03:02 — history below). Surface:
`push/pop/insert/remove`,
`reserve/resize/truncate`, `capacity/len/is_empty`, slicing without
copying; efficient bulk copying and custom allocators remain
registry-tracked deferrals.

**The binding requirement:** container allocations MUST be integrated
with the ownership analysis. A language with sophisticated memory
checking MUST NOT ship containers that fall outside that system — a
proper ownership/move/destruction model for container types is the
prerequisite for a reliable standard library. This is the single
largest immediate omission in fsht-01:01.

**Ratified surface (fsht-02:01).** `Vec<T>` is a prelude
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

Elements were restricted to non-owning types (scalars, `str`, POD
structs, enums, arrays, spans); owning elements (`Vec<String>`,
`Vec<Vec<T>>`) were rejected with a diagnostic until drop elaboration
through nested shapes landed — which fsht-03:02 delivered (history
below; the fsht-02:01 restriction was ratified scope, tracked with
02.09.02). Container mutation inside `parfor` bodies is rejected (race
on the header / allocator contention); the supported parallel shape is
a `Span<T>` view taken before the loop. Custom allocators and
bulk-copy APIs are NOT in fsht-02:01 (registry-tracked deferrals).

**Ratified resolution (fsht-02:01):** borrowed views fold into the
existing `Span<T>` — no distinct `Slice<T>` / `SliceMut<T>` types
(`v[lo..hi]` and `vec_slice` yield `Span<T>`; in-place element
mutation goes through the `v[i]` lvalue). `Slice`/`SliceMut` are
dropped from the roadmap. The `String` migration onto the container
model was deferred to fsht-03:02 and delivered with it (see below).

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
- fsht-02:01 (ratified 2026-11-19) — chapter 20 promoted to normative.
  The naming question is closed: views are `Span<T>` only —
  `Slice`/`SliceMut` dropped. Remaining deferrals carried forward:
  custom allocators, bulk copying, owning element types (with
  02.09.02), String migration (fsht-03:02).
- fsht-03:02 (ratified 2026-11-19) — the owning-element restriction
  and the value-level restriction (containers inside user
  structs/enums/arrays) are lifted by the drop elaboration of
  03.02.10 (ch. 24 §5); String migration delivered with the same
  increment (02.06.01). Custom allocators and bulk-copy APIs remain
  deferrals.

### fsht-02:01-02.09.02 — container move semantics

Status: normative (fsht-02:01). Spec:
[spec/20-dynamic-collections.md](../../spec/20-dynamic-collections.md)
§3. Reference implementation: Penstock 0.1.0-INDEV.

Move semantics and destruction for owned containers (drop on scope
exit, move-out invalidation) as part of fsht-02:01-02.09.01's model.

**Ratified surface (fsht-02:01).** For `Vec<T>` bindings:

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
- **ratified restrictions** (all tracked here): owned containers stay
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
- fsht-02:01 (ratified 2026-11-19) — normative together with
  02.09.01; the restrictions above are ratified scope, tracked for
  lifting by fsht-03:02-03.02.10.
- fsht-03:02 (ratified 2026-11-19) — the tracked lifting delivered:
  owned containers now appear inside user structs/enums/arrays and
  as owning elements (`Vec<String>`, `Vec<Vec<T>>`) — drops walk the
  shape innermost-first, moves transfer whole-shape, `vec_clone`
  deep-copies element-wise (ch. 24 §5). The return-a-view-of-a-local
  rejection was reclassified `F0301` → `F0311` (same rejection,
  precise escape diagnostic — 03.02.09/03.02.10).
