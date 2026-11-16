# 12 — Parallelism: `parfor` (normative in fsht-01:01)

## Grammar

```ebnf
parfor_stmt ::= [ "@reproducible" ] "parfor" "(" identifier "in"
                 expr ".." expr ")" [ clauses ] block
clauses     ::= "[" clause { "," clause } "]"
clause      ::= reduction | "threads" ":" int | "chunk" ":" int
              | affinity | "collapse" ":" int
reduction   ::= "reduction" "(" op ":" identifier ")"
op          ::= "+" | "-" | "*" | "min" | "max"
affinity    ::= "affinity" ":" ( "close" | "spread" )
```

## Execution model (fsht-01:01-04.01.01)

* The iteration space `[lo, hi)` is split into chunks executed by a
  persistent work-stealing worker pool (size `FRT_THREADS`, default all
  cores); the calling thread participates. Step is ±1 — `by -1` iterates
  descending internally.
* Writes to captured scalars/structs race → **`F0307`**, unless the
  accumulator is a declared reduction. Writes through pointers
  (`a[i] = ...`, `a[i].f = ...`) and through `soa` handles are the
  intended data-parallel pattern and are allowed (stride quality is
  `F0403`'s business).
* Indirect calls (fn pointers) inside a `parfor` body are `F0307`
  (unknown effects).

## Reductions (fsht-01:01-04.02.01)

`reduction(+:acc)` makes the accumulator a per-chunk register value;
chunks combine with the operator after the region. `+`/`-`
accumulators SHOULD be initialised to 0 (`F0308`); `*` MUST be 1
(`F0309`); `min`/`max` are supported. Float reductions use fast-math so
the vectoriser may reorder them — `@strictfp` on the enclosing function
or `@reproducible` on the region buys back determinism.

## `@reproducible` (fsht-01:01-04.02.03)

```
@reproducible parfor (i in 0..n) [reduction(+: acc)] { ... }
```

requests a **deterministic** parallel reduction: the range is partitioned
into fixed blocks (the `chunk:` clause, else 8192) independent of the
worker count; every partial is computed in strict IEEE-754 order (the
accumulator chain is never reassociated or vectorised); partials combine
in ascending block order with strict-FP adds. The result is
bitwise-identical for any `FRT_THREADS` / affinity / scheduler on the same
binary. `min`/`max` are included. Without the flag, reductions may use
fast-math reassociation and thread-count-derived chunking — faster, but
the float result can differ between runs.

## Nesting

* **Rectangular nesting** (inner bounds independent of the outer var, no
  conflicting reductions): the compiler collapses — the inner loop is
  serialised inside the outer chunk function, the whole nested space runs
  in one parallel region and the inner loop vectorises.
* **Dynamic nesting**: the chunk function itself dispatches; inner
  chunks are stealable tasks in the global pool. The caller helps until
  its region drains — no thread ever blocks on a region, so nesting
  cannot deadlock.

## `break`/`continue` inside `parfor` (lane-local)

`continue;` skips the rest of the current iteration; `break;` stops the
**current chunk's** remaining iterations — other chunks are unaffected.
Neither terminates the whole region: iterations already dispatched
elsewhere still run. Reduction accumulators observed by a chunk that
broke early still combine. Use a flag + `if` when global termination is
intended. Nested `for`/`while` loops inside the body bind
`break`/`continue` to themselves as usual.

## Clauses and intrinsics

`threads:8`, `chunk:4096`, `affinity:close` (large contiguous ranges,
cache-friendly) and `affinity:spread` (~8T small interleaved ranges
spreading hot lines across cores) are advisory scheduling knobs.
`freshet.threads()` reports the pool size.

## Conformance requirements

The chunked execution model, the `F0307` race rejection for captured
scalar writes, reduction semantics with their init-value diagnostics, and
`@reproducible`'s bitwise thread-count independence are MUST-level.
Lane-local `break`/`continue` is MUST-level. Affinity semantics are
SHOULD-level (best-effort placement). Parallelism is limited to `parfor`
data parallelism in fsht-01:01 — task-level concurrency, atomics and
synchronisation primitives are future work recorded in the registry.
