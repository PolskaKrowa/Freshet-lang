# 04 — parallelism features (fsht-03:03)

### fsht-01:01-04.01.01 — `parfor` execution model

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

Chunked iteration over `[lo, hi)` on a persistent work-stealing worker
pool (`FRT_THREADS`, calling thread participates); writes to captured
scalars race → `F0307`; pointer/SoA writes are the intended pattern.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-04.02.01 — reductions

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

`reduction(ops: acc)` with `+ - * min max`; per-chunk registers
combined after the region; init-value diagnostics `F0308`/`F0309`; float
reductions use fast-math unless restricted.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-04.02.03 — `@reproducible` reductions

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

Deterministic, thread-count-independent reductions: fixed block
partitioning (chunk clause, else 8192), strict IEEE-754 partials,
ascending-order combination — bitwise identical for any `FRT_THREADS`,
affinity or scheduler on the same binary.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-04.03.01 — nesting (collapse / work-stealing)

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

Rectangular nesting collapses (inner serialised, vectorises); dynamic
nesting makes inner chunks stealable tasks — no thread blocks on a
region, so nesting cannot deadlock.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-04.03.02 — scheduling clauses

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

`threads:n`, `chunk:n`, `affinity:close|spread`, `collapse:k`.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-04.03.03 — lane-local `break`/`continue`

Status: normative. Spec: [ch. 12](../../spec/12-parfor.md)

`continue` skips the current iteration; `break` stops the current
chunk's remaining iterations only — neither terminates the region;
reduction accumulators observed by a chunk that broke early still
combine.

History:
- fsht-01:01 — first standardised (lifts the historical `F0106`
  limitation).

### fsht-01:01-04.03.05 — worker-pool environment

Status: normative (runtime surface). Spec: [ch. 19](../../spec/19-toolchain.md)

`FRT_THREADS`, `FRT_AFFINITY`, `FRT_CHUNK`, `FRT_SERIAL_CUTOFF`,
`FRT_SMT_INTERLEAVE`, `freshet.threads()`.

History:
- fsht-01:01 — first standardised.

### fsht-04:01-04.04.01 — iterators

Status: proposed (not scheduled).

Convenient collection processing over the container set of fsht-02:01;
must compose with parfor's data-parallel model rather than replace it.

### GPU programming — deliberately deferred

Status: deferred (no version).

Build a reliable CPU numerical ecosystem first. GPU support needs its
own execution model and memory abstractions; the registry records the
decision so it is not silently forgotten.

### MPI / distributed computing — deliberately deferred

Status: deferred (no version).

Very valuable eventually; the first distributed numerical libraries can
be separate runtime integrations rather than language surface.
