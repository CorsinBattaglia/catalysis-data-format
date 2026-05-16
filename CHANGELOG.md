# Changelog
All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-05-16

This release marks the initial adaptation of the Battery Data Format into the **Catalysis Data Format (CDF)**, targeting electrolyser and electrocatalysis time-series data.

### Forked from
- Upstream: [battery-data-alliance/battery-data-format](https://github.com/battery-data-alliance/battery-data-format) (Apache-2.0)
- Fork: [catalysis-data-alliance/catalysis-data-format](https://github.com/catalysis-data-alliance/catalysis-data-format)

### Added
- 8 new optional columns in the CDF column registry (`src/cdf/normalize/spec.py`):
  - `working_electrode_potential_volt` — Working electrode potential (V)
  - `counter_electrode_potential_volt` — Counter electrode potential (V)
  - `reference_electrode_potential_volt` — Reference electrode potential (V)
  - `cell_resistance_ohm` — Total ohmic cell resistance (ohm)
  - `faradaic_efficiency_percent` — Faradaic efficiency (%)
  - `gas_flow_rate_ml_min` — Gas outlet flow rate (mL/min)
  - `electrolyte_ph` — Electrolyte pH (dimensionless)
  - `product_concentration_mol_l` — Product concentration (mol/L)
- CDF-specific IRI base (`https://w3id.org/catalysis-data-format/ontology/catalysis-data-format#`) for the 8 new columns.
- CI pipeline with lint/type/tests/docs and build/twine checks (inherited from upstream).
- Sphinx docs with pydata theme and converted notebook examples (inherited from upstream).
- Unit tests for IO, registry, validation, repair, CLI, and raw conversion (inherited from upstream).
- Community files: CONTRIBUTING, CODE_OF_CONDUCT, SECURITY (inherited from upstream).
- Release workflow for TestPyPI/PyPI publication via GitHub Actions (inherited from upstream).

### Changed
- **Package scope**: Battery cycler data → electrolyser / electrocatalysis time-series data.
- **Package rename**: `batterydf` → `catalysisdf` (PyPI); Python import and CLI renamed from `bdf` to `cdf`.
- **Source directory**: `src/bdf/` → `src/cdf/`; all internal imports updated accordingly.
- **File extension**: `.bdf` → `.cdf` throughout I/O, CLI, and documentation.
- **CLI entry point**: `bdf` → `cdf`.
- **Entry-point group**: `bdf.data_sources` → `cdf.data_sources`.
- **Environment variables**: `BDF_*` prefix → `CDF_*` (e.g. `CDF_FORMAT_WARNINGS`, `CDF_CRAWL_CACHE`, `CDF_ONTOLOGY_PATH`).
- **Error class**: `BDFValidationError` → `CDFValidationError`.
- **README**: Rewritten for catalysis/electrolyser scope; updated column table, file extension, install instructions, and fork attribution.
- Enriched packaging metadata (keywords, description, homepage URLs).
