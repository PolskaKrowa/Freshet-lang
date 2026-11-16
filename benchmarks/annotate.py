#!/usr/bin/env python3
"""Freshet-lang loss annotation (fsht-01:01).

For every benchmark kernel where another language beat Freshet, produce an
in-detail, side-by-side annotation of the generated code of the hot
function — final optimised LLVM IR (Freshet vs the rival), source-annotated
disassembly, and (when perf + hardware counters are available, e.g. on the
self-hosted perf runner) `perf record`/`perf annotate` instruction-level
cycle attribution for BOTH binaries. A measured instruction census and
derived observations explain, in numbers, why the rival optimised the
function better than Freshet did.

usage:
  benchmarks/annotate.py --results results.json
      [--benchmarks-dir .] [--workdir /tmp/flang-annot]
      [--out reports] [--threshold 1.05] [--perf auto|force|off]
      [--max-ir-lines 260] [--max-dis-lines 240]

Input: the results.json written by bench.py. Output: one markdown report
per losing pair under <out>/losses/ plus an INDEX.md. Everything static
(IR + disassembly) works on any machine with the toolchains; the perf
sections additionally require perf and PMU access (the self-hosted runner).
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

LANG_LABEL = {"idiomatic": "idiomatic C++", "tuned": "hand-tuned C++",
              "rust": "safe Rust", "freshet": "Freshet"}


# ---------------------------------------------------------------- helpers

def log(msg):
    print(msg, flush=True)


def run_cmd(cmd, timeout=300, cwd=None):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout, cwd=cwd)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def which(x):
    return shutil.which(x) if x else None


def find_clangxx():
    """PATH first, then the newest /usr/lib/llvm-*/bin/clang++ (mirrors
    Penstock's own 23..19 probe order)."""
    w = which("clang++")
    if w:
        return w
    for v in (23, 22, 21, 20, 19):
        for cand in glob.glob("/usr/lib/llvm-%d/bin/clang++" % v):
            if os.path.isfile(cand):
                return cand
    return None


def sh(cmd, timeout=300, cwd=None):
    p = run_cmd(cmd, timeout, cwd)
    if p is None:
        return None, "timeout/missing: %s" % " ".join(cmd[:3])
    return p.returncode == 0, (p.stdout or "") + (p.stderr or "")


def head(text, n, what):
    lines = text.splitlines()
    if len(lines) <= n:
        return text
    return "\n".join(lines[:n]) + "\n... (%d of %d %s lines shown)" % (
        n, len(lines), what)


# ---------------------------------------------------------------- IR/disasm

def extract_ll_function(ll_text, needle="hot"):
    """Return the textual `define` block of the first function whose
    (mangled) name contains needle, or None."""
    out = []
    inside = False
    for line in ll_text.splitlines():
        if not inside and line.startswith("define ") and ("@" + needle) in line:
            inside = True
        if inside:
            out.append(line)
            if line == "}":
                return "\n".join(out)
    return None if not inside else "\n".join(out)


def find_symbol(exe, needle="hot"):
    """Find the symbol containing `needle` via nm; prefer exact matches."""
    ok, out = sh(["nm", exe])
    if not ok or not out:
        return None
    exact, fuzzy = [], []
    for m in re.finditer(r"^\s*([0-9a-fA-F]+)\s+\w\s+(\S+)", out, re.M):
        sym = m.group(2)
        if needle == sym:
            exact.append(sym)
        elif needle in sym:
            fuzzy.append(sym)
    for lst in (exact, fuzzy):
        if lst:
            lst.sort(key=len)
            return lst[0]
    return None


def disassemble(exe, sym, source=True):
    args = ["objdump", "--disassemble=" + sym, "-l"]
    if source:
        args.append("-S")
    ok, out = sh(args + [exe])
    if not ok or not out.strip():
        ok, out = sh(["objdump", "-d", exe])
        if ok and sym:
            # carve the function out of the full disassembly
            m = re.search(r"^%s[0-9a-zA-Z_$.]*:.*?(?=^[0-9a-zA-Z_$.]+:|\Z)"
                          % re.escape(sym), out, re.M | re.S)
            if m:
                return m.group(0)
        return None
    return out


# ---------------------------------------------------------------- census

VEC_FP = re.compile(r"^(v?fmadd|vfmul|vfadd|vfsub|vfdiv|vmul|vadd|vsub|vdiv|"
                    r"vmin|vmax|vmovddup|vpermil|vunpck|vbroadcast|"
                    r"vinsertf|vextractf|fma)")
SCALAR_FP = re.compile(r"^(fmul|fadd|fsub|fdiv|fmin|fmax|sqrtsd|sqrtss|"
                       r"movsd|movss|ucomisd|ucomiss|comisd|comiss|cvt|"
                       r"xorpd|xorps|andpd|addsd|addss|subsd|mulsd|divsd|"
                       r"mulss|divss|subss)")
INT_VEC = re.compile(r"^(vpadd|vpsub|vpmul|vpand|vpor|vpxor|vpshuf|vpack|"
                     r"vmovdq|vmovd|vpaddd|vpmov|vptest|vpcmp|vmovapd|"
                     r"vmovupd|vmovups|vmovdqu|vpmovzx|vpmovsx)")
BRANCH = re.compile(r"^j")
CALL = re.compile(r"^call")
LOADS = re.compile(r"^(mov|movq|movl|movz|movs|lea|xchg|push|pop)")


def census(disasm):
    counts = {"instructions": 0, "vector_fp": 0, "scalar_fp": 0,
              "int_vector": 0, "div": 0, "mul": 0, "shift": 0,
              "call": 0, "branch": 0, "ret": 0, "mem": 0, "other": 0}
    for m in re.finditer(r"^\s+[0-9a-f]+:\s+(?:[0-9a-f]{2}\s+)+\s*(\S+)",
                         disasm, re.M):
        mn = m.group(1)
        counts["instructions"] += 1
        if VEC_FP.match(mn):
            counts["vector_fp"] += 1
        elif SCALAR_FP.match(mn):
            counts["scalar_fp"] += 1
        elif INT_VEC.match(mn):
            counts["int_vector"] += 1
        elif mn.startswith("div"):
            counts["div"] += 1
        elif mn.startswith(("mul", "imul")):
            counts["mul"] += 1
        elif mn.startswith(("shl", "shr", "sar", "rol", "ror", "sal")):
            counts["shift"] += 1
        elif CALL.match(mn):
            counts["call"] += 1
        elif BRANCH.match(mn):
            counts["branch"] += 1
        elif mn.startswith("ret"):
            counts["ret"] += 1
        elif LOADS.match(mn):
            counts["mem"] += 1
        else:
            counts["other"] += 1
    return counts


def observations(freshet_c, rival_c, freshet_ir, rival_ir):
    obs = []
    if rival_c["vector_fp"] > 0 and freshet_c["vector_fp"] == 0:
        obs.append("The rival emits **%d vector FP instructions** in the hot "
                   "function while Freshet emits **none** — the rival "
                   "vectorised this loop and Freshet stayed scalar. Check "
                   "Freshet's backend remarks (in this report) and the "
                   "`@vectorize` annotation / F0902 notes." %
                   rival_c["vector_fp"])
    if freshet_c["vector_fp"] > 0 and rival_c["vector_fp"] == 0:
        obs.append("Freshet emits **%d vector FP instructions** while the "
                   "rival emits none (the rival may be scalar by algorithm "
                   "or memory-bound — compare TIME before reading this as a "
                   "win)." % freshet_c["vector_fp"])
    if freshet_c["div"] > rival_c["div"]:
        obs.append("Freshet executes **%d division instructions** vs the "
                   "rival's %d (div/rem shape: F0401/F0402 territory — "
                   "strength-reduction opportunities)." %
                   (freshet_c["div"], rival_c["div"]))
    if freshet_c["instructions"] > 2 * max(rival_c["instructions"], 1):
        obs.append("Freshet's hot function is **~%.1fx longer** "
                   "(%d vs %d instructions) — look for missed dead-code "
                   "elimination, guards surviving from checked builds, or "
                   "over-inflation from unrolling." %
                   (freshet_c["instructions"] / max(rival_c["instructions"], 1),
                    freshet_c["instructions"], rival_c["instructions"]))
    if freshet_c["call"] > rival_c["call"]:
        obs.append("Freshet performs **%d calls** in the hot function vs the "
                   "rival's %d — inlining candidates (Penstock's @inline / "
                   "Stage A1) or runtime dispatch overhead." %
                   (freshet_c["call"], rival_c["call"]))
    if freshet_c["branch"] > 2 * max(rival_c["branch"], 1):
        obs.append("Freshet branches **%d times** vs the rival's %d — "
                   "lane-masking or bounds-check residue (F0902/F0923: the "
                   "BCE pass) may be serialising the loop." %
                   (freshet_c["branch"], rival_c["branch"]))
    if rival_c["int_vector"] > 0 and freshet_c["int_vector"] == 0:
        obs.append("The rival uses **%d integer SIMD instructions**; "
                   "Freshet uses none — integer loop not packed." %
                   rival_c["int_vector"])
    for name, ir, other in (("Freshet", freshet_ir, rival_ir),
                            ("the rival", rival_ir, freshet_ir)):
        if ir and "<4 x double>" in ir and other and "<4 x double>" not in other:
            obs.append("%s's IR contains `<4 x double>` vector IR while "
                       "the other does not — 256-bit-wide FP vectorisation "
                       "present in %s only." % (name, name))
    if not obs:
        obs.append("No gross static difference found — the loss is likely "
                   "scheduling, alignment or micro-op selection; consult "
                   "the perf annotation (if present) for cycle-level "
                   "attribution.")
    return obs


# ---------------------------------------------------------------- perf

def perf_available():
    ok, out = sh(["perf", "stat", "-e", "cycles,instructions", "--", "true"],
                 timeout=30)
    return bool(ok)


def perf_record(exe, data, timeout=300):
    ok, out = sh(["perf", "record", "-F", "997", "-o", data, "--", exe],
                 timeout=timeout)
    return bool(ok), out


def perf_annotate(data, sym):
    for cmd in (["perf", "annotate", "--stdio", "-i", data, sym],
                ["perf", "annotate", "--stdio", "-i", data, "--symbol=" + sym],
                ["perf", "report", "--stdio", "-i", data, "--sort", "symbol"]):
        ok, out = sh(cmd, timeout=120)
        if ok and out.strip():
            # keep only the target symbol region when possible
            if "annotate" in cmd[1]:
                m = re.search(r"^[%s]+" % re.escape(sym), out, re.M)
                if not m:
                    m = re.search(r"^_?[0-9A-Za-z_$.]*%s.*?:"
                                  % re.escape(sym), out, re.M)
                if m:
                    tail = out[m.start():]
                    return "\n".join(tail.splitlines()[:400])
            return head(out, 400, "perf output")
    return None


# ---------------------------------------------------------------- builders

class Annotator:
    def __init__(self, args):
        self.args = args
        self.penstock = args.penstock or os.environ.get("PENSTOCK") or which("penstock") \
            or sibling("bin/penstock")
        self.clangxx = find_clangxx()
        self.gxx = which("g++") or which("c++")
        self.rustc = args.rustc or os.environ.get("RUSTC") or which("rustc")
        self.use_perf = (args.perf == "force") or (
            args.perf == "auto" and perf_available())
        self.perf_note = ("perf + hardware counters detected"
                          if self.use_perf else
                          "perf not usable here — static annotation only "
                          "(run this on the self-hosted perf runner for "
                          "cycle attribution)")

    # -- builds returning (exe, ll_text_or_None, notes)
    def build_freshet(self, src, exe):
        notes = []
        ll = None
        cmd = [self.penstock, "--emit-final-ir", "-g"] + \
            shlex(self.args.freshet_flags) + [src, "-o", exe]
        ok, out = sh(cmd, timeout=600)
        if not ok:
            return None, None, ["penstock build failed: %s" % head(out, 6, "log")]
        ll_path = exe + ".final.ll"
        if os.path.isfile(ll_path):
            ll = open(ll_path).read()
        else:
            for cand in (os.path.abspath("a.ll"),):
                if os.path.isfile(cand):
                    ll = open(cand).read()
            notes.append("final IR file not found (%s) — fell back to -S IR"
                         % ll_path)
        # backend remarks: run a second -S build with --opt-remarks
        rok, rout = sh([self.penstock, "--opt-remarks", "-S"] +
                       shlex(self.args.freshet_flags) + [src, "-o", exe + ".rmk"],
                       timeout=600)
        remarks = head((rout or ""), 160, "remark lines") if rok else ""
        return exe, ll, notes + [remarks] if remarks else notes

    def build_cpp(self, src, exe):
        notes, ll = [], None
        if self.clangxx:
            ok, out = sh([self.clangxx, "-O2", "-std=c++17",
                          "-ffp-contract=off", "-S", "-emit-llvm", src,
                          "-o", exe + ".ll"], timeout=300)
            if ok:
                ll = open(exe + ".ll").read()
            else:
                notes.append("clang++ IR emission failed: %s" % head(out, 4, "log"))
            ok, out = sh([self.clangxx, "-O2", "-std=c++17",
                          "-ffp-contract=off", "-g", src, "-o", exe, "-lm"],
                         timeout=300)
            if not ok:
                return None, None, notes + ["clang++ binary build failed"]
            return exe, ll, notes
        if self.gxx:
            ok, out = sh([self.gxx, "-O2", "-std=c++17", "-ffp-contract=off",
                          "-g", src, "-o", exe, "-lm"], timeout=300)
            if not ok:
                return None, None, ["g++ binary build failed"]
            notes.append("clang++ not found — LLVM IR section unavailable "
                         "for this rival (disassembly + census still "
                         "reported); g++ built the binary.")
            return exe, None, notes
        return None, None, ["no C++ compiler found"]

    def build_rust(self, src, exe):
        notes, ll = [], None
        ok, out = sh([self.rustc, "--edition", "2021", "-C", "opt-level=3",
                      "-C", "debuginfo=1", src, "-o", exe], timeout=600)
        if not ok:
            return None, None, ["rustc binary build failed: %s" % head(out, 6, "log")]
        ok, out = sh([self.rustc, "--edition", "2021", "-C", "opt-level=3",
                      "--emit=llvm-ir", src, "-o", exe + ".ll"], timeout=600)
        if ok and os.path.isfile(exe + ".ll"):
            ll = open(exe + ".ll").read()
        else:
            notes.append("rustc --emit=llvm-ir failed: %s" % head(out, 4, "log"))
        return exe, ll, notes


def shlex(s):
    if not s:
        return []
    import shlex
    return shlex.split(s)


def sibling(rel):
    here = HERE
    for _ in range(3):
        cand = os.path.join(os.path.dirname(here), rel)
        if os.path.isfile(cand):
            return cand
        here = os.path.dirname(here)
    return None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True, help="results.json from bench.py")
    ap.add_argument("--workdir", default="/tmp/flang-annot")
    ap.add_argument("--out", default=None)
    ap.add_argument("--threshold", type=float, default=1.05)
    ap.add_argument("--perf", choices=["auto", "force", "off"], default="auto")
    ap.add_argument("--max-ir-lines", type=int, default=260)
    ap.add_argument("--max-dis-lines", type=int, default=240)
    ap.add_argument("--penstock")
    ap.add_argument("--rustc")
    ap.add_argument("--freshet-flags", default="")
    args = ap.parse_args()

    with open(args.results) as f:
        data = json.load(f)
    results = data.get("results", [])
    outdir = args.out or os.path.join(os.path.dirname(
        os.path.abspath(args.results)), "reports")
    losses_dir = os.path.join(outdir, "losses")
    os.makedirs(losses_dir, exist_ok=True)
    os.makedirs(args.workdir, exist_ok=True)

    ann = Annotator(args)
    log("Freshet-lang loss annotation (fsht-01:01)")
    log("  penstock : %s" % (ann.penstock or "NOT FOUND"))
    log("  clang++  : %s" % (ann.clangxx or "not found (C++ IR skipped)"))
    log("  rustc    : %s" % (ann.rustc or "not found (rust pairs skipped)"))
    log("  perf     : %s" % ann.perf_note)
    if not ann.penstock:
        log("  no penstock — nothing to annotate; aborting")
        return 2

    kdir_base = os.path.join(HERE, "kernels")
    index = ["# Freshet losses — annotated (fsht-01:01)", "",
             "Every pair below is a kernel where another language beat "
             "Freshet by more than the configured threshold. Each report "
             "contains the final optimised LLVM IR and source-annotated "
             "disassembly of BOTH hot functions, a measured instruction "
             "census, and perf cycle attribution when available.", ""]
    n_reports = 0

    for r in results:
        kname = r["kernel"]
        if r.get("verdicts", {}).get("freshet") == "ok":
            pass
        ft = r.get("times", {}).get("freshet")
        if ft is None:
            continue
        for lang in ("idiomatic", "tuned", "rust"):
            if r.get("verdicts", {}).get(lang) != "loss":
                continue
            rt = r["times"][lang]
            ratio = ft / rt
            log("  %s vs %s: loss (%.2fx) — annotating" % (kname, lang, ratio))
            report = build_report(ann, args, kname, kdir_base, lang, ft, rt,
                                  ratio)
            path = os.path.join(losses_dir, "%s-vs-%s.md" % (kname, lang))
            with open(path, "w") as f:
                f.write(report)
            index.append("- [%s lost to %s by %.2fx](losses/%s-vs-%s.md)"
                         % (kname, LANG_LABEL[lang], ratio, kname, lang))
            n_reports += 1

    if n_reports == 0:
        index.append("- No losses at the current threshold — nothing to "
                     "annotate.")
    with open(os.path.join(losses_dir, "..", "INDEX.md"), "w") as f:
        f.write("\n".join(index) + "\n")
    log("")
    log("%d report(s) under %s; index: %s" % (
        n_reports, losses_dir, os.path.join(outdir, "INDEX.md")))
    return 0


def build_report(ann, args, kname, kdir_base, lang, ft, rt, ratio):
    kdir = os.path.join(kdir_base, kname)
    wd = os.path.join(args.workdir, "%s_%s" % (kname, lang))
    os.makedirs(wd, exist_ok=True)
    sections = []
    sections.append("# `%s` — Freshet lost to %s by %.2fx (fsht-01:01)\n"
                    % (kname, LANG_LABEL[lang], ratio))
    sections.append("| | freshet | %s |\n|---|---|---|\n"
                    "| hot-region time (best) | %.1f ms | %.1f ms |"
                    % (LANG_LABEL[lang], ft / 1e6, rt / 1e6))
    sections.append("> Kernel: **%s** (spec: `benchmarks/KERNELS.md`). "
                    "Hot function: `hot` in every implementation. "
                    "Checksum agreement was checked by `bench.py` before "
                    "this report was generated." % kname)

    fexe, fir, fnotes = ann.build_freshet(os.path.join(kdir, "freshet.fsht"),
                                          os.path.join(wd, "freshet"))
    if lang == "rust":
        rex, rir, rnotes = ann.build_rust(os.path.join(kdir, "safe.rs"),
                                          os.path.join(wd, "rust"))
    else:
        rex, rir, rnotes = ann.build_cpp(
            os.path.join(kdir, "idiomatic.cpp" if lang == "idiomatic"
                         else "tuned.cpp"), os.path.join(wd, lang))

    # ---- LLVM IR
    for title, ir in (("Freshet — final optimised LLVM IR (`hot`)", fir),
                      ("%s — LLVM IR (`hot`)" % LANG_LABEL[lang], rir)):
        if ir:
            fn = extract_ll_function(ir, "hot")
            body = fn or head(ir, 20, "file")
            sections.append("## %s\n\n```llvm\n%s\n```" % (title, head(
                body, args.max_ir_lines, "IR")))
        else:
            sections.append("## %s\n\n(IR unavailable — see notes at the "
                            "end of this report)" % title)

    # ---- disassembly + census
    cens = {}
    for tag, exe in (("freshet", fexe), (lang, rex)):
        title = "Freshet" if tag == "freshet" else LANG_LABEL[lang]
        if not exe:
            sections.append("## %s — disassembly\n\n(binary unavailable)"
                            % title)
            cens[tag] = {}
            continue
        sym = find_symbol(exe, "hot")
        if not sym:
            sections.append("## %s — disassembly\n\n(no `hot` symbol found)"
                            % title)
            cens[tag] = {}
            continue
        dis = disassemble(exe, sym)
        c = census(dis or "")
        cens[tag] = c
        sections.append("## %s — disassembly (`%s`)\n\n```asm\n%s\n```"
                        % (title, sym, head(dis or "", args.max_dis_lines,
                                            "disassembly")))

    if cens.get("freshet") and cens.get(lang):
        fc, rc = cens["freshet"], cens[lang]
        rows = ["| metric | freshet | %s |" % LANG_LABEL[lang],
                "|---|---|---|"]
        for k in ("instructions", "vector_fp", "scalar_fp", "int_vector",
                  "div", "mul", "shift", "call", "branch", "ret", "mem",
                  "other"):
            rows.append("| %s | %s | %s |" % (k, fc.get(k, "?"), rc.get(k, "?")))
        sections.append("## Instruction census (measured from the "
                        "disassembly above)\n\n" + "\n".join(rows))
        sections.append("## Observations\n\n" + "\n".join(
            "- " + o for o in observations(fc, rc, fir, rir)))

    # ---- perf
    sections.append("## perf annotation\n\n" + ann.perf_note + "\n")
    if ann.use_perf:
        for tag, exe in (("freshet", fexe), (lang, rex)):
            title = "Freshet" if tag == "freshet" else LANG_LABEL[lang]
            if not exe:
                continue
            data = os.path.join(wd, "perf_%s.data" % tag)
            ok, _ = perf_record(exe, data)
            if not ok:
                sections.append("### %s\n\nperf record failed (run it on "
                                "the self-hosted perf runner)." % title)
                continue
            sym = find_symbol(exe, "hot") or "hot"
            pa = perf_annotate(data, sym)
            sections.append("### %s (`%s`)\n\n%s" % (
                title, sym, ("```\n" + (pa or "perf annotate produced no "
                "output for this symbol") + "\n```" if pa else
                "perf annotate unavailable for `%s`" % sym)))

    # ---- notes
    notes = [n for n in (fnotes + rnotes) if n]
    if notes:
        sections.append("## Build notes\n\n" + "\n".join("- %s" % n
                                                         for n in notes))
    sections.append("## Reproduce\n\n```sh\n"
                    "benchmarks/bench.py --kernels %s\n"
                    "benchmarks/annotate.py --results results.json\n```\n"
                    % kname)
    return "\n\n".join(sections) + "\n"


if __name__ == "__main__":
    sys.exit(main())
