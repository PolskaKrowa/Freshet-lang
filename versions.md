# Freshet versioning (fsht-03:03)

This document defines how the Freshet standard and its features are
numbered, and how a feature's history is recorded across versions. It is
normative for everything contributed to this repository.

## Standard versions — `fsht-xx:yy`

A version of the Freshet standard is denoted

```
fsht-xx:yy        xx = major (two digits), yy = minor (two digits)
```

* **`fsht-01:01`** is the first ratified standard: an exact, normative
  snapshot of what the reference compiler (Penstock 0.1.0-INDEV)
  implements — nothing speculative inside the spec chapters.
* **`fsht-02:01`** ratified dynamic collections: `Vec<T>` with the
  ownership-integrated move/drop model (registry 02.09.01–02.09.02).
* **`fsht-02:02`** ratified user-defined traits with static dispatch
  (registry 06.02.01).
* **`fsht-02:03`** ratified const generics and `const fn` (registry
  06.03.01). All three fsht-02 increments are pure extensions — no
  fsht-01:01 program changes meaning.
* **`fsht-03:01`** ratified the expanded standard library: numeric
  text parsing, streaming I/O with `Result` integration, the module
  decomposition, and the checked/saturating/wrapping variants with
  conversion facilities (registry 05.04.01, 05.05.01, 05.06.01,
  08.01.04).
* **`fsht-03:02`** ratified mutable borrows with exclusivity and the
  lifetime/escape refinement (registry 03.02.09, 03.02.10) —
  including the `String` migration onto the tracked container model,
  drop elaboration through user shapes, and the `usize` resolution
  (fixed 64-bit on every target, registry 02.01.05).
* **`fsht-03:03`** ratified the portable, target-aware runtime
  (registry 10.03.02) with the five-target matrix and the
  tested-before-declared gate, closing the fsht-01:01 `--target`
  limitation (10.03.01). Every fsht-03 increment preserves the defined
  behaviour of prior programs; the newly diagnosed shapes were already
  undefined behaviour (dangling views, use-after-free Strings).
* **Minor bumps (`yy`)** add features or clarifications without breaking
  programs that compiled against the previous version.
* **Major bumps (`xx`)** carry any change that alters the meaning of an
  already-valid program — semantic fixes, removed diagnostics, changed
  defaults. A major bump MAY deprecate; removal happens no earlier than
  one major version after the deprecation notice.
* Versions are tagged in git; because git refnames cannot contain a
  colon, the tag for `fsht-xx:yy` is spelled `fsht-xx-yy` (this
  repository: `fsht-01-01`, `fsht-02-01`, `fsht-02-02`, `fsht-02-03`,
  `fsht-03-01`, `fsht-03-02`, `fsht-03-03`). The distributed tarballs
  exclude the `.git` directory — tag the matching import commit when
  importing a tarball. The current standard is
  [fsht-03:03](spec/README.md).

### Version history

| version | contents |
|---|---|
| fsht-01:01 | baseline snapshot of Penstock 0.1.0-INDEV — chapters 00–19 |
| fsht-02:01 | dynamic collections + container move semantics (ch. 20, registry 02.09.01–02) |
| fsht-02:02 | user-defined traits, static dispatch (ch. 21, registry 06.02.01) |
| fsht-02:03 | const generics + `const fn` (ch. 22, registry 06.03.01) |
| fsht-03:01 | expanded standard library: parsing, streaming I/O, modules, checked/saturating/wrapping + conversions (ch. 23, registry 05.04.01/05.05.01/05.06.01/08.01.04) |
| fsht-03:02 | mutable borrows & lifetimes: `&mut` exclusivity (`F0310`), escape analysis (`F0311`), String migration, drop elaboration, `usize` resolved (ch. 24, registry 03.02.09/03.02.10) |
| fsht-03:03 | portable target-aware runtime: decomposition, five-target matrix, tested-before-declared (ch. 25, registry 10.03.02) |

## Feature identifiers — `fsht-xx:yy-aa.bb.cc`

Every feature of the standard carries a permanent identifier:

```
fsht-xx:yy-aa.bb.cc
     |   |  |  └─ cc — the exact feature (atomic_load, malloc_large,
     |   |  |          data representation of a type, ...)
     |   |  └──── bb — the minor subset (allocation, thread task
     |   |            handling, templates, ...)
     |   └─────── aa — the major subset (memory, parallelism, I/O,
     |                data-types, ...)
     └───────── xx:yy — the version in which the feature FIRST
                 became part of the standard
```

Rules:

1. The identifier is allocated when the feature is **accepted** (its
   registry entry exists) and never changes. A feature first shipped in
   fsht-02:03 is forever `fsht-02:03-aa.bb.cc`.
2. `aa` (major subset) and `bb` (minor subset) are defined by the
   [subset taxonomy](registry/subsets.md); `cc` is unique within
   `aa.bb`.
3. Status of a feature: `normative` (in the spec chapters),
   `accepted` (ratified design with a target version, not yet
   implemented), `in development` (accepted feature whose first cut is
   implemented in the reference compiler but not yet ratified — the
   registry entry carries the cut's surface, deferrals and a draft
   spec chapter, all marked non-normative), `proposed` (open design,
   RFC stage), `deprecated` (scheduled for removal in a stated
   version).
4. Roadmap items beyond the ratified surface — the fsht-04 proposals,
   the fsht-03:04 compiler capabilities, async I/O, closures — exist
   ONLY as registry entries with target versions; the spec chapters
   stay a snapshot of shipped behaviour. (The fsht-02 roadmap items
   were ratified 2026-11-19: chapters 20–22 became normative and their
   deferral annotations moved into the registry histories; the
   fsht-03 roadmap items were ratified the same day — chapters 23–25
   became normative, the seven accepted entries flipped with full
   histories, and the ledger below emptied again.)

## Update references — the feature history rule

**A feature that changed in a later version MUST list, inside its
registry entry, a reference for EVERY version in which it changed, in
ascending version order, stating what changed.** Deprecations and
removals are announced there too.

Worked example (illustrative, using the scheme exactly as it will look;
the scenario is hypothetical):

```
### fsht-01:02-04.03.07 — array mutexing policy

Status: normative (fsht-01:02) → updated (fsht-02:01) → partial
deprecation announced (fsht-03:01)

First standardised in fsht-01:02: arrays shared across parfor regions
MUST be mutexed ...

History:
- fsht-01:02 — first standardised.
- fsht-02:01 — array mutexing for architecture `foo` no longer requires
  argument `bar` to be set to value `baz` to prevent races with arrays
  larger than the allocator's large-block threshold for the primary
  allocator. Developers run the allocator exactly as on any other
  architecture. Passing `baz` to `bar` is announced for deprecation.
- fsht-03:01 — passing `baz` to `bar` is formally deprecated; the
  argument is ignored and diagnosed. Removal target: fsht-04:01.
```

Every entry in [registry/features/](registry/features/) follows this
shape: identifier, title, status line, the rule, and the History block.
The master index is [registry/features.md](registry/features.md).

## In-development ledger

Features whose first cut is implemented in the reference compiler but
not yet ratified. Ratifying the version promotes the draft chapter to
normative and removes the deferral annotations that did not make the
cut (they stay as registry history).

Currently empty — the last rows (fsht-02:01–fsht-02:03: 02.09.01,
02.09.02, 06.02.01, 06.03.01; then fsht-03:01–fsht-03:03: 05.04.01,
05.05.01, 05.06.01, 08.01.04, 03.02.09, 03.02.10, 10.03.02) were
ratified on 2026-11-19 and now live in the per-subset entries with
full histories.

## What counts as "changed"

Semantic changes, severity changes, added/removed constraints, ABI or
representation changes, diagnostic behaviour changes, and deprecations
all require a History reference. Purely editorial work does not.

## Compatibility

* Programs valid under fsht-xx:yy SHOULD remain valid under
  fsht-xx:yy+1 (minor guarantees), except where a History reference
  documents a deprecation already announced one major version ahead.
* Conformance statements should name the exact `fsht-xx:yy` they target;
  the [test suite](tests/) is the arbiter.
