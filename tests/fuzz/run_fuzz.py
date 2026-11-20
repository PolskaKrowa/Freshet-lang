#!/usr/bin/env python3
"""Freshet differential fuzz driver (fsht-03:03).

Generates random deterministic-output programs (fuzz/gen.py), then builds
and runs each one under several compiler configurations and compares the
full stdout — the differential oracle. Any difference between
configurations is a compiler defect; a crash or timeout is a defect; a
compile failure on a valid program is a conformance signal worth filing
(it may also be a generator bug — both are recorded, neither is silent).

usage:
  tests/fuzz/run_fuzz.py [--seeds 64] [--seed-base 20250101] [--budget 12]
      [--configs "-O0|-O3|-O3 --no-loop-opts"]  (default; | separated,
      rendered as argument lists)
      [--compiler PATH] [--timeout 30] [--out DIR]

Compiler discovery: --compiler, then $FSHC, then `penstock` on PATH, then
a sibling Penstock checkout (../bin/penstock).
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gen  # noqa: E402  (fuzz/gen.py)


def find_compiler(flag_val):
    if flag_val:
        return flag_val
    if os.environ.get("FSHC"):
        return os.environ["FSHC"]
    w = shutil.which("penstock")
    if w:
        return w
    cand = os.path.join(os.path.dirname(HERE), "..", "Penstock", "bin",
                        "penstock")
    for probe in (cand,
                  os.path.join(os.path.dirname(HERE), "..", "bin", "penstock")):
        if os.path.isfile(probe):
            return probe
    return None


def parse_configs(spec):
    cfgs = []
    for part in spec.split("|"):
        cfgs.append(part.split())
    return cfgs


def run_one(compiler, flags, src, exe, timeout):
    try:
        p = subprocess.run([compiler] + flags + [src, "-o", exe],
                           capture_output=True, text=True, timeout=timeout * 4)
    except subprocess.TimeoutExpired:
        return "compile-timeout", ""
    if p.returncode != 0:
        return "compile-failed", (p.stderr or p.stdout)[-800:]
    try:
        r = subprocess.run([exe], capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return "run-timeout", ""
    if r.returncode != 0:
        return "crashed", ("rc=%d" % r.returncode)
    return "ok", r.stdout


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--seed-base", type=int, default=20250101)
    ap.add_argument("--budget", type=int, default=12)
    ap.add_argument("--configs", default="-O0|-O3|-O3 --no-loop-opts")
    ap.add_argument("--compiler")
    ap.add_argument("--timeout", type=int, default=30)
    ap.add_argument("--out", default=os.path.join(HERE, "fuzz-artifacts"))
    args = ap.parse_args()

    import random
    compiler = find_compiler(args.compiler)
    if not compiler:
        print("run_fuzz: no Freshet compiler found (use --compiler or $FSHC)")
        return 2
    cfgs = parse_configs(args.configs)
    print("run_fuzz: compiler=%s seeds=%d configs=%s" % (
        compiler, args.seeds, " / ".join(" ".join(c) for c in cfgs)))

    os.makedirs(args.out, exist_ok=True)
    ok = mismatch = crash = compile_fail = 0
    hard_fail = False

    for idx in range(args.seeds):
        seed = args.seed_base + idx
        rng = random.Random(seed)
        program = gen.gen_program(rng, args.budget, str(seed))
        src = os.path.join(args.out, "seed_%d.fsht" % seed)
        with open(src, "w") as f:
            f.write(program)
        outputs = {}
        labels = {}
        for ci, flags in enumerate(cfgs):
            exe = os.path.join(args.out, "seed_%d_cfg%d.bin" % (seed, ci))
            status, payload = run_one(compiler, flags, src, exe, args.timeout)
            labels[" ".join(flags)] = (status, payload)
            outputs[" ".join(flags)] = (status, payload)
        statuses = {v[0] for v in outputs.values()}
        if "crashed" in statuses or "run-timeout" in statuses:
            crash += 1
            hard_fail = True
            print("  seed %d: CRASH/TIMEOUT" % seed)
            for k, v in labels.items():
                print("      %-24s %s" % (k, v[0]))
        elif "compile-failed" in statuses or "compile-timeout" in statuses:
            compile_fail += 1
            print("  seed %d: COMPILE-FAIL (kept %s; check validity against "
                  "the spec — this is a conformance signal or a generator "
                  "bug)" % (seed, src))
            for k, v in labels.items():
                if v[0] != "ok":
                    print("      %-24s %s: %s" % (k, v[0], v[1][:200]))
        else:
            outs = {v[1] for v in outputs.values()}
            if len(outs) != 1:
                mismatch += 1
                hard_fail = True
                print("  seed %d: OUTPUT MISMATCH (kept %s)" % (seed, src))
                for k, v in labels.items():
                    print("      %-24s %r" % (k, v[1][:120]))
            else:
                ok += 1
                os.remove(src)

    print("run_fuzz: %d ok, %d mismatch, %d crash, %d compile-fail "
          "(seed base %d)" % (ok, mismatch, crash, compile_fail,
                              args.seed_base))
    if mismatch or crash:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
