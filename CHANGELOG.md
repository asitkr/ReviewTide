# Changelog

All notable changes to ReviewTide are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed

- Metric wording is being reviewed for the next patch.

## [1.0.0] - 2026-05-05

### Added

- Stable contract: exit codes 0, 1 and 2, and the written input contract in
  `docs/FORMAT.md`.
- Percentile reporting with the sample size next to every number.

## [0.9.0] - 2026-01-20

### Added

- Ownership concentration and the bus factor signal per path prefix.
- A worked run over the bundled PR export.

## [0.8.0] - 2025-04-08

### Added

- Review depth: comment counts and review rounds per pull request.
- `--since` window for git log input.

## [0.7.0] - 2024-07-02

### Added

- JSON report with fixed keys, including per-percentile sample sizes.
- `flow` and `ownership` subcommands.

## [0.6.0] - 2023-11-21

### Added

- Queue time before first review and first response latency as separate
  metrics, because they answer different questions.
