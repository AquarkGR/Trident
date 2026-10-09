# csv2parquet CLI
**Date:** 2026-10-09 · **Builder:** sonnet · **Status:** Delivered

## Summary
Asked for a small Python CLI that converts a CSV file to Parquet with an optional `--compression` flag, plus a test using `sample.csv`. Delivered `csv2parquet` (built on pyarrow) and a 10-case pytest suite that passes. It gives a reusable, tested command for turning CSVs into compact Parquet files.

## Decisions
- pyarrow only (no pandas) — smallest dependency set.
- Default compression `snappy`; choices none, snappy, gzip, brotli, lz4, zstd — common codecs, all bundled in pyarrow wheels.
- Refuse to overwrite an existing output unless `--force` — avoids silent data loss.
- Output defaults to the input name with a `.parquet` suffix — convenient default.
- Bad codec rejected by argparse (exit 2) before any file is touched — no partial output.
- Changes left uncommitted; no README — per the plan.

## Sources and licences
| Source | Version | Licence | Used for |
|---|---|---|---|
| pyarrow | 26.0.0 | Apache-2.0 | CSV reading and Parquet writing |
| pytest | 9.1.1 | MIT | Tests (test extra only) |
| cldellow/csv2parquet | n/a | Apache-2.0 | Prior art reviewed; no code copied |

## Verification
| Criterion | Result | Evidence |
|---|---|---|
| `--help` lists input, output, `--compression` | Pass | Exit 0 |
| Default output is valid Parquet | Pass | `PAR1` at start and end |
| 3 rows, columns city, temp_c, date | Pass | Read-back check |
| Values round-trip, temp_c float64 | Pass | 24.5, 13.1, 8.0 |
| snappy, gzip, zstd codecs | Pass | Metadata reports SNAPPY, GZIP, ZSTD |
| Bad codec | Pass | Exit 2, stderr names `bogus`, no file |
| Missing input | Pass | Exit 1, stderr message, no file |
| Existing output | Pass | Refused without `--force`; overwritten with it |
| Test suite | Pass | 10 passed |
| Outputs only in `tmp_path` | Pass | Repo tree unchanged by tests |

## Changes
- pyproject.toml — packaging, dependencies, console script, pytest config
- src/csv2parquet/__init__.py — version string
- src/csv2parquet/cli.py — argparse CLI and conversion logic
- src/csv2parquet/__main__.py — enables `python -m csv2parquet`
- tests/test_cli.py — 10 tests

## Risks and next steps
- Tests do not cover the none, brotli and lz4 codecs (checked manually, they work).
- `requires-python >=3.11` and `pyarrow>=26` are strict; relax if older environments are needed.
- Whole file is read into memory; files larger than RAM are out of scope.
- Nothing is committed yet.
