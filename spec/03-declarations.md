# 03 — Declarations (normative in fsht-01:01)

## Bindings

```ebnf
binding ::= "let" [ "mut" ] identifier ":" type "=" expr ";"
```

`let x: T = e;` declares an immutable binding; `let mut` a mutable one.
A binding is immutable unless `mut` is written; assignment through an
immutable binding is `F0208`. `malloc` results are *owned*: writable even
through an immutable binding (chapter 06).

## Functions

```ebnf
function_decl ::= [ attribute { attribute } ]
                  [ "export" ] "fn" identifier "(" [ params ] ")"
                  [ "->" type ] block
attribute    ::= "@" identifier [ "(" args ")" ]
params       ::= param { "," param }
param        ::= [ "owned" | "borrowed" ] identifier ":" type
```

`fn main()` is the entry point; it returns `i32` to the C ABI and an
implicit `return 0` is appended. Every other non-void function MUST
return a value on every path (`F0209`; `while (true)` counts as
non-terminating). `export fn` keeps its exact C symbol (external linkage).

### Parameter ownership modes (fsht-01:01-03.02.01)

* `owned data: *T` — ownership transfers IN: every caller MUST pass
  `give(...)` (`F0303` otherwise); the callee may `free` it.
* `borrowed s: Span<T>` — read-only view: no `free`, no `give`, no writes
  through the parameter; callers may not give it away either.
* unannotated — the default contract of chapter 06 applies.

### Function attributes — language-level contracts (fsht-01:01-01.03.*)

Attributes are contracts, not optimiser hints; violating one is a compile
error (or, for `@alias`, an `F0306` warning plus suppression of the
corresponding LLVM attribute).

| attribute | promise | enforcement |
|---|---|---|
| `@pure` | reads no memory, writes no memory | validated by effect analysis; a violating `@pure` is a hard `F0304` |
| `@strictfp` | strict IEEE-754 for this function (chapter 13) | selects the strict rounding-environment group |
| `@fastmath` | opt into relaxed FP for this function | only with chapter 13's global rules; `@strictfp` wins over `@fastmath` on the same function |
| `@inline` | aggressive inlining requested | strongest alwaysinline hint; cost/legality still apply |
| `@noinline` | forbid inlining | useful for differential benchmarking |
| `@hpc_strict` | performance diagnostics are errors for this fn | per-function strict mode (chapter 15) |
| `@unsafe` | whole body is an unsafe scope | chapter 06 |
| `@alias(a, b)` | callers always pass non-overlapping `a`, `b` | `F0305` when the checker proves overlap without the declaration; `F0306` (warning + LLVM `noalias` suppressed for that pair) when the promise is broken; lowered only when every caller in the compilation unit is verified |
| `@reproducible` | (on a `parfor`) deterministic reduction — chapter 12 |
| `@vectorize` | (on a loop) request vectorisation — a hint, not proof (chapter 19) |
| `@test` | zero-arg void test-runner entry (chapter 19) |

## Struct, enum and module declarations

```ebnf
struct_decl ::= "struct" identifier [ "align" "(" int ")" ] "{" fields "}"
fields      ::= field { "," field }
field       ::= identifier ":" type
enum_decl   ::= "enum" identifier "{" variant { "," variant } "}"
variant     ::= identifier [ "(" type { "," type } ")" ]
module_decl ::= "module" identifier ";"
import_decl ::= "import" identifier ";"
```

See chapters 04, 08 and 16. Generic declarations take `<` param `[,`
param `]` `>` lists with optional `: constraint` bounds (chapter 09).

## Conformance requirements

* Attributes are MUST-level contracts with the enforcement semantics in
  the table; an implementation that silently ignores a violated `@pure`
  is non-conforming.
* The implicit `return 0` exists ONLY for `main`.
* Unknown or conflicting attributes are `F0105`.
