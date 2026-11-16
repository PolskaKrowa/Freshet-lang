# 18 — The `fsh` standard-library module (normative in fsht-01:01)

`import fsh;` — found through the builtin modules directory, no `-I`
needed. The fsht-01:01 surface is deliberately minimal: a
Freshet-facing wrapper over the runtime for argv, environment, file I/O
and test assertions, without a single manual `extern fn` (fsht-01:01-05.03.01).

```
pub fn args_count() -> i64
pub fn args_get(i: i64) -> str            // borrowed view of argv[i]
pub fn arg_or(i: i64, d: str) -> str
pub fn env_get(name: str) -> str          // "" when unset
pub fn env_or(name: str, d: str) -> str
pub fn file_size(path: str) -> i64        // -1 when missing
pub fn file_read(path: str) -> str        // fresh NUL-terminated buffer
pub fn file_write(path: str, data: str) -> i64
pub fn assert_eq_i64(got: i64, want: i64, what: str) -> i64
pub fn assert_eq_f64(got: f64, want: f64, what: str) -> i64
```

* `file_read` returns a `str` view over a **fresh heap buffer** the
  caller must free; an empty result means the file was missing.
* The C-level `libfsh` (include/fsh/*.h, libfsh.a) remains available
  through `extern fn` + `#link fsh` for everything not wrapped here.

## Known gaps (honest fsht-01:01 surface)

* **No numeric text parsing**: `fmt_i64`/`fmt_f64` exist; `parse_i64` /
  `parse_f64` do not (registry `fsht-03:01-05.04.01`).
* **No streaming I/O**: `file_read` reads whole files; buffered
  readers/writers for multi-gigabyte datasets are part of the fsht-03:01
  standard-library update, together with `Result<T, E>` integration so
  I/O failures propagate instead of surfacing as ambiguous empty values.
* **No generic containers**: `String` is the only growable buffer
  (chapter 10). The planned module decomposition for fsht-03:01 —
  `core / alloc / collections / string / math / io / numeric / time /
  bits / random` — is tracked in the registry, not here.

## Conformance requirements

The module surface above with its exact signatures and the documented
buffer/empty-value semantics are MUST-level for the reference
implementation; independent implementations SHOULD provide the same
surface (it is the library the test suite's `assert_eq_*` helpers use).
