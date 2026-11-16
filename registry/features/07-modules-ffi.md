# 07 — modules & FFI features (fsht-01:01)

### fsht-01:01-07.01.01 — modules and visibility

Status: normative. Spec: [ch. 16](../../spec/16-modules.md)

`module`/`import`/`pub`; private by default; qualified names
(`mod::item`); importing is a language-level dependency, never textual
inclusion; `F0004` for missing/private/ambiguous imports and cycles.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-07.01.02 — multi-file compilation

Status: normative. Spec: [ch. 16](../../spec/16-modules.md)

`penstock main.fsht util.fsht` — every `.fsht` argument is a module of
one program (first is the entry); internal symbol disambiguation
`u_<module>$<name>` only on collisions; C-ABI names preserved for
`main`/`export fn`/`extern fn`.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-07.01.03 — project manifest

Status: normative (reference implementation). Spec: [ch. 16](../../spec/16-modules.md)

`penstock build [dir]` with `penstock.toml` (`[project]/[target]/
[build]/[link]/[modules]`), whole-program content-hash dependency cache.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-07.02.01 — function pointers

Status: normative. Spec: [ch. 17](../../spec/17-ffi.md)

First-class pointer-sized `fn(P...) -> R` values; name coercion;
reassignable slots; indirect calls type-checked; unknown effects →
`F0307` inside parfor, forbidden in `@pure`.

History:
- fsht-01:01 — first standardised.

### fsht-01:01-07.02.02 — C callbacks and extern linkage

Status: normative. Spec: [ch. 17](../../spec/17-ffi.md)

`extern fn` with fn-pointer parameters gives the C callback ABI
(Freshet functions run as `qsort` comparators); `export fn` keeps exact
C symbols; string literals NUL-terminated for interop.

History:
- fsht-01:01 — first standardised.

### fsht-04:01-07.03.01 — variadic `extern fn`

Status: proposed (not scheduled).

Better C interoperability (e.g. `printf`-family); out of scope in
fsht-01:01, recorded here so the boundary is explicit.

### fsht-04:01-07.04.01 — automatic C header generation

Status: proposed (not scheduled).

Easier library interoperability: generate C headers from Freshet
`export fn` declarations; today bindings are declared, not generated.

### fsht-04:02-10.05.01 — package manager

Status: deferred (target fsht-04:02 at the earliest).

External library distribution. NOTE (maintainer): the registry package
requires a custom webserver for package hosting, which the maintainer
will manage personally — the feature is deferred until that
infrastructure exists, not for language-design reasons.
