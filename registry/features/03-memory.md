# 03 — memory features (fsht-03:03)

### fsht-01:01-03.01.01 — `malloc` / `free`

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

`malloc(T, n)` — aligned, uninitialised, owned storage; `free(a)`
releases it; `memcpy`/`memset` raw byte primitives.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-03.01.02 — the ownership state machine

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

Alive / MaybeFreed / Freed / Moved tracking of `malloc` results; leak,
double free, use-after-free, use-after-give and give-of-non-owned are
all `F0301` errors; suspicious shapes warn `F0302`.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — compound assignments (`x /= 8`) shared the
  wrong lowering (`div` is not even an LLVM opcode); they now share the
  exact binary lowering including signed strength reduction.

### fsht-01:01-03.01.03 — `give` transfer

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

`give(a)` transfers ownership into an `owned` callee parameter; usable
as a call argument.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — `give(p)` as a call argument never parsed
  (keyword vs identifier); fixed and covered.

### fsht-01:01-03.02.01 — `owned` / `borrowed` parameters

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

The signature-carried borrowing contract (see fsht-01:01-01.02.03 for
the declaration side): `F0303` enforcement at every call site.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-03.02.02 — `unsafe` scopes

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

`unsafe { }` blocks omit bounds checks and downgrade in-scope ownership
diagnostics to warnings; the safe path is the default and the hatch is
greppable.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-03.03.01 — data stacks (`stack_alloc`)

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

Per-thread bump-pointer data stacks with scope death (watermark restore
after defers on every exit path), static-root lifetime proofs
(`F0926`/`F0927` diagnostics), interprocedural non-escape summaries,
and correct threading through `parfor` dispatch (collapsed inner
regions share the enclosing stacks).

History:
- fsht-01:01 — first standardised (Goose-ported pass family
  `F0925`–`F0927` in the reference implementation).

### fsht-03:02-03.02.09 — explicit mutable borrowing with exclusivity

Status: normative (fsht-03:02). Spec:
[spec/24-borrows-lifetimes.md](../../spec/24-borrows-lifetimes.md) §1–§2.
Reference implementation: Penstock 0.1.0-INDEV (conformance: corpus
`tests/corpus/21_borrow_mut_lifetimes.fsht`, props
`tests/props/p09_borrow_exclusivity.fsht`, fuzz `b_borrow` block here;
negatives `n26_borrow_two_mut`, `n27_borrow_view_conflict`,
`n28_view_escape_local`; the corpus 14/18/19 programs pin the
legacy-form compatibility).

`&mut`-style exclusive mutable borrows with aliasing exclusivity
checking, maturing the existing owned/borrowed model rather than
redesigning it. **Ratified surface (fsht-03:02):** general borrow
expressions `&mut place` / `&place` over locals, parameters, field
paths and indexed elements, yielding `*T`, live from creation to last
use; the `borrowed mut` parameter mode (call sites pass a mutable
borrow — `&mut place` or the legacy `&place`; a shared borrow or bare
pointer is the existing `F0303`); the exclusivity rule **one writer or
many readers** (`F0310`, the new diagnostic of ch. 15's safety table);
views (`Span<T>`/`str`) are shared borrows of their place from
creation to last use, so growth-mutators, release operations, moves
and `give` conflict with a live view — in-place element writes
(`v[i] = e`) do not invalidate views (no reallocation), and mutable
borrows inside a dispatched `parfor` body are `F0307`. The legacy
`&v` argument form of the mutation builtins is re-specified as the
mutable-borrow spelling it always was; `&mut v` MUST also be accepted
— fsht-01/02 programs are unaffected. Programs newly rejected were
outside defined behaviour in every prior version (growth/move against
a live view dangles it after reallocation or transfer).

History:
- fsht-03:02 (accepted) — first accepted.
- fsht-03:02 (ratified 2026-11-19) — chapter 24 §1–§2 normative;
  `F0310` minted (the `F0301` family's aliasing edges split out per
  ch. 15's ID-split rule). Disjoint-place simultaneous mutable borrows
  (`&mut a[0]` alongside `&mut a[1]`) are a ratified deferral (ch. 24
  §8) — one mutable borrow per storage root at a time today.

### fsht-03:02-03.02.10 — lifetime / escape analysis refinement

Status: normative (fsht-03:02). Spec:
[spec/24-borrows-lifetimes.md](../../spec/24-borrows-lifetimes.md) §3–§6.
Reference implementation: Penstock 0.1.0-INDEV (conformance: corpus
`tests/corpus/21_borrow_mut_lifetimes.fsht`, negative
`n28_view_escape_local`).

Better lifetime and escape analysis for slices and pointers; better
numeric conversion facilities; a clearly documented integer
representation model (resolving fsht-01:01-02.01.05's `usize` question
here, not separately). **Ratified surface (fsht-03:02):** borrows and
views MUST NOT outlive their storage — `F0311` (returning `&mut local`
or a view of a local; storing into an outliving root), replacing the
blunt fsht-02:01 `F0301` rejection with a precise lifetime diagnostic
(same rejection — it was always unsound; the "views of parameters stay
legal" permission is clarified to mean the borrowed-parameter case);
interprocedural non-escape summaries cover `&mut x` passed to callees
that provably do not let it escape; the **`String` migration** onto the
ownership-tracked container model (auto-drop, move invalidation,
pre-emptive `string_free`, `string_clone`, `str_of` views under the
borrow discipline — ch. 24 §4, cross-referenced from 02.06.01);
**drop elaboration through user shapes** lifting the fsht-02:01
value-level restriction (containers/String in struct fields, enum
payloads, fixed arrays; owning element types `Vec<String>`/
`Vec<Vec<T>>` — ch. 24 §5, cross-referenced from 02.09.01/02.09.02);
and the **integer representation model**: `usize` is permanently the
fixed 64-bit unsigned integer on every target, including wasm32
(ch. 24 §6, cross-referenced from 02.01.05). The better numeric
conversion facilities landed earlier, with fsht-03:01's variant
family (08.01.04, ch. 23 §3).

History:
- fsht-03:02 (accepted) — first accepted.
- fsht-03:02 (ratified 2026-11-19) — chapter 24 §3–§6 normative;
  `F0311` minted. The escape rules close the fsht-02:01 restrictions
  1 and 3 (lifting) and reclassify restriction 2 (still rejected, now
  `F0311`); the conversion-facilities component was delivered with
  fsht-03:01's 08.01.04 and is recorded there.
