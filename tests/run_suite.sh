#!/usr/bin/env bash
# Freshet-lang conformance & stress suite (fsht-01:01).
#
#   tests/run_suite.sh [extra penstock flags]
#
# Runs, against the Freshet compiler named by $FSHC (default: penstock on
# PATH, else a sibling Penstock checkout's bin/penstock):
#
#   1. corpus/    — positive programs with golden stdout (.expected)
#   2. negative/  — programs the standard REQUIRES to be rejected; when the
#                   compiler is penstock, the diagnostic ID in the .expected
#                   file must appear in the compiler output
#   3. props/     — self-checking property programs, run across several
#                   build configurations with identical output required
#                   (FRT_THREADS varied for the reproducibility property)
#   4. fuzz/      — differential fuzz smoke run (seeds via $FUZZ_SEEDS,
#                   default 32; full runs: tests/fuzz/run_fuzz.py --seeds 1000)
#
# Exit code 0 = suite green; 1 = any failure.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)

FSHC=${FSHC:-}
if [ -z "$FSHC" ]; then
  FSHC=$(command -v penstock || true)
fi
if [ -z "$FSHC" ]; then
  for cand in ../Penstock/bin/penstock ../bin/penstock ../../Penstock/bin/penstock; do
    if [ -x "$cand" ]; then FSHC=$(cd "$(dirname "$cand")" && pwd)/$(basename "$cand"); break; fi
  done
fi
if [ -z "$FSHC" ]; then
  echo "run_suite: no Freshet compiler found — set FSHC or put penstock on PATH"
  exit 2
fi
EXTRA_FLAGS=${1:-}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0

ok()   { pass=$((pass+1)); echo "  PASS  $1"; }
bad()  { fail=$((fail+1)); echo "  FAIL  $1"; }
run_compile() {  # -> rc in $?
  "$FSHC" $EXTRA_FLAGS "$1" -o "$TMP/t" 2>"$TMP/err"
}

echo "== Freshet-lang conformance suite (fsht-01:01) =="
echo "   compiler: $FSHC ${EXTRA_FLAGS:+(extra: $EXTRA_FLAGS)}"
echo

echo "-- corpus (golden outputs)"
for src in tests/corpus/*.fsht; do
  name=$(basename "$src" .fsht)
  want=$(cat "tests/corpus/$name.expected")
  if run_compile "$src"; then
    got=$("$TMP/t" 2>/dev/null)
    if [ "$got" = "$want" ]; then ok "corpus/$name"
    else bad "corpus/$name (got '$got' want '$want')"; fi
  else bad "corpus/$name (compile failed)"; sed -n '1,3p' "$TMP/err"; fi
done

echo "-- negative (programs the standard rejects)"
for src in tests/negative/*.fsht; do
  name=$(basename "$src" .fsht)
  code=$(head -n1 "tests/negative/$name.expected" | awk '{print $2}')
  if run_compile "$src"; then
    bad "negative/$name (compiled but must be rejected)"
  else
    if [ "${FSHC##*/}" = "penstock" ] && ! grep -q "\[$code\]" "$TMP/err"; then
      bad "negative/$name (rejected, but without diagnostic $code)"
      sed -n '1,3p' "$TMP/err"
    else ok "negative/$name ($code)"; fi
  fi
done

echo "-- properties (identical output across build configurations)"
run_cfg() {  # $1 name, $2.. flags; runs program under each; outputs compared
  local name=$1; shift
  local outs=""
  for cfg in "$@"; do
    if ! ( $FSHC $EXTRA_FLAGS $cfg "tests/props/$name.fsht" -o "$TMP/p_$name" ) 2>/dev/null; then
      echo "    (config '$cfg' failed to compile)"
      continue
    fi
    outs="$outs#$( "$TMP/p_$name" 2>/dev/null )"
  done
  if [ "${#outs}" -eq 0 ]; then bad "props/$name (no successful build)"; return; fi
  if [ "$(echo "$outs" | tr '#' '\n' | sort -u | wc -l)" -le 1 ]; then
    ok "props/$name (configs agree)"
  else
    bad "props/$name (configurations disagree)"
    echo "$outs" | tr '#' '\n' | sort -u | sed -n '1,6p'
  fi
}
run_cfg p02_int_semantics    "-O0" "-O3" "-O3 --no-loop-opts"
run_cfg p03_span_str_rules   "-O0" "-O3" "-O3 --no-loop-opts"
run_cfg p04_fp_strict_default "-O0" "-O3" "-O3 --no-loop-opts"
# p01: @reproducible must be bit-identical across worker counts
outs=""
for t in 1 2 4 8; do
  if $FSHC $EXTRA_FLAGS tests/props/p01_reproducible_threads.fsht -o "$TMP/p1_$t" 2>/dev/null; then
    outs="$outs#$(FRT_THREADS=$t "$TMP/p1_$t" 2>/dev/null)"
  fi
done
if [ -n "$outs" ] && [ "$(echo "$outs" | tr '#' '\n' | sort -u | wc -l)" -le 1 ]; then
  ok "props/p01_reproducible_threads (FRT_THREADS 1/2/4/8 bit-identical)"
else
  bad "props/p01_reproducible_threads (output depends on thread count)"
  echo "$outs" | tr '#' '\n' | sort -u | sed -n '1,6p'
fi

echo "-- differential fuzz (smoke: ${FUZZ_SEEDS:-32} seeds)"
if python3 tests/fuzz/run_fuzz.py --seeds "${FUZZ_SEEDS:-32}" \
      --compiler "$FSHC" --out "$TMP/fuzzout"; then
  ok "fuzz differential smoke"
else
  bad "fuzz differential smoke (artifacts under $TMP/fuzzout)"
fi

echo
echo "== $pass passed, $fail failed =="
[ $fail -eq 0 ]
