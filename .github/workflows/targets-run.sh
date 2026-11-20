#!/usr/bin/env bash
# Execution helper for the fsht-03:03 target matrix
# (.github/workflows/targets.yml). Resolves the artifact Penstock
# emitted (bare executable, .exe on windows, .wasm for the wasm rows)
# and runs it in the row's execution environment.
#
#   targets-run.sh <binary-path> <mode> [VAR=VAL ...]
#
# mode: native | wasmtime | node. Extra VAR=VAL arguments become the
# process environment (FRT_* knobs) so chapter 25 §4's silent-default
# rule is exercised per target.
set -u
BIN=$1
MODE=$2
shift 2
ART=""
for cand in "$BIN" "$BIN.exe" "$BIN.wasm"; do
  if [ -f "$cand" ]; then ART=$cand; break; fi
done
if [ -z "$ART" ]; then
  echo "targets-run: no artifact at $BIN{,.exe,.wasm}" >&2
  exit 2
fi
case "$MODE" in
  native)
    exec env "$@" "$ART"
    ;;
  wasmtime)
    ARGS=()
    for kv in "$@"; do
      ARGS+=(--env "$kv")
    done
    exec wasmtime run "${ARGS[@]}" "$ART"
    ;;
  node)
    exec env "$@" node "$(dirname "$0")/targets-embed.js" "$ART"
    ;;
  *)
    echo "targets-run: unknown run mode '$MODE'" >&2
    exit 2
    ;;
esac
