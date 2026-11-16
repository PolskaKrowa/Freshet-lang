# The Freshet-lang stress & conformance suite (fsht-01:01)

This directory is the compiler-independent part of the standards
repository: everything here stresses *a given Freshet compiler* against
the normative rules of the fsht-01:01 specification, using differential
and golden-output oracles instead of compiler-internal assertions.

## Layout

```
tests/
  corpus/     curated positive programs + .expected golden stdout
  negative/   programs the standard requires to be REJECTED
              (each .expected names the diagnostic ID, e.g. `reject F0301`)
  props/      self-checking property programs (integer semantics, span/str
              rules, strict-FP default, @reproducible thread-invariance)
  fuzz/       seeded random-program generator + differential driver
  run_suite.sh  the top-level runner

fsht-02:01 draft additions: `corpus/13_vec_containers` and
`negative/n18–n22_vec_*` exercise the in-development dynamic-collection
rules (registry 02.09.01/02.09.02, draft spec chapter 20). They run
with the rest of the suite; a compiler without the fsht-02:01 cut will
fail them (compile errors on unknown builtins), which is the expected
conformance signal until fsht-02:01 ratifies.
```

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
   byte-based `str` indexing, span slicing rules) and verified
   independently with Python arithmetic.
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
   arithmetic). `run_fuzz.py` builds each program under several
   configurations and compares full stdout; crashes, timeouts, output
   mismatches and compile failures of valid programs are all recorded —
   failing programs are kept in an artifacts directory for
   reduction. Programs print only computed values; float accumulation
   uses exact dyadic constants so no legal reassociation can change the
   output.

## Conformance classes

A compiler claiming fsht-01:01 conformance:

* compiles and runs every `corpus/` program with exactly the golden
  output;
* rejects every `negative/` program (diagnostic IDs are SHOULD-level —
  the numeric registry itself is normative for Penstock);
* produces configuration-equivalent output for `props/` and for fuzz
  programs (this is where optimisation correctness is stressed).

The fuzz generator deliberately grows with the standard: every new
fsht-02:xx feature gains a generator block + corpus entries in the same
pull request, so the suite's coverage follows the specification.
