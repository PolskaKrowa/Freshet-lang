# Licence

The Freshet-lang repository is dual-licensed by content class:

* **Specification prose** — everything under `spec/`, `registry/`,
  `versions.md`, `CONTRIBUTING.md`, `README.md` and the `*.md`
  documentation of `tests/` and `benchmarks/` — is licensed under the
  Creative Commons Attribution 4.0 International licence (CC-BY-4.0):
  https://creativecommons.org/licenses/by/4.0/
  (human-readable summary:
  https://creativecommons.org/licenses/by/4.0/deed.en). You may share
  and adapt the standard for any purpose, including commercially, provided
  you give appropriate credit, link the licence, and indicate changes.

* **Code** — the Freshet programs under `tests/` and
  `benchmarks/` (`*.fsht`, `*.cpp`, `*.rs`), the harnesses
  (`bench.py`, `annotate.py`, `fuzz/*.py`, `run_suite.sh`) and the CI
  workflows — is licensed under the Apache Licence, Version 2.0; the full
  text is in [LICENSE-APACHE-2.0.txt](LICENSE-APACHE-2.0.txt). This
  matches the licence of the reference compiler (Penstock), so test
  programs and kernels can flow in both directions.

When contributing, you agree your contributions are licensed under these
same terms (Apache-2.0 for code, CC-BY-4.0 for specification prose).
