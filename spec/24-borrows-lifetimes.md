# 24 — Mutable borrows & lifetimes (normative in fsht-03:02)

> **Status.** Normative since fsht-03:02 (ratified 2026-11-19; first cut
> implemented in Penstock 0.1.0-INDEV). Registry entries
> [fsht-03:02-03.02.09](../registry/features/03-memory.md) and
> [fsht-03:02-03.02.10](../registry/features/03-memory.md). This
> increment matures the existing owned/borrowed model rather than
> redesigning it. Every fsht-02:03 program whose behaviour was *defined*
> remains valid with identical output; the programs it newly rejects
> (aliasing a growth-mutator against a live view, using a `String` after
> `string_free`, moving a container out from under a live view) were
> already outside defined behaviour — dangling views after reallocation
> or transfer — and are now diagnosed instead of silently misbehaving
> (`F0310`/`F0311`, chapter 15). The `usize` resolution and the String
> migration are clarifications recorded in their registry histories.
> Everything listed in §8 is a registry-tracked deferral, not a silent
> omission.

## 1. Borrow expressions (fsht-03:02-03.02.09)

```ebnf
borrow_expr ::= "&" [ "mut" ] place
place       ::= identifier { "." identifier | "[" expr "]" }
```

`&x` / `&mut x` become general expressions over places (locals,
parameters, field paths, indexed elements), yielding `*T`:

* `&mut x` — an **exclusive mutable borrow**: the callee or holder may
  write through it; no other borrow of `x` may be live while it is
  (§2).
* `&x` — a **shared borrow**: read-only access; many shared borrows may
  coexist.
* A borrow is *live* from its creation to its **last use** (a call it is
  passed to, an indexing read/write through it) — lexical, computed by
  the checker; storage is freed to re-borrow afterwards.
* The fsht-01/02 argument form `&v` passed to the mutation builtins
  (`vec_push(&v, …)`, `string_append(&s, …)`, the `io` handles of
  chapter 23 §4) is re-specified as the mutable-borrow spelling it
  always was semantically; `&mut v` is the explicit new spelling and
  MUST be accepted at every such call site. Both denote the same
  exclusive borrow — legacy programs are unaffected.
* `borrowed mut` parameters join the signature-carried modes
  (chapter 03):

```
param ::= [ "owned" | "borrowed" [ "mut" ] ] identifier ":" type
```

`borrowed mut p: *T` (or an aggregate: `borrowed mut v: Vec<T>`) gives
the callee exclusive write access; the call site MUST pass a mutable
borrow — `&mut place` (or `&place` where the legacy form applies) — and
a bare pointer value or a shared borrow is the existing passing-mode
mismatch `F0303`. Read-only `borrowed` parameters are unchanged.

```
fn fill(p: borrowed mut *i64, n: usize) {
    for (i in 0..n) { p[i] = (i as i64) * 2; }
}
fn main() {
    let mut buf: [i64; 4] = [0, 0, 0, 0];
    let r: *i64 = &mut buf[0];
    fill(r, 4);              // the borrow of buf extends through fill
    print_i64(buf[3]);        // 6 — re-read via the owner is fine
}
```

## 2. Exclusivity — `F0310`

At any program point, a place's borrows obey **one writer or many
readers**; violations are the compile-time error `F0310` (the safety
table's new family member, chapter 15):

* two live mutable borrows of the same place (including two `borrowed
  mut` aliases of one argument, and `f(&mut x, &mut x)`);
* a mutable borrow created while a **live shared borrow** of the same
  place exists (or vice versa: a shared borrow *used* while a mutable
  borrow is live).

**Views are shared borrows.** A `Span<T>`/`str` derived from a place
(`v[lo..hi]`, `vec_slice`, `str_of(&s)`, `span(arr)`, slicing a
borrowed parameter further) borrows that place from creation to last
use. Growth-mutators (`vec_push`, `vec_insert`, `vec_resize`,
`vec_reserve`, `vec_truncate`, `vec_clear`, `string_append`), release
(`vec_free`, `string_free`, chapter 23's `reader_close`), moves
(`let b = a;`, by-value arguments, `return v;`) and `give` therefore
conflict with a live view of the same storage (`F0310`): reallocation
or transfer would dangle it.

* **In-place element writes do not invalidate views.** `v[i] = e` and
  field writes through the owner write the existing storage; no
  reallocation happens, so views taken before remain valid and
  readable after. This is the ratified fsht-02:01 lvalue rule, now
  stated within the borrowing discipline.
* Mutable borrows inside a **dispatched** `parfor` body are rejected
  (`F0307`, the existing container rule generalised): shared reads
  through views remain the supported parallel shape.

## 3. Lifetime / escape analysis refinement — `F0311` (fsht-03:02-03.02.10)

A borrow or view MUST NOT outlive its storage; violations are `F0311`
(the precise lifetime diagnostic; the fsht-02:01 rejection of
"returning a borrowed view of a local container" was reclassified from
the blunt `F0301` to this family — same rejection, stated as the rule
it always implemented, per the ID-split rule of chapter 15):

* returning `&mut local`, or a view of a local container / local
  `String`, from a function (`F0311`: the drop at exit dangles it);
  returning views of **`borrowed` parameters** stays legal — the
  signature carries that the caller's storage outlives the callee
  (this is what the fsht-02:01 permission "views of parameters stay
  legal" meant: the *borrowed-parameter* case; views of by-value
  container parameters were already undefined — the callee-exit drop
  dangles them — and are diagnosed now);
* storing a borrow of function-local storage into a global, a heap
  object that outlives it, or through a pointer whose root outlives
  the source (`F0311`; the static-root proofs and `F0926`/`F0927` of
  data stacks, chapter 06, continue to govern `stack_alloc`);
* an interprocedural non-escape summary (the chapter 06 mechanism)
  covers callees: passing `&mut x` to a function that provably does not
  let it escape keeps the borrow's lifetime exactly the call;
* escape of borrows into fn values or extern calls is rejected unless
  the callee's signature carries an outliving-root contract.

## 4. The `String` migration (fsht-03:02)

`String` joins the ownership-tracked container model of chapter 20
(the migration fsht-02:01 deferred to exactly this increment, together
with the lifetime analysis that makes it safe):

* **Auto-drop.** Every owned `String` binding drops at its scope's
  closing brace (reverse declaration order, after defers), on every
  exit path; by-value `String` parameters drop at callee exit;
  `break`/`continue`/`return` flush them. Drops are idempotent.
* **Moves.** `let b = a;`, by-value arguments, `return s;` transfer
  ownership; the source binding is invalidated (use-after-move
  `F0301`); the transfer nulls the source's data pointer.
* **Manual release.** `string_free(&s)` pre-empts the scope-exit drop
  and invalidates the binding — fsht-01/02 programs that freed
  explicitly keep working unchanged. Double free, use-after-free and
  `give()` of a non-owned `String` are `F0301`. A never-freed `String`
  can no longer leak (the leak diagnostic does not apply; chapter 06's
  "documented gap" paragraph is closed).
* **Views.** `str_of(&s)` is a shared borrow of `s` (§2): legal to
  read, print, slice, pass — and diagnosed (`F0310`) if `s` grows or
  is moved/freed while the view is live. Views that would escape
  their storage are `F0311` (§3) — this is the analysis fsht-02:01
  waited for before migrating.
* **New builtins.** `string_clone(&s) -> String` (owned deep copy —
  needed by container cloning, §5) and `string_clear(&s)`;
  `str_cat`, `string_from`, `fmt_i64`, `fmt_f64`, `string_new`,
  `string_append`, `str_eq`, `str_to_cstr` keep their exact
  signatures. `String` remains `{ data: *u8, len, cap }` — layout
  unchanged, discipline upgraded.
* Programs that relied on the untracked gap (use-after-`string_free`,
  aliasing growth against a live view) were undefined at runtime in
  every prior version; fsht-03:02 diagnoses them.

## 5. Drop elaboration through user shapes

The fsht-02:01 restrictions "owned containers stay at value level"
and "owning element types are rejected" are lifted (tracked by
02.09.01/02.09.02 for lifting; the escape analysis is the enabling
mechanism):

* A `Vec<T>` may now appear as a **struct field**, an **enum
  payload**, or a **fixed-array element**; `Vec<String>`,
  `Vec<Vec<T>>` and nested combinations are accepted. `String` fields
  likewise.
* Scope-exit drops walk the shape **innermost-first**: each owning
  element drops, then the enclosing container's buffer frees. Moves of
  user shapes transfer every inner ownership atomically (a shape is
  one unit — partial invalidation does not exist).
* `vec_clone` of owning elements performs an element-wise deep copy
  (`string_clone` for `String` elements, recursive clone for nested
  vectors); `vec_from_span`/`vec_from_array` of owning element types
  are type errors (`F0201`) — the bulk-copy deferral stands (§8).
* A struct with owning fields used as a plain by-value parameter is a
  whole-shape move (chapter 04's copy semantics apply only to
  non-owning shapes — a POD struct containing a container no longer
  copies silently; copying is `vec_clone`-style and explicit).

## 6. The integer representation model (`usize` resolved)

The open question of registry 02.01.05 is closed: **`usize` is
permanently the fixed 64-bit unsigned integer on every target**,
identical to `u64` — including the 32-bit WebAssembly targets of
chapter 25. The deliberate divergence from C's target-pointer-sized
`size_t` buys uniform numeric semantics across the target matrix
(indices and lengths behave the same everywhere; a wasm32 heap index
fits trivially). `sizeof`/`alignof` and `usize` therefore never change
with `--target`. No fsht program changes meaning; the migration note
is: none required. The decision is recorded in 02.01.05's history.

## 7. Conformance requirements

The borrow-expression grammar with shared/exclusive semantics and
last-use lifetimes, the `F0310` exclusivity table, the view-as-shared-
borrow rule with the in-place-write carve-out, `F0311`'s escape rules
for borrows/views, the ownership-tracked `String` lifecycle (auto-drop,
moves, pre-emptive `string_free`, `string_clone`), drop elaboration
through user shapes, and the fixed-64-bit `usize` are MUST-level. The
interprocedural summary mechanism is the reference implementation's
HOW and SHOULD-level elsewhere (the WHAT — which programs are
rejected — is MUST-level either way).

## 8. Deferrals (registry-tracked)

* Bulk-copy container APIs (`vec_from_span` of owning elements,
  `vec_extend`); custom allocators.
* Borrow-elaboration through fn values stored in structs (fn pointers
  keep chapter 17's rules).
* Multiple mutable borrows of **disjoint** places proven by a
  path-sensitive analysis (`&mut a[0]` alongside `&mut a[1]`): today
  one mutable borrow per storage root at a time.
* A `lifetime`-spelled surface (named regions): the current model is
  inferred, never written.
