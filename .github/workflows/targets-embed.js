#!/usr/bin/env node
// Minimal embedder harness for the fsht-03:03 target matrix
// (.github/workflows/targets.yml, wasm32-standalone rows).
//
// Loads the standalone wasm module Penstock emitted, provides the
// embedder-side surface the runtime's platforms/wasm layer expects —
// the `frt_config` globals carrying the FRT_* knobs (chapter 25 §4:
// standalone wasm receives knobs through the embedder, and defaults
// silently when they are absent or unparsable), the module's memory
// when it imports one, and stdout shims for the print surface — then
// calls the exported entry point and relays the program's stdout. The
// workflow compares that stdout against this repository's golden:
// the tested-before-declared gate, ch. 25 §3.
"use strict";

const fs = require("fs");

function embedderGlobals() {
  // FRT_* from the environment become frt_* globals (unset or
  // unparsable => 0, which the runtime reads as "use the documented
  // default" — the silent-default rule).
  const knobs = ["threads", "chunk", "serial_cutoff", "dstk_reserve"];
  const g = {};
  for (const k of knobs) {
    const raw = process.env["FRT_" + k.toUpperCase()];
    if (raw === undefined || !/^-?\d+$/.test(raw)) { g["frt_" + k] = 0; }
    else { g["frt_" + k] = Number(raw); }
  }
  g["frt_affinity"] = process.env.FRT_AFFINITY === "1" ? 1 : 0;
  g["frt_smt_interleave"] = process.env.FRT_SMT_INTERLEAVE === "1" ? 1 : 0;
  g["frt_timing"] = process.env.FRT_TIMING === "1" ? 1 : 0;
  g["frt_prof_out"] = 0;
  return g;
}

let memory = null;

function writeStdout(s) { process.stdout.write(s); }

// stdout shims for the print surface the standalone lowering imports.
// Two conventions are handled: numeric-argument print builtins, and
// (ptr, len) byte writes into the module's linear memory. Anything
// else fails loudly so an unexpected import is never silently wrong.
function printShim(name) {
  if (/^(fd_write|write|write_stdout|print_bytes)$/.test(name)) {
    return function (fd, ptr, len) {
      if (fd !== undefined && fd !== 1 && fd !== 2) { return 0; }
      const buf = new Uint8Array(memory.buffer, ptr, len);
      writeStdout(new TextDecoder("utf-8").decode(buf));
      return len;
    };
  }
  if (/^(putchar|print_char|print_u8)$/.test(name)) {
    return function (c) { writeStdout(String.fromCharCode(c)); return 0; };
  }
  if (/^(print_i64|print_i32|print_int)$/.test(name)) {
    return function (v) { writeStdout(String(v)); return 0; };
  }
  if (/^(print_u64|print_u32|print_uint)$/.test(name)) {
    return function (v) { writeStdout(String(v < 0 ? v + 18446744073709551616 : v)); return 0; };
  }
  if (/^print_f64$/.test(name)) {
    return function (v, digits) {
      writeStdout(Number(v).toFixed(digits === undefined ? 6 : digits));
      return 0;
    };
  }
  if (/^(println|newline)$/.test(name)) {
    return function () { writeStdout("\n"); return 0; };
  }
  return function () {
    console.error("targets-embed: unhandled import function '" + name + "'");
    process.exit(3);
  };
}

async function main() {
  const path = process.argv[2];
  const bytes = fs.readFileSync(path);
  const mod = await WebAssembly.compile(bytes);

  const imports = {};
  for (const imp of WebAssembly.Module.imports(mod)) {
    imports[imp.module] = imports[imp.module] || {};
    if (imp.kind === "memory") {
      memory = new WebAssembly.Memory({ initial: 16, maximum: 65536 });
      imports[imp.module][imp.name] = memory;
    } else if (imp.kind === "global") {
      const g = embedderGlobals();
      const type = /dstk|reserve/.test(imp.name) ? "i64" : "i32";
      imports[imp.module][imp.name] =
        new WebAssembly.Global({ value: type, mutable: true }, g[imp.name] || 0);
    } else if (imp.kind === "function") {
      imports[imp.module][imp.name] = printShim(imp.name);
    }
  }

  const inst = await WebAssembly.instantiate(mod, imports);
  if (!memory && inst.exports.memory) { memory = inst.exports.memory; }

  const entry = inst.exports.main || inst.exports._main ||
    inst.exports.__main_void || null;
  if (!entry) {
    console.error("targets-embed: no exported entry point in " + path);
    process.exit(2);
  }
  entry();
}

main().catch((e) => { console.error("targets-embed: " + e); process.exit(1); });
