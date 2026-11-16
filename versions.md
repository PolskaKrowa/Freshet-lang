# Freshet versioning (fsht-01:01)

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
* **Minor bumps (`yy`)** add features or clarifications without breaking
  programs that compiled against the previous version.
* **Major bumps (`xx`)** carry any change that alters the meaning of an
  already-valid program — semantic fixes, removed diagnostics, changed
  defaults. A major bump MAY deprecate; removal happens no earlier than
  one major version after the deprecation notice.
* Versions are tagged in git; because git refnames cannot contain a
  colon, the tag for `fsht-xx:yy` is spelled `fsht-xx-yy` (this
  repository: `fsht-01-01`). The current standard is
  [fsht-01:01](spec/README.md).

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
4. fsht-01:01 roadmap items (dynamic containers, user traits, const
   generics, the expanded library, the portable runtime) exist ONLY as
   registry entries with target versions — the spec chapters stay a
   snapshot of today.

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
