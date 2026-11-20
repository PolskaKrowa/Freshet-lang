# 23 — The expanded standard library (normative in fsht-03:01)

> **Status.** Normative since fsht-03:01 (ratified 2026-11-19; first cut
> implemented in Penstock 0.1.0-INDEV). This chapter is a pure extension
> of fsht-02:03 — the functions, modules and prelude enums defined here
> did not exist before fsht-03:01, so no earlier program changes meaning.
> Registry entries
> [fsht-03:01-05.04.01](../registry/features/05-io.md),
> [fsht-03:01-05.05.01](../registry/features/05-io.md),
> [fsht-03:01-05.06.01](../registry/features/05-io.md) and
> [fsht-03:01-08.01.04](../registry/features/08-numeric-semantics.md).
> Everything listed in §7 is a registry-tracked deferral, not a silent
> omission.

## 1. Numeric text parsing (fsht-03:01-05.04.01)

```ebnf
parse_fn   ::= ("parse_i64" | "parse_u64" | "parse_f64") "(" expr ")"
```

The counterpart of the formatting builtins (chapter 10): `parse_i64`,
`parse_u64` and `parse_f64` take a `str` and return a `Result` over a
new prelude enum:

```
enum ParseError { Invalid, OutOfRange }
parse_i64(s: str) -> Result<i64,  ParseError>
parse_u64(s: str) -> Result<u64,  ParseError>
parse_f64(s: str) -> Result<f64,  ParseError>
```

* Leading and trailing ASCII whitespace (space, tab, `\r`, `\n`) is
  skipped; the remainder MUST be non-empty and well-formed, else the
  result is `Err(Invalid)`.
* Integer forms: optional `+`/`-` sign (minus rejected by `parse_u64`
  with `Err(Invalid)`), then decimal digits only. Values beyond the
  destination type's range yield `Err(OutOfRange)` — overflow is
  reported, never wrapped.
* `parse_f64` accepts the full `fmt_f64` round-trip grammar: decimal
  point, optional exponent (`e`/`E`, optional sign), and the spellings
  `inf`, `-inf`, `nan` (case-insensitive). Out-of-range magnitudes yield
  `Err(OutOfRange)`; a syntactically valid but non-number remainder is
  `Err(Invalid)`.
* **The round-trip law** (MUST-level, pinned by the suite): for every
  `x: i64` and `x: u64`, `parse_i64(str_of(&fmt_i64(x)))` is `Ok(x)` and
  `parse_u64(str_of(&fmt_i64(x)))` is `Ok(x)`; for every `f64` `y` in
  the `fmt_f64` round-trip domain, `parse_f64(str_of(&fmt_f64(y, d)))`
  is `Ok(y')` where `y'` prints identically at the same digit count.
* The error path composes with `?` and `match` exactly like any
  `Result` (chapter 11); `Err` payloads are not printed by `print`.

## 2. Checked / saturating / wrapping variants (fsht-03:01-08.01.04)

```ebnf
checked_fn  ::= ("checked_add" | "checked_sub" | "checked_mul"
              |  "checked_div" | "checked_rem") "(" expr "," expr ")"
satur_fn    ::= ("saturating_add" | "saturating_sub" | "saturating_mul")
              "(" expr "," expr ")"
wrapping_fn ::= ("wrapping_add" | "wrapping_sub" | "wrapping_mul")
              "(" expr "," expr ")"
bounds_fn   ::= ("int_min" | "int_max") "(" expr ")"
```

Overflow policy is written, not assumed. For every integer scalar type
`T` (`i8`…`i64`, `u8`…`u64`, `usize`):

```
checked_add(a: T, b: T) -> Option<T>     // None on overflow
checked_sub(a: T, b: T) -> Option<T>
checked_mul(a: T, b: T) -> Option<T>
checked_div(a: T, b: T) -> Option<T>     // None on divisor 0 / INT_MIN / -1
checked_rem(a: T, b: T) -> Option<T>     // None on divisor 0 / INT_MIN / -1
saturating_add(a: T, b: T) -> T          // clamps to int_min/int_max
saturating_sub(a: T, b: T) -> T
saturating_mul(a: T, b: T) -> T
wrapping_add(a: T, b: T) -> T            // == the plain operator (explicit)
wrapping_sub(a: T, b: T) -> T
wrapping_mul(a: T, b: T) -> T
int_min(seed: T) -> T                     // type bounds of T
int_max(seed: T) -> T
```

* Both operands MUST have the **identical** integer type — the variant
  family is precision-explicit and performs no mixed-width promotion
  (`F0201`). A bare INT literal argument adopts the other operand's
  type (chapter 14's literal rule), so `checked_add(mx, 1)` is an i64
  call. Float operands are a type error (`F0201`); floating-point
  overflow is defined IEEE behaviour and needs no variants.
* `checked_div`/`checked_rem` return `None` exactly where the plain
  operators **trap** (chapter 14): divisor zero, and `INT_MIN / -1`.
  The plain operators keep their fsht-01:01 semantics — wrapping remains
  the default for `add`/`sub`/`mul` (registry history of 08.01.01).
  The `F0214` literal-zero rule targets the division *operators*; the
  variant family is a call surface — `checked_div(x, 0)` is legal and
  evaluates to `None`.
* `int_min`/`int_max` take one expression of type `T` purely to fix the
  instantiation; the argument value is not used.

## 3. Numeric conversions

```ebnf
cast_fn     ::= ("checked_cast" | "saturating_cast") "(" expr ")"
```

The "better numeric conversion facilities" of registry
`fsht-03:02-03.02.10` land here (recorded in that entry's history):
explicit, diagnosable conversion alongside the always-available
truncating `as`:

```
checked_cast<T, U>(x: T)    -> Option<U>   // None when not representable
saturating_cast<T, U>(x: T) -> U           // clamps to U's bounds
```

* `U` is inferred from the binding's type, an `Option<U>`/`U`-typed
  context, or a `match` arm — an unresolved `U` is `F0201`.
* Integer-to-integer: `checked_cast` is `Some` only when the value is
  representable in `U`; `saturating_cast` clamps to `int_min::<U>`/
  `int_max::<U>`. The truncating `as` cast (chapter 14) remains the
  deliberate width-drop and is unchanged.
* Float-to-integer: `checked_cast` is `None` for NaN and for magnitudes
  outside the representable integer range (including both infinities);
  on the `Some` path the value truncates toward zero (matching `as`).
  `saturating_cast` maps NaN to `0`, clamps infinities and out-of-range
  magnitudes to the bounds, and truncates toward zero.
* Integer-to-float and float-to-float conversions use `as` with the
  documented rounding; they are exactness-invisible at the value level
  and out of scope here.

## 4. Streaming I/O with `Result` integration (fsht-03:01-05.05.01)

Reading an entire multi-gigabyte dataset into a single `String` is not a
viable scientific-computing strategy — the library streams. Two new
prelude structs and one prelude enum:

```
Reader { handle: i64 }
Writer { handle: i64 }
enum IoError { NotFound, Permission, Eof, Busy, Other(i64) }
```

Module `io` (§5) provides the surface; qualified calls are written
`io::reader_open(...)`:

```
pub fn reader_open(path: str) -> Result<Reader, IoError>
pub fn reader_stdin() -> Reader
pub fn reader_read(r: borrowed mut Reader, buf: Span<u8>)
    -> Result<usize, IoError>
pub fn reader_read_line(r: borrowed mut Reader) -> Result<String, IoError>
pub fn writer_open(path: str) -> Result<Writer, IoError>
pub fn writer_write(w: borrowed mut Writer, data: str)
    -> Result<usize, IoError>
pub fn writer_flush(w: borrowed mut Writer) -> Result<usize, IoError>
pub fn reader_close(r: borrowed mut Reader)
pub fn writer_close(w: borrowed mut Writer)
pub fn remove(path: str) -> Result<bool, IoError>
```

* **Open.** `reader_open`/`writer_open` open a file for reading / for
  writing (create or truncate); missing paths and permission failures
  are `Err(NotFound)` / `Err(Permission)` — the ambiguous empty values
  of fsht-01:01's `file_read` are replaced, not removed (chapter 18
  keeps its surface).
* **Buffering (MUST).** Readers and writers buffer: `reader_read` of
  `n` bytes performs at most one underlying block fill per call from an
  internal buffer (default 64 KiB); `writer_write` appends to an
  internal buffer flushed at close, on `writer_flush`, or when the
  buffer fills. `Ok(count)` reports the bytes handled.
* **Reading.** `reader_read` fills `buf` (an out-region: the callee
  writes through the span) up to `buf.len` and returns
  `Ok(bytes_read)`; `Ok(0)` signals end of file. `reader_read_line`
  returns the next line without its terminator as an owned `String`
  (auto-dropped per chapter 24); hitting end of file with no partial
  line is `Err(Eof)`.
* **Ownership-tracked handles.** A `Reader`/`Writer` binding is an
  owned resource under the container model: scope-exit close is
  automatic and idempotent, `reader_close`/`writer_close` pre-empt it
  (the binding is invalidated — later use is `F0301`), and a by-value
  handle argument is a move. Double close is therefore impossible to
  express twice through one binding.
* `reader_stdin()` opens the process standard input; on targets without
  one it yields a reader whose first read returns `Err(Eof)`
  (chapter 25 defines the per-target behaviour).
* `remove` deletes a path: `Ok(true)`, `Err(NotFound)` when absent.
  The `?` operator propagates all of these with defers running
  (chapter 11).

## 5. Standard-library decomposition (fsht-03:01-05.06.01)

The `fsh` module grows into a proper collection of reusable modules.
The builtin modules directory (chapter 16's resolution order) ships:

```
core         primitive operations, memory, assertions
alloc        allocators, buffers, vectors
collections  vectors, queues, maps, sets
string       UTF-8 strings and formatting
math         standard mathematical functions
io           files, streams, buffered readers/writers
numeric      numeric traits and common algorithms
time         duration, timestamps and timers
bits         bit manipulation, endian conversion
random       random-number generators
```

* **Minimum normative content** (MUST): `core` exposes the `assert`
  family and the `freshet.*` intrinsics; `string` exposes the chapter 10
  builtins plus §1's parse functions; `collections` exposes the chapter
  20 `vec_*` surface; `math` exposes the chapter 13 intrinsic functions;
  `numeric` exposes §2/§3's variant and conversion functions plus
  `abs`/`gcd`/`clamp`; `bits` exposes `bswap16`/`bswap32`/`bswap64`
  (byte-swap) and `popcount` (set-bit count); `io` exposes §4; `time`
  exposes `now_ns`/`now_ms` (monotonic, unspecified epoch); `alloc`
  exposes `page_size`; `random` exposes `sm64_next(&mut state: u64) ->
  u64` — the **xorshift64\*** generator (shifts 12/25/27, multiplier
  2685821657736338717, u64 wrapping) also used by this repository's
  fuzz and benchmark harnesses, so random streams are reproducible
  across implementations.
* **The layer-separation rule** (MUST, chapter 00's three layers): the
  language standard never requires a Layer-2 (scientific) module, a
  Layer-2 library MUST be expressible without compiler changes, and a
  conforming compiler MUST NOT auto-import anything beyond the prelude
  and the modules listed above — a plain CLI program never drags in
  half a physics framework.
* **The `fsh` façade (MUST):** `import fsh;` keeps its exact fsht-01:01
  surface (chapter 18) unchanged; the new modules are additive, and
  `fsh`'s functions remain the thin aliases they always were.
* Module functions are ordinary pub declarations (chapter 16): visible
  unqualified after `import` or qualified as `io::reader_open`; the
  parse/checked/saturating/wrapping builtins of §1–§3 are
  **compiler-known builtins** usable without any import (the `fmt_*`
  precedent) and are re-exported by `string`/`numeric`.

## 6. Conformance requirements

The parse grammar and round-trip law, the variant signatures with
identical-operand types and `checked_div`'s trap-equivalent `None`
cases, the `checked_cast`/`saturating_cast` representability rules,
the buffered reader/writer surface with its `IoError` taxonomy, the
ownership-tracked handle lifecycle (scope-exit close, close as
pre-emptive release, use-after-close `F0301`), the module list with its
minimum content, the layer-separation rule and the `fsh` façade are
MUST-level. The 64 KiB default buffer size is SHOULD-level (a conforming
implementation MAY choose another, but MUST buffer).

## 7. Deferrals (registry-tracked)

* Queue, map and set container types (the `collections` skeleton ships
  with vectors only).
* Custom allocators over the `alloc` module (with fsht-02:01's tracked
  deferral).
* `time` beyond `now_ns`/`now_ms`; calendar arithmetic.
* Asynchronous I/O (fsht-04:01-05.07.01) — after streaming I/O, as its
  registry entry states.
* `parse_i8`/`parse_u8` and the narrower-width parsing family — use
  `parse_i64` + `checked_cast` (§3), which is the composition the
  registry's conversion requirement anticipated.
