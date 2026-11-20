# The Freshet-lang stress & conformance suite (fsht-03:03)

This directory is the compiler-independent part of the standards
repository: everything here stresses *a given Freshet compiler* against
the normative rules of the fsht-03:03 specification, using differential
and golden-output oracles instead of compiler-internal assertions.

## Layout

```
tests/
  corpus/     curated positive programs + .expected golden stdout
  negative/   programs the standard requires to be REJECTED
              (each .expected names the diagnostic ID, e.g. `reject F0301`)
  props/      self-checking property programs (integer semantics, span/str
              rules, strict-FP default, @reproducible thread-invariance,
              container invariants, trait dispatch, const generics,
              the numeric library, the borrowing discipline)
  fuzz/       seeded random-program generator + differential driver
  run_suite.sh  the top-level runner
```

The fsht-02 coverage (ratified 2026-11-19 together with spec chapters
20–22):

* **fsht-02:01 dynamic collections** — `corpus/14_vec_containers` and
  `negative/n15–n19_vec_*` exercise the `Vec<T>` surface, the
  ownership/move/drop model and the `Span<T>` view resolution
  (registry 02.09.01/02.09.02, spec ch. 20); `props/p05_vec_containers`
  checks the runtime container invariants; the fuzz generator has a
  matching `b_vec` block.
* **fsht-02:02 traits** — `corpus/18_traits_static_dispatch` and
  `negative/n20–n22` exercise trait declarations, impls, `+` bounds and
  static dispatch (registry 06.02.01, spec ch. 21);
  `props/p06_traits_dispatch` checks that one generic body picks the
  right impl per representation; the fuzz generator has a matching
  `b_traits` block.
* **fsht-02:03 const generics** — `corpus/19_const_generics` and
  `negative/n23–n25` exercise const parameters, const expressions,
  `const fn` and `const_assert` (registry 06.03.01, spec ch. 22);
  `props/p07_const_generics` checks instantiation exactness; the fuzz
  generator has a matching `b_constgen` block.

The fsht-03 coverage (ratified 2026-11-19 together with spec chapters
23–25; fsht-02 coverage follows it):

* **fsht-03:01 the expanded standard library** — `corpus/
  20_stdlib_parsing_streaming` exercises the parse functions over
  `Result`+`ParseError`, the checked/saturating/wrapping variants, the
  conversions, the decomposed modules (`io`/`bits`/`numeric`/`random`)
  and the streaming `Reader`/`Writer` round-trip; `props/
  p08_stdlib_numeric` pins the consistency laws (parse∘fmt identity,
  checked↔wrapping agreement, saturating bounds, `checked_div`'s
  trap-equivalence); the fuzz generator has matching `b_parse` and
  `b_checked` blocks; `negative/n29_reader_use_after_close`,
  `n30_checked_mixed_width` and `n31_parse_not_str` pin the handle
  lifecycle and the type rules (registry 05.04.01/05.05.01/05.06.01,
  08.01.04, spec ch. 23).
* **fsht-03:02 mutable borrows & lifetimes** — `corpus/
  21_borrow_mut_lifetimes` exercises every legal side of the discipline
  (borrow expressions, `borrowed mut` parameters, shared-borrow
  coexistence, views surviving in-place writes, the tracked `String`,
  drop elaboration through struct shapes, owning elements, nested
  containers); `props/p09_borrow_exclusivity` checks the same shapes
  are configuration-stable; `negative/n26–n28` pin the illegal side
  (`F0310` twice, `F0311` once); the fuzz generator has a matching
  `b_borrow` block (registry 03.02.09/03.02.10, spec ch. 24).
* **fsht-03:03 the portable runtime** — `corpus/22_portable_program` is
  the pinned portable exhibit: the target-matrix workflow
  (`.github/workflows/targets.yml`) runs it on every ratified target
  with this repository's golden as the single expected output — the
  tested-before-declared gate (registry 10.03.02, spec ch. 25).

A compiler that implements only the fsht-01:01 surface will reject the
fsht-02/03 entries (unknown builtins / unknown syntax) — that is the
intended per-version conformance gating, not a suite defect.

## Running

```sh
FSHC=/path/to/penstock tests/run_suite.sh          # whole suite
tests/run_suite.sh --strict-performance           # with extra compiler flags
FUZZ_SEEDS=500 tests/run_suite.sh                 # longer fuzz smoke
tests/fuzz/run_fuzz.py --seeds 2000 --seed-base 7 # dedicated fuzz campaign
```

Compiler discovery: `$FSHC`, then `penstock` on `PATH`, then a sibling
`Penstock/` checkout's `bin/penstock`.

## Oracles

1. **Golden output** (`corpus/`): the program's entire stdout must equal
   the `.expected` file. Goldens were derived from the normative rules
   (two's-complement wrapping, truncating division, IEEE-754 defaults,
   byte-based `str` indexing, span slicing rules, container
   move/drop semantics) and verified independently with Python
   arithmetic.
2. **Rejection** (`negative/`): a conforming compiler must refuse the
   program. When the compiler is Penstock, the printed diagnostic must
   carry the ID named in the `.expected` file — for other compilers the
   requirement is rejection itself; the IDs are the standard's registry
   and any Freshet compiler is encouraged to map them.
3. **Configuration equivalence** (`props/` + `fuzz/`): the same program
   built at `-O0`, `-O3` and `-O3 --no-loop-opts` (and, for the
   reproducibility property, at `FRT_THREADS` = 1/2/4/8) must produce
   byte-identical output. Divergence is a compiler defect.
4. **Fuzz differential** (`fuzz/`): `gen.py` composes random
   deterministic-output programs from spec-valid shapes (loops of every
   documented flavour, casts, structs, enums + `match`, spans, strings,
   malloc/defer ownership shapes, `parfor` reductions over exact integer
   arithmetic — and since fsht-02: `Vec<T>` container blocks, trait
   dispatch blocks and const-generic instantiation blocks; since
   fsht-03: parse round-trip blocks, checked/saturating/wrapping
   variant blocks and mutable-borrow blocks).
   `run_fuzz.py` builds each program under several configurations and
   compares full stdout; crashes, timeouts, output mismatches and
   compile failures of valid programs are all recorded — failing
   programs are kept in an artifacts directory for reduction. Programs
   print only computed values; float accumulation uses exact dyadic
   constants so no legal reassociation can change the output.

## Conformance classes

A compiler claiming fsht-03:03 conformance:

* compiles and runs every `corpus/` program with exactly the golden
  output;
* rejects every `negative/` program (diagnostic IDs are SHOULD-level —
  the numeric registry itself is normative for Penstock);
* produces configuration-equivalent output for `props/` and for fuzz
  programs (this is where optimisation correctness is stressed).

The fuzz generator deliberately grows with the standard: every new
fsht-xx:yy feature gains a generator block + corpus entries in the same
pull request, so the suite's coverage follows the specification.
