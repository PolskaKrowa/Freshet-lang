# 01 — core language features (fsht-03:03)

### fsht-01:01-01.01.01 — lexical structure

Status: normative. Spec: [ch. 01](../../spec/01-lexical.md)

Tokens, C-like identifiers, line and (nesting) block comments, numeric
literals with optional suffixes (`42u8`, `1.5f32`, `0x1F`), string
literals as `str` values.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.01.02 — preprocessor

Status: normative. Spec: [ch. 01](../../spec/01-lexical.md)

`#include` (quoted/angled, `-I` search), `#define` object and
function-like macros, `#link`, `#pragma once`, `#ifdef/#ifndef/#else/
#endif`. A local text facility only — MUST NOT leak into imported
modules.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.02.01 — bindings

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md)

`let` / `let mut` with mandatory type annotations; immutable unless
`mut` (`F0208`); `malloc` results are owned and writable even through
immutable bindings.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.02.02 — functions and the entry point

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md)

`fn name(params) -> T { ... }`, `export fn` for external linkage,
`fn main()` returning `i32` to the C ABI with an implicit `return 0`
(main only). Definite-return analysis (`F0209`) for every non-void
function; `while (true)` counts as non-terminating.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — definite-return analysis made a hard error
  (`return;` in a non-void fn was previously a warning); the
  fall-off-the-end path now emits `unreachable` IR instead of a
  fabricated zero value.

### fsht-01:01-01.02.03 — parameter ownership modes

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md) · [ch. 06](../../spec/06-memory-ownership.md)

`owned` (callers must `give(...)`, callee may free — `F0303`) and
`borrowed` (read-only view, no free/give/writes on either side) as
signature-carried contracts checked at every call site.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.01 — `@pure`

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md)

A language-level contract (reads no memory, writes no memory) validated
by effect analysis; a violating `@pure` is a hard `F0304`, never a
bypass. `willreturn` requires a separate termination proof.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.02 — `@strictfp` / `@fastmath`

Status: normative. Spec: [ch. 13](../../spec/13-floating-point.md)

Per-function FP mode selection; `@strictfp` always wins over
`@fastmath`; the default is strict IEEE-754 per operation.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.03 — `@inline` / `@noinline`

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md)

Strong inlining hints as language attributes; cost/legality still apply.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.04 — `@hpc_strict`

Status: normative. Spec: [ch. 15](../../spec/15-diagnostics.md)

Per-function strict-performance mode: performance diagnostics become
errors for that function.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.05 — `@unsafe fn`

Status: normative. Spec: [ch. 06](../../spec/06-memory-ownership.md)

Whole-body unsafe scope: bounds checks omitted, ownership diagnostics
downgraded to warnings.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.03.06 — `@alias(a, b)`

Status: normative. Spec: [ch. 03](../../spec/03-declarations.md)

Caller promise that parameters `a`/`b` never overlap. `F0305` when the
checker proves aliasing without the declaration; `F0306` warning +
`noalias` suppression when the promise is broken. Lowered only when
every caller in the compilation unit is verified (LTO-aware lowering is
future work).

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the historical checker skipped the error for
  same-root arguments when the pair WAS declared `@alias` — the
  opposite of the spec. Fixed to match the spec exactly.

### fsht-01:01-01.04.01 — loops

Status: normative. Spec: [ch. 05](../../spec/05-statements.md)

`while`, C-style `for` (`i += E` / `i -= E` / `i = i ± E` steps) and
range `for` with `by` strides (`by -1` descending). Non-unit strides
warn `F0405`; IV written in body warns `F0406`.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — the C-style `for` step and `give(...)`
  call arguments never parsed in pre-audit builds; both are fixed and
  regression-covered.

### fsht-01:01-01.04.02 — `break` / `continue`

Status: normative. Spec: [ch. 05](../../spec/05-statements.md) · [ch. 12](../../spec/12-parfor.md)

Loop-exit statements binding to the innermost `for`/`while` (`F0213`
outside a loop); lane-local semantics inside `parfor`.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — constant-trip unrolling could drop `break`s;
  unroll/fusion/lane transforms now veto bodies containing early exits.

### fsht-01:01-01.04.03 — `match`

Status: normative. Spec: [ch. 05](../../spec/05-statements.md) · [ch. 08](../../spec/08-enums.md)

Tag dispatch with positional immutable payload bindings, `_` wildcard
and exhaustive coverage (`F0204`). A statement, not an expression.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-01.04.04 — `defer`

Status: normative. Spec: [ch. 05](../../spec/05-statements.md)

`defer <call>` runs at scope exit — every `return` and before every
`break`/`continue` leaving the scope.

History:
- fsht-01:01 — first standardised.
- fsht-01:01 (correction) — a second `return` in one function silently
  skipped defers on that path (a leak); defers now run on every exit
  path.

### fsht-04:01-01.05.01 — operator overloading

Status: proposed (not scheduled; must not delay fsht-02/03 work).

Natural mathematical types (complex numbers, vectors) would benefit from
operator overloading. Design sketch: overloaded operators resolve at
monomorphisation time once user traits exist (fsht-02:02), keeping
static dispatch.

### fsht-04:01-01.05.02 — method syntax

Status: proposed (not scheduled).

`x.foo(y)` sugar for `foo(&x, y)`-style free functions — more ergonomic
library APIs without an object system.

### fsht-04:01-01.06.01 — hygienic macros

Status: proposed (deliberately deferred).

General compile-time evaluation (fsht-02:03) comes first. The goal is
C/C++-level macros everyone knows — none of the exotic systems three
people will ever use.
