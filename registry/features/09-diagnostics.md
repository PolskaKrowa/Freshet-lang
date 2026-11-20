# 09 — diagnostics features (fsht-03:03)

### fsht-01:01-09.01.01 — correctness/performance severity policy

Status: normative. Spec: [ch. 15](../../spec/15-diagnostics.md)

Correctness diagnostics are always errors; performance diagnostics are
warnings by default; `--strict-performance` / `@hpc_strict` restore the
hard gates; the ID names the rule, not its severity.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-09.02.01 — the `Fnnnn` registry

Status: normative. Spec: [ch. 15](../../spec/15-diagnostics.md)

Stable IDs `F0001`–`F0929` (driver/project, syntax, semantics, safety,
performance, optimisation remarks), never reused or renumbered;
splits create new IDs; `--explain` prints the entry and long-form page.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-09.02.02 — performance diagnostics family

Status: normative. Spec: [ch. 15](../../spec/15-diagnostics.md)

`F0401`–`F0408`: non-power-of-2/runtime division, cache-line strides,
field straddling, loop strides, IV mutation, layout padding, AoS→SoA
advice. The cache-layout analysis behind them (efficiency model, layout
simulation, straddle detection) is specified in the chapters.

History:
- fsht-01:01 — first standardised.

### fsht-03:04-09.03.01 — compile-time numerical guarantees

Status: proposed (compiler capability; target fsht-03:04). Spec: —

Detect potential numerical instability: warn about catastrophic
cancellation, suspicious accumulation of floating-point error, possible
overflow in intermediate calculations; explicit numerical accuracy
diagnostics. These are warnings and analysis tools — NOT claims that
the compiler can prove arbitrary numerical algorithms correct. Registry
records the boundary deliberately.

History:
- fsht-03:04 (proposed) — first proposed for the Penstock compiler
  intelligence roadmap.

### fsht-03:04-09.04.01 — memory and allocation diagnostics

Status: proposed (compiler capability; target fsht-03:04). Spec: —

Building on the existing memory-layout analysis: excessive allocations
in hot loops, unnecessary copying of large arrays, unnecessary
AoS↔SoA conversions, poor memory-access locality, excessive temporary
buffers, cache-unfriendly data structures.

History:
- fsht-03:04 (proposed) — first proposed.

### fsht-03:04-10.06.01 — numerical profiling report

Status: proposed (compiler capability; target fsht-03:04). Spec: —

A report per function identifying CPU time split, memory vs
floating-point operation share, estimated bandwidth, L1/L2 cache
misses, vectorised vs scalar loops, active workers and parallel
regions. Measurements that require hardware performance counters are
clearly separated from static compiler estimates — measured data is
never presented as an estimate and vice versa. This capability, made
honest, is what makes a compiler a genuinely interesting tool for
diagnosing numerical software.

History:
- fsht-03:04 (proposed) — first proposed.
