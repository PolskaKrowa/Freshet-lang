# Subset taxonomy (fsht-01:01)

The `aa.bb` part of a feature identifier: `aa` names the major subset,
`bb` the minor subset, `cc` the exact feature. This table is normative
for identifier allocation.

## `aa` — major subsets

| aa | subset |
|---|---|
| 01 | core language — lexical structure, declarations, attributes, control flow |
| 02 | data types — scalars, structs, arrays, spans, SoA, strings, enums, Option/Result |
| 03 | memory — allocation, ownership, unsafe, data stacks |
| 04 | parallelism — parfor execution, reductions, scheduling |
| 05 | I/O — print/stdio, formatting, files, the `fsh` module |
| 06 | generics — templates, constraints (and, later, traits) |
| 07 | modules & FFI — imports, projects, extern fn, function pointers |
| 08 | numeric semantics — integer and floating-point rules |
| 09 | diagnostics — the F-code registry, severity policy, analysis passes |
| 10 | toolchain & targets — backend matrix, runtime, cross-targeting, tooling |

## `bb` — minor subsets (allocated per major subset; gaps reserved)

| aa | bb | minor subset |
|---|---|---|
| 01 | 01 | lexical: tokens, literals, preprocessor |
| 01 | 02 | declarations: bindings, functions, parameters |
| 01 | 03 | function attributes |
| 01 | 04 | control flow statements |
| 01 | 05 | (reserved) operator surface, future: overloading, methods |
| 01 | 06 | (reserved) future: hygienic macros |
| 02 | 01 | scalar types |
| 02 | 02 | structs |
| 02 | 03 | fixed-size arrays |
| 02 | 04 | spans |
| 02 | 05 | SoA arrays |
| 02 | 06 | strings (`str`, `String`) |
| 02 | 07 | Option / Result |
| 02 | 08 | enums and tagged unions |
| 02 | 09 | (reserved) dynamic containers: Vec, Slice, SliceMut, ByteBuffer |
| 03 | 01 | allocation primitives |
| 03 | 02 | ownership & borrowing |
| 03 | 03 | data stacks |
| 04 | 01 | execution model |
| 04 | 02 | reductions |
| 04 | 03 | scheduling (threads, chunk, affinity, nesting) |
| 04 | 04 | (reserved) iterators |
| 05 | 01 | print/stdio |
| 05 | 02 | formatting |
| 05 | 03 | the `fsh` module |
| 05 | 04 | (reserved) parsing (parse_i64/parse_f64) |
| 05 | 05 | (reserved) streaming I/O |
| 05 | 06 | (reserved) library decomposition core/alloc/... |
| 05 | 07 | (reserved) async I/O |
| 06 | 01 | monomorphisation |
| 06 | 02 | (reserved) user-defined traits |
| 06 | 03 | (reserved) const generics |
| 06 | 04 | (reserved) closures |
| 07 | 01 | modules & project manifest |
| 07 | 02 | function pointers & callbacks |
| 07 | 03 | (reserved) variadic extern fn |
| 07 | 04 | (reserved) C header generation |
| 08 | 01 | integer semantics |
| 08 | 02 | floating-point semantics |
| 09 | 01 | severity policy |
| 09 | 02 | the F-code registry |
| 09 | 03 | (reserved) numerical-analysis diagnostics |
| 09 | 04 | (reserved) memory/allocation diagnostics |
| 10 | 01 | backend matrix |
| 10 | 02 | runtime |
| 10 | 03 | (reserved) target-aware runtime |
| 10 | 04 | tooling (test/fmt/lint/LSP/debug) |
| 10 | 05 | (reserved) package management |
| 10 | 06 | (reserved) numerical profiling report |

`cc` values are allocated per `aa.bb` in the order features are
accepted; they are permanent.
