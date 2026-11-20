# 06 — Memory & ownership (normative in fsht-01:01)

## Allocation

```ebnf
malloc_builtin ::= "malloc" "(" type "," expr ")"
free_builtin   ::= "free" "(" expr ")"
give_stmt      ::= "give" "(" expr ")"
memcpy_builtin ::= "memcpy" "(" expr "," expr "," expr ")"
memset_builtin ::= "memset" "(" expr "," int "," expr ")"
```

* `let a: *f64 = malloc(f64, n)` — aligned, **uninitialised** storage for
  `n` elements; the count is a `usize` expression.
* `free(a)` releases it.
* `give(a)` transfers ownership into an `owned` callee parameter (chapter
  03); `give(...)` may appear as a call argument.
* `memcpy`/`memset` are the raw byte primitives.

## The ownership state machine (fsht-01:01-03.01.02)

`malloc` results are *owned*: writable even through an immutable
binding, and tracked through the states **Alive / MaybeFreed / Freed /
Moved**. The following are compile-time errors under `F0301`:

* leak — a `malloc` never matched by a visible `free`, a `defer free`, or
  a `give` transfer;
* double free;
* use-after-free;
* use-after-give;
* `give` of a non-owned value.

Suspicious-but-unprovable ownership operations are `F0302` warnings.

`String` allocations were a **documented gap** through fsht-02:03 — the
ownership state machine did not track them. The fsht-03:02 update
([chapter 24 §4](24-borrows-lifetimes.md)) closed the gap: `String` is
ownership-tracked (auto-drop, move invalidation, pre-emptive
`string_free`), and `str_of(&s)` views live under the borrow
discipline (registry `fsht-03:02-03.02.09`/`03.02.10`). Containers
joined the checked model earlier, in fsht-02:01 (`Vec<T>`,
[chapter 20](20-dynamic-collections.md), registry
`fsht-02:01-02.09.01`).

## Borrowing: `owned` and `borrowed` parameters

The `give(p)` call-site marker says *what* is transferred; the parameter
declaration says *why* (chapter 03): `owned` moves ownership IN (callee
may free; every caller must `give` — `F0303`); `borrowed` is a read-only
view (no free, no give, no writes through it, on either side). This is
the fsht-01:01 answer to borrow checking: explicit, signature-carried,
checked at every call site. Since fsht-03:02 the model is matured by
general `&`/`&mut` borrow expressions with exclusivity checking and
the `borrowed mut` mode — [chapter 24](24-borrows-lifetimes.md) —
without redesigning this surface.

## `unsafe` scopes

```ebnf
unsafe_block ::= "unsafe" block | "@unsafe" fn
```

`unsafe { ... }` (or `@unsafe fn`) marks code whose correctness the
compiler cannot prove: Span/array bounds checks are omitted inside it,
and ownership diagnostics that fire within it are downgraded to
warnings. The safe path stays the default; the escape hatch is explicit
and greppable. A conforming compiler MUST provide the safe/unsafe split
with exactly this shape.

## Machine intrinsics

`freshet.prefetch_r(p)`, `freshet.prefetch_w(p)`, `freshet.clflush(p)`,
`freshet.pause()` map to machine instructions; they are memory-effectful
and never pure.

## Data stacks (`stack_alloc`) (fsht-01:01-03.03.01)

`stack_alloc(T, n)` allocates from the function's per-thread bump-pointer
**data stack**; the allocation dies when its scope ends (watermark
restore in reverse declaration order on every exit path, after defers).
The checker proves scope ownership with static-root lifetime proofs:

* `free`, `give`, returning, or an owned argument on data-stack memory
  is `F0926`;
* storing it into a global or through a pointer whose root outlives the
  source's is `F0926` — stores into lexically-nested destinations are
  proven safe;
* passing it to a callee is judged by an interprocedural non-escape
  summary;
* `stack_alloc` must be the direct initializer of a `let` (`F0927`);
  stack-using functions may not be exported or taken as fn values;
* stack memory must not be referenced inside a **dispatched** `parfor`
  body (`F0926` region capture) — collapsed inner regions are fine.

Data stacks are an opt-in compiler capability (`--stacks` reporting,
`FRT_DSTK_RESERVE` sizing); the *language* surface above is what the
standard fixes.

## Conformance requirements

The malloc/free/give state machine with `F0301` coverage, the
owned/borrowed call-site enforcement, and the `unsafe` downgrade rules
are MUST-level. Machine intrinsics are SHOULD-level (the reference
implementation lowers them directly).
