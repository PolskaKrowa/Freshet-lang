#!/usr/bin/env python3
"""Freshet-lang benchmark driver (fsht-01:01).

Builds and runs every benchmark kernel in every available implementation
(freshet / idiomatic C++ / hand-tuned C++ / safe Rust), checks that all
built implementations agree on the kernel checksum, times the hot region
(best of N repetitions, using the program-reported TIME line), and writes
``results.json`` + ``results.md`` with a win/loss verdict per language pair.

usage:
  benchmarks/bench.py [--kernels k1,k2] [--reps 5] [--workdir DIR]
      [--penstock PATH] [--cxx PATH] [--rustc PATH]
      [--freshet-flags "--fast-math"] [--skip rust] [--timeout 120]
      [--out results.json] [--list]

Toolchain discovery order for each language: explicit CLI flag, then the
PENSTOCK / CXX / RUSTC environment variables, then PATH, then common
locations relative to a sibling Penstock checkout (bin/penstock). A
missing toolchain skips that language with a note (exit code stays 0);
a checksum disagreement or a crash is a FAILURE (exit code 1).

The reference kernel specification is benchmarks/KERNELS.md; each kernel
prints exactly ``TIME <ns>`` and ``CS <decimal>``.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KDIR = os.path.join(HERE, "kernels")

LANGS = ("freshet", "idiomatic", "tuned", "rust")
FILES = {"freshet": "freshet.fsht", "idiomatic": "idiomatic.cpp",
         "tuned": "tuned.cpp", "rust": "safe.rs"}
LABELS = {"freshet": "freshet", "idiomatic": "idiomatic C++",
          "tuned": "hand-tuned C++", "rust": "safe Rust"}


# ---------------------------------------------------------------- utilities

def log(msg):
    print(msg, flush=True)


def find_tool(flag_val, env_name, path_names, sibling_probe):
    """flag > env > PATH > sibling checkout probe."""
    if flag_val:
        return flag_val if os.path.isfile(flag_val) or shutil.which(flag_val) else None
    if env_name and os.environ.get(env_name):
        cand = os.environ[env_name]
        return cand if os.path.isfile(cand) or shutil.which(cand) else None
    for name in path_names:
        w = shutil.which(name)
        if w:
            return w
    if sibling_probe:
        here = HERE
        for _ in range(3):
            cand = os.path.join(os.path.dirname(here), sibling_probe)
            if os.path.isfile(cand):
                return cand
            here = os.path.dirname(here)
    return None


def run_cmd(cmd, timeout, cwd=None, env=None):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd, env=env)
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        return None


def parse_output(text):
    """Parse the TIME/CS contract. Returns (time_ns:int|None, cs:str|None)."""
    if text is None:
        return None, None
    t = t2 = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("TIME ") and t is None:
            try:
                t = int(line[5:].strip())
            except ValueError:
                pass
        elif line.startswith("CS ") and t2 is None:
            t2 = line[3:].strip()
    return t, t2


# ---------------------------------------------------------------- per-lang

class Toolchain:
    def __init__(self, args):
        self.penstock = find_tool(args.penstock, "PENSTOCK",
                                   ["penstock"], "bin/penstock")
        self.cxx = find_tool(args.cxx, "CXX", ["clang++", "g++", "c++"], None)
        self.rustc = find_tool(args.rustc, "RUSTC", ["rustc"], None)
        self.freshet_flags = shlex_split(args.freshet_flags)

    def available(self, lang):
        return {"freshet": self.penstock, "idiomatic": self.cxx,
                "tuned": self.cxx, "rust": self.rustc}[lang]

    def build(self, lang, src, exe, workdir, timeout):
        if lang == "freshet":
            cmd = [self.penstock] + self.freshet_flags + [src, "-o", exe]
        elif lang in ("idiomatic", "tuned"):
            cmd = [self.cxx, "-O2", "-std=c++17", "-ffp-contract=off",
                   src, "-o", exe, "-lm"]
        else:
            cmd = [self.rustc, "--edition", "2021", "-C", "opt-level=3",
                   src, "-o", exe]
        p = run_cmd(cmd, timeout, cwd=workdir)
        if p is None:
            return False, "build timeout"
        if p.returncode != 0:
            return False, (p.stderr or p.stdout).strip()[-1500:]
        return True, ""


def shlex_split(s):
    if not s:
        return []
    import shlex
    return shlex.split(s)


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Freshet-lang benchmark driver")
    ap.add_argument("--kernels", help="comma-separated subset")
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--workdir", default="/tmp/freshet-lang-bench")
    ap.add_argument("--penstock")
    ap.add_argument("--cxx")
    ap.add_argument("--rustc")
    ap.add_argument("--freshet-flags", default="")
    ap.add_argument("--skip", default="", help="comma-separated langs to skip")
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--out", default=None, help="results.json path")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    kernels = []
    for name in sorted(os.listdir(KDIR)):
        if os.path.isfile(os.path.join(KDIR, name, "kernel.json")):
            kernels.append(name)
    if args.kernels:
        want = [k.strip() for k in args.kernels.split(",") if k.strip()]
        bad = [k for k in want if k not in kernels]
        if bad:
            log("unknown kernels: %s (have: %s)" % (bad, ", ".join(kernels)))
            return 2
        kernels = want
    if args.list:
        log("\n".join(kernels))
        return 0

    skip = set(k.strip() for k in args.skip.split(",") if k.strip())
    tc = Toolchain(args)

    header = []
    for lang in LANGS:
        if lang in skip:
            header.append("%s: skipped by --skip" % LABELS[lang])
        elif not tc.available(lang):
            header.append("%s: toolchain not found -> skipped" % LABELS[lang])
        else:
            header.append("%s: %s" % (LABELS[lang], tc.available(lang)))
    log("Freshet-lang benchmarks (fsht-01:01)")
    for h in header:
        log("  " + h)
    log("")

    os.makedirs(args.workdir, exist_ok=True)
    results = []
    failures = 0

    for kname in kernels:
        kdir = os.path.join(KDIR, kname)
        with open(os.path.join(kdir, "kernel.json")) as f:
            meta = json.load(f)
        row = {"kernel": kname, "title": meta.get("title", ""),
               "cs_type": meta.get("cs"), "times": {}, "cs": {},
               "status": {}, "fail": False, "notes": []}
        ref_cs = None
        for lang in LANGS:
            if lang in skip or not tc.available(lang):
                row["status"][lang] = "skipped"
                continue
            src = os.path.join(kdir, FILES[lang])
            exe = os.path.join(args.workdir, "%s_%s" % (kname, lang))
            ok, err = tc.build(lang, src, exe, args.workdir, args.timeout)
            if not ok:
                row["status"][lang] = "build-failed"
                row["fail"] = True
                row["notes"].append("%s build failed: %s" % (lang, err[:300]))
                failures += 1
                continue
            best = None
            cs_seen = None
            crashed = False
            for rep in range(args.reps):
                p = run_cmd([exe], timeout=args.timeout,
                            cwd=args.workdir, env=build_env())
                if p is None or p.returncode != 0:
                    crashed = True
                    row["notes"].append("%s run failed (rc=%s)" % (
                        lang, "timeout" if p is None else p.returncode))
                    break
                t, cs = parse_output(p.stdout)
                if t is None or cs is None:
                    crashed = True
                    row["notes"].append("%s violated the TIME/CS contract: %r"
                                        % (lang, (p.stdout or "")[:120]))
                    break
                if cs_seen is None:
                    cs_seen = cs
                elif cs_seen != cs:
                    crashed = True
                    row["notes"].append("%s unstable checksum" % lang)
                    break
                best = t if best is None else min(best, t)
            if crashed:
                row["status"][lang] = "run-failed"
                row["fail"] = True
                failures += 1
                continue
            row["status"][lang] = "ok"
            row["times"][lang] = best
            row["cs"][lang] = cs_seen
            if ref_cs is None:
                ref_cs = cs_seen
            elif cs_seen != ref_cs:
                row["fail"] = True
                row["notes"].append("CHECKSUM MISMATCH within %s "
                                    "(freshet/ref=%s, %s=%s)"
                                    % (kname, ref_cs, lang, cs_seen))
        # verdicts vs freshet (only when freshet itself ran ok)
        verdicts = {}
        if row["status"].get("freshet") == "ok":
            ft = row["times"]["freshet"]
            for lang in LANGS:
                if row["status"].get(lang) != "ok":
                    continue
                ratio = ft / row["times"][lang] if row["times"][lang] else None
                verdicts[lang] = ("loss" if ratio and ratio > 1.05 else
                                  "win" if ratio and ratio < 1 / 1.05 else "parity")
        row["verdicts"] = verdicts
        results.append(row)
        line = "  %-14s" % kname
        for lang in LANGS:
            st = row["status"].get(lang)
            if st != "ok":
                line += "%-12s" % ("--" if st == "skipped" else "FAIL")
            else:
                line += "%-12s" % fmt_ns(row["times"][lang])
        log(line + "   " + ("FAIL " if row["fail"] else "ok"))
        for note in row["notes"]:
            log("      ! " + note)

    out_json = args.out or os.path.join(args.workdir, "results.json")
    with open(out_json, "w") as f:
        json.dump({"driver": os.path.abspath(__file__),
                   "reps": args.reps, "results": results}, f, indent=2)
    md_path = os.path.splitext(out_json)[0] + ".md"
    write_markdown(md_path, results, tc)
    log("")
    log("results: %s" % out_json)
    log("summary: %s" % md_path)
    if failures:
        log("%d failure(s) — see notes above" % failures)
    return 1 if failures else 0


def build_env():
    e = dict(os.environ)
    # keep parfor deterministic-friendly defaults for benchmarking
    e.setdefault("FRT_SERIAL_CUTOFF", "256")
    return e


def fmt_ns(ns):
    if ns >= 1_000_000_000:
        return "%.2fs" % (ns / 1e9)
    if ns >= 1_000_000:
        return "%.1fms" % (ns / 1e6)
    return "%dus" % (ns // 1000)


def write_markdown(path, results, tc):
    lines = ["# Freshet-lang benchmark results (fsht-01:01)", "",
             "Best of the configured repetitions, hot-region time "
             "(program-reported `TIME`). `CS` must agree across every "
             "built implementation — a disagreement is a suite failure.", "",
             "| kernel | freshet | idiomatic C++ | tuned C++ | safe Rust |"
             " freshet vs idiomatic | vs tuned | vs rust |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        def cell(lang):
            st = r["status"].get(lang)
            if st != "ok":
                return "--" if st == "skipped" else "FAIL"
            return fmt_ns(r["times"][lang])
        def verdict(lang):
            v = r.get("verdicts", {}).get(lang)
            if not v:
                return ""
            if r["status"].get(lang) == "ok" and r["status"].get("freshet") == "ok":
                ratio = r["times"]["freshet"] / r["times"][lang]
                return "%s (%.2fx)" % (v, ratio)
            return v
        lines.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
            r["kernel"], cell("freshet"), cell("idiomatic"), cell("tuned"),
            cell("rust"), verdict("idiomatic"), verdict("tuned"),
            verdict("rust")))
    lines += ["", "Notes:"]
    for r in results:
        for n in r["notes"]:
            lines.append("- `%s`: %s" % (r["kernel"], n))
    if not any(r["notes"] for r in results):
        lines.append("- none")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    sys.exit(main())
