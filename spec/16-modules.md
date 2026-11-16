# 16 — Modules (normative in fsht-01:01)

## Declaration and visibility

```ebnf
module_decl ::= "module" identifier ";"
import_decl ::= "import" identifier ";"
visibility  ::= "pub"
qualified    ::= module_name "::" ( identifier | type )
```

* `module geometry;` — optional file-based module identity; MUST be the
  first declaration in the file; default: the sanitised file stem.
* `import geometry;` — a language-level dependency (see resolution below).
* `pub fn` / `pub struct` export; everything else is private.

```
module geometry;
import fsh;
pub fn distance(a: Point, b: Point) -> f64 { ... }
pub struct Point { x: f64, y: f64 }
fn helper() { ... }               // invisible outside the module
```

## Semantics

* **Importing is not textual inclusion.** No duplicate definitions, no
  macro leakage: `#include`/`#define` remain preprocessor features for
  local text splicing (chapter 01); `import` is a semantic dependency.
* From a module you can see: your own declarations (pub or private), `pub`
  declarations of directly imported modules, and the prelude (`String`,
  `Option`, `Result`). Everything else is private — using it is `F0004`
  ("private to module 'm'").
* Two modules may define the same name (private decls coexist); an
  ambiguous unqualified reference to two visible `pub` decls is `F0004`
  (qualify it).
* Qualified names: `geometry::distance(a, b)` in expressions,
  `mod::Type` in type position. Qualifying a non-imported module is
  `F0004`.
* **Resolution order** for `import geometry;`: the entry file's
  directory, then `-I<dir>` directories, then the builtin modules
  directory (where the shipped `fsh` module lives), then `.` — for
  `geometry.fsht` or `geometry/mod.fsht`. Missing module → `F0004` with
  every searched path. **Circular imports are `F0004`** with the full
  cycle chain.
* **Multi-file compilation:** `penstock main.fsht util.fsht` — every
  `.fsht` argument is a module of ONE program (the first is the entry);
  imports resolve the rest. Internal symbols disambiguate to
  `u_<module>$<name>` in generated IR only when two modules define the
  same name; `main`, `export fn` and `extern fn` keep their exact C-ABI
  names.

## Project manifest (fsht-01:01-07.01.03)

```toml
[project]
name = "demo"
[target]
type = "bin"             # bin | static-lib | shared-lib
src  = ["src/main.fsht"]
[build]
opt = 3
threads = 0
[link]
libs = ["m"]
[modules]
path = ["lib"]
```

`penstock build [dir]` reads `penstock.toml`; output lands beside the
manifest as `<project name>` (`lib<name>.a` / `<name>.so` for library
targets) unless `-o` overrides. Whole-program dependency tracking: the
build cache hashes the CONTENT of every module in the import closure plus
the flags — unchanged sources print "up to date" and skip recompilation
(`--force` rebuilds).

## Conformance requirements

Visibility, resolution order, cycle detection, non-textual import
semantics and the IR symbol plan are MUST-level; the manifest surface is
MUST-level for the reference implementation and SHOULD-level elsewhere.
