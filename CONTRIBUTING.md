# Contributing to the Freshet standard (fsht-03:03)

This repository is designed to be modified: the standard is a living
document, the registry is a ledger, and the suites grow with every
feature. This file is the rulebook for changing it.

## The feature lifecycle

1. **Proposed** — open an issue describing the feature, its subset
   placement (`aa.bb`, see [registry/subsets.md](registry/subsets.md))
   and the design. Discussion happens on the issue.
2. **Accepted** — a PR adds the registry entry with status `accepted`
   and a target version (`fsht-vv:ww`). The design constraint text goes
   in the entry. Accepted designs are commitments, not curiosities: the
   fsht-03 roadmap entries were all in this state until their
   2026-11-19 ratification; the next accepted designs will carry
   fsht-04 targets.
3. **Normative** — when the reference implementation ships the feature,
   the spec chapters gain the normative text and the entry flips to
   `normative`. The identifier's `xx:yy` MUST be the version that first
   shipped it.
4. **Updated** — every later change updates the entry's **History**
   block with a reference per version (see
   [versions.md](versions.md)). This is mandatory: a feature whose
   behaviour changed without a history reference is a defect in this
   repository, not a detail.

## Rules of the specification

* The spec is a **snapshot of shipped behaviour**. Never add
  speculative text to `spec/` — the roadmap lives in the registry only.
* Per-chapter EBNF is normative; the consolidated grammar is
  informative. Update both when the grammar changes.
* RFC-2119 keywords (MUST/SHOULD/MAY) are load-bearing; a rule that is
  optional must not be written as MUST.
* Diagnostic IDs are never renumbered or reused; a split creates new IDs
  and updates the registry history of the split family.
* A spec change that alters the meaning of a valid program requires a
  major-version bump and deprecation notices one major version ahead.

## Rules of the suites

* Every new feature lands with **suite coverage in the same PR**:
  corpus entries (positive + golden), negative entries for the rules it
  introduces, a fuzz-generator block when the grammar surface grows, and
  benchmark kernels when the feature is on the performance path.
* Goldens are derived from the normative rules, never from running the
  compiler once and pasting the output (that would make the compiler the
  oracle). Cross-check arithmetic independently (python is fine).
* Benchmarks follow [benchmarks/KERNELS.md](benchmarks/KERNELS.md):
  four implementations of every kernel, identical checksums, the
  TIME/CS output contract, and the FP determinism rules (no refactors,
  no FMA, exact expression order).
* A benchmark must be honest about what it compares (see each kernel's
  policy notes — e.g. `radix_sort` deliberately pits Freshet's
  hand-written radix against `std::sort` and `sort_unstable`, because
  that is the real choice a user faces in fsht-01:01).

## Practical notes

* 4-space indent in code; 78-100 column wrap in markdown and code
  reviews; line comments `//` in Freshet sources.
* `penstock fmt` passes on every committed `.fsht` file (the formatter's
  token-identity gate makes this safe).
* CI (`.github/workflows/`) runs the suite self-check on every PR, the
  conformance suite when a Penstock checkout is available, and the
  fsht-03:03 target matrix (`targets.yml`) on its cadence — a target
  row that is not green MUST NOT be declared supported (spec ch. 25 §3).
  Keep all three green.

## Committing

Sign off your commits (`git commit -s`). Contribution licensing is
Apache-2.0 for code and CC-BY-4.0 for specification prose
([LICENSE.md](LICENSE.md)).
