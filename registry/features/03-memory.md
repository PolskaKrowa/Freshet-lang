# 03 — memory features (fsht-01:01)

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

Status: accepted (target fsht-03:02). Spec: —

`&mut`-style exclusive mutable borrows with aliasing exclusivity
checking, maturing the existing owned/borrowed model rather than
redesigning it.

History:
- fsht-03:02 (accepted) — first accepted.

### fsht-03:02-03.02.10 — lifetime / escape analysis refinement

Status: accepted (target fsht-03:02). Spec: —

Better lifetime and escape analysis for slices and pointers; better
numeric conversion facilities; a clearly documented integer
representation model (resolving fsht-01:01-02.01.05's `usize` question
here, not separately).

History:
- fsht-03:02 (accepted) — first accepted.
