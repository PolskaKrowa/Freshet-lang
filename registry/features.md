# Feature index (fsht-01:01)

Master table of every registry entry. Full entries (rules, histories,
update references) live in the per-subset files.

## Normative in fsht-01:01

| identifier | title | subset file |
|---|---|---|
| fsht-01:01-01.01.01 | lexical structure | [01](features/01-core.md) |
| fsht-01:01-01.01.02 | preprocessor | [01](features/01-core.md) |
| fsht-01:01-01.02.01 | bindings | [01](features/01-core.md) |
| fsht-01:01-01.02.02 | functions and the entry point | [01](features/01-core.md) |
| fsht-01:01-01.02.03 | parameter ownership modes | [01](features/01-core.md) |
| fsht-01:01-01.03.01 | `@pure` | [01](features/01-core.md) |
| fsht-01:01-01.03.02 | `@strictfp` / `@fastmath` | [01](features/01-core.md) |
| fsht-01:01-01.03.03 | `@inline` / `@noinline` | [01](features/01-core.md) |
| fsht-01:01-01.03.04 | `@hpc_strict` | [01](features/01-core.md) |
| fsht-01:01-01.03.05 | `@unsafe fn` | [01](features/01-core.md) |
| fsht-01:01-01.03.06 | `@alias(a, b)` | [01](features/01-core.md) |
| fsht-01:01-01.04.01 | loops | [01](features/01-core.md) |
| fsht-01:01-01.04.02 | `break` / `continue` | [01](features/01-core.md) |
| fsht-01:01-01.04.03 | `match` | [01](features/01-core.md) |
| fsht-01:01-01.04.04 | `defer` | [01](features/01-core.md) |
| fsht-01:01-02.01.01 | scalar integer types | [02](features/02-data-types.md) |
| fsht-01:01-02.01.02 | floating-point types | [02](features/02-data-types.md) |
| fsht-01:01-02.01.03 | `bool` | [02](features/02-data-types.md) |
| fsht-01:01-02.01.05 | `usize` representation | [02](features/02-data-types.md) |
| fsht-01:01-02.02.01 | structs and C layout | [02](features/02-data-types.md) |
| fsht-01:01-02.02.03 | by-value struct parameters | [02](features/02-data-types.md) |
| fsht-01:01-02.03.01 | fixed-size arrays `[T; N]` | [02](features/02-data-types.md) |
| fsht-01:01-02.04.01 | spans `Span<T>` | [02](features/02-data-types.md) |
| fsht-01:01-02.05.01 | SoA arrays `soa(S)` | [02](features/02-data-types.md) |
| fsht-01:01-02.06.01 | `String` | [02](features/02-data-types.md) |
| fsht-01:01-02.06.02 | `str` | [02](features/02-data-types.md) |
| fsht-01:01-02.07.01 | `Option<T>` / `Result<T, E>` | [02](features/02-data-types.md) |
| fsht-01:01-02.07.02 | the `?` operator | [02](features/02-data-types.md) |
| fsht-01:01-02.08.01 | enums and tagged unions | [02](features/02-data-types.md) |
| fsht-01:01-03.01.01 | `malloc` / `free` | [03](features/03-memory.md) |
| fsht-01:01-03.01.02 | the ownership state machine | [03](features/03-memory.md) |
| fsht-01:01-03.01.03 | `give` transfer | [03](features/03-memory.md) |
| fsht-01:01-03.02.01 | `owned` / `borrowed` parameters | [03](features/03-memory.md) |
| fsht-01:01-03.02.02 | `unsafe` scopes | [03](features/03-memory.md) |
| fsht-01:01-03.03.01 | data stacks (`stack_alloc`) | [03](features/03-memory.md) |
| fsht-01:01-04.01.01 | `parfor` execution model | [04](features/04-parallelism.md) |
| fsht-01:01-04.02.01 | reductions | [04](features/04-parallelism.md) |
| fsht-01:01-04.02.03 | `@reproducible` reductions | [04](features/04-parallelism.md) |
| fsht-01:01-04.03.01 | nesting (collapse / work-stealing) | [04](features/04-parallelism.md) |
| fsht-01:01-04.03.02 | scheduling clauses | [04](features/04-parallelism.md) |
| fsht-01:01-04.03.03 | lane-local `break`/`continue` | [04](features/04-parallelism.md) |
| fsht-01:01-04.03.05 | worker-pool environment | [04](features/04-parallelism.md) |
| fsht-01:01-05.01.01 | print builtins | [05](features/05-io.md) |
| fsht-01:01-05.02.01 | formatting | [05](features/05-io.md) |
| fsht-01:01-05.03.01 | the `fsh` module | [05](features/05-io.md) |
| fsht-01:01-06.01.01 | monomorphised generics | [06](features/06-generics.md) |
| fsht-01:01-06.01.02 | built-in constraints | [06](features/06-generics.md) |
| fsht-01:01-07.01.01 | modules and visibility | [07](features/07-modules-ffi.md) |
| fsht-01:01-07.01.02 | multi-file compilation | [07](features/07-modules-ffi.md) |
| fsht-01:01-07.01.03 | project manifest | [07](features/07-modules-ffi.md) |
| fsht-01:01-07.02.01 | function pointers | [07](features/07-modules-ffi.md) |
| fsht-01:01-07.02.02 | C callbacks and extern linkage | [07](features/07-modules-ffi.md) |
| fsht-01:01-08.01.01 | integer wrapping arithmetic | [08](features/08-numeric-semantics.md) |
| fsht-01:01-08.01.02 | division and remainder | [08](features/08-numeric-semantics.md) |
| fsht-01:01-08.01.03 | shifts | [08](features/08-numeric-semantics.md) |
| fsht-01:01-08.02.01 | the strict floating-point default | [08](features/08-numeric-semantics.md) |
| fsht-01:01-08.02.02 | transcendental lowering policy | [08](features/08-numeric-semantics.md) |
| fsht-01:01-09.01.01 | severity policy | [09](features/09-diagnostics.md) |
| fsht-01:01-09.02.01 | the `Fnnnn` registry | [09](features/09-diagnostics.md) |
| fsht-01:01-09.02.02 | performance diagnostics family | [09](features/09-diagnostics.md) |
| fsht-01:01-10.01.01 | the LLVM backend matrix | [10](features/10-toolchain.md) |
| fsht-01:01-10.02.01 | the Freshet runtime | [10](features/10-toolchain.md) |
| fsht-01:01-10.03.01 | `--target` cross-targeting | [10](features/10-toolchain.md) |
| fsht-01:01-10.04.01 | tooling | [10](features/10-toolchain.md) |
| fsht-01:01-10.04.02 | observability | [10](features/10-toolchain.md) |

## Accepted (target versions) — the fsht-02/03 roadmap

| identifier | title | target |
|---|---|---|
| fsht-02:01-02.09.01 | dynamic collections (Vec/Slice/SliceMut/ByteBuffer/String) | fsht-02:01 |
| fsht-02:01-02.09.02 | container move semantics | fsht-02:01 |
| fsht-02:02-06.02.01 | user-defined traits (static dispatch) | fsht-02:02 |
| fsht-02:03-06.03.01 | const generics + const fn | fsht-02:03 |
| fsht-03:01-05.04.01 | numeric text parsing | fsht-03:01 |
| fsht-03:01-05.05.01 | streaming I/O with Result integration | fsht-03:01 |
| fsht-03:01-05.06.01 | standard-library decomposition | fsht-03:01 |
| fsht-03:01-08.01.04 | checked/saturating/wrapping variants | fsht-03:01 |
| fsht-03:02-03.02.09 | mutable borrowing with exclusivity | fsht-03:02 |
| fsht-03:02-03.02.10 | lifetime/escape analysis refinement | fsht-03:02 |
| fsht-03:03-10.03.02 | portable target-aware runtime | fsht-03:03 |

## Proposed (not scheduled)

fsht-04:01-01.05.01 operator overloading · fsht-04:01-01.05.02 method
syntax · fsht-04:01-01.06.01 hygienic macros · fsht-04:01-04.04.01
iterators · fsht-04:01-05.07.01 async/await · fsht-04:01-06.04.01
closures · fsht-04:01-07.03.01 variadic extern fn ·
fsht-04:01-07.04.01 C header generation · fsht-03:04-09.03.01 numerical
guarantees · fsht-03:04-09.04.01 allocation diagnostics ·
fsht-03:04-10.06.01 numerical profiling report.

## Deliberately deferred / rejected

GPU programming (deferred) · MPI/distributed (deferred) · package
manager (deferred to fsht-04:02; custom webserver owned by the
maintainer) · large OO class system (rejected) · exotic macro language
(rejected: general compile-time evaluation first, C/C++-level macros
only).

## Count

64 normative entries, 11 accepted, 11 proposed, 5 deferred/rejected —
the complete fsht-01:01 ledger.
