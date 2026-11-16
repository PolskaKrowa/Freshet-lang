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

Status: accepted (target fsht-02:01). Spec: — (not yet normative)

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

History:
- fsht-02:01 (accepted) — first accepted for fsht-02:01 with the
  ownership-integration requirement stated above.

### fsht-02:01-02.09.02 — container move semantics

Status: accepted (target fsht-02:01). Spec: —

Move semantics and destruction for owned containers (drop on scope
exit, move-out invalidation) as part of fsht-02:01-02.09.01's model.

History:
- fsht-02:01 (accepted) — first accepted.
