# Feature registry (fsht-01:01)

The registry is the single ledger of every Freshet feature: what exists
today (normative), what is accepted for a future version, what is
proposed, what is deprecated — with permanent identifiers and full
version histories.

## Entry format

```markdown
### fsht-xx:yy-aa.bb.cc — <title>

Status: normative | accepted (target fsht-vv:ww) | proposed | deprecated
Spec: <chapter link> or — (not yet in spec)

<one short paragraph: the rule/feature>

History:
- fsht-xx:yy — first standardised / first accepted.
- fsht-vv:ww — <what changed; deprecation notices name removal targets>.
```

* The identifier's `xx:yy` is the version where the feature FIRST became
  part of the standard; it never changes.
* Every later change MUST appear in the History block (see
  [versions.md](../versions.md) for the rules and the worked example).
* fsht-01:01 entries with intra-version corrections list them as
  `fsht-01:01 (correction)` — corrections made while ratifying the
  first snapshot, mined from the reference implementation's own audit
  trail.

## Contents

| file | major subset (`aa`) |
|---|---|
| [features/01-core.md](features/01-core.md) | 01 — core language (lexical, declarations, attributes, control flow) |
| [features/02-data-types.md](features/02-data-types.md) | 02 — data types (scalars, structs, arrays, spans, SoA, strings, enums, Option/Result) |
| [features/03-memory.md](features/03-memory.md) | 03 — memory (allocation, ownership, unsafe, data stacks) |
| [features/04-parallelism.md](features/04-parallelism.md) | 04 — parallelism (parfor, reductions, scheduling) |
| [features/05-io.md](features/05-io.md) | 05 — I/O and the `fsh` module |
| [features/06-generics.md](features/06-generics.md) | 06 — generics and future traits |
| [features/07-modules-ffi.md](features/07-modules-ffi.md) | 07 — modules and FFI |
| [features/08-numeric-semantics.md](features/08-numeric-semantics.md) | 08 — numeric semantics |
| [features/09-diagnostics.md](features/09-diagnostics.md) | 09 — diagnostics and future analysis passes |
| [features/10-toolchain.md](features/10-toolchain.md) | 10 — toolchain, runtime and targets |

The master index table is [features.md](features.md); the subset
taxonomy is [subsets.md](subsets.md).

## How features are added

1. Open an issue describing the feature, its subset placement and the
   design.
2. A PR adds the registry entry (status `proposed`, no version yet) and,
   when the design is ratified, `accepted` with its target version
   (`fsht-vv:ww` — the version that will first ship it).
3. When the reference implementation ships it and the spec chapters gain
   the normative text, the entry's status flips to `normative` and the
   identifier's version becomes the shipping version.

Roadmap entries (fsht-02/03 targets) are accepted designs tracked this
way — the spec itself only ever describes shipped behaviour.
