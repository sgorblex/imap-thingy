# Changelog

## [0.8.0](https://github.com/sgorblex/imap-thingy/compare/v0.7.0...v0.8.0) (2026-10-29)


### Features

* give built-in actions human-readable names ([#49](https://github.com/sgorblex/imap-thingy/issues/49)) ([9c4322c](https://github.com/sgorblex/imap-thingy/commit/9c4322c4149d4cc4e2df874137be831bd8cff433))

## [0.7.0](https://github.com/sgorblex/imap-thingy/compare/v0.6.0...v0.7.0) (2026-10-23)


### Features

* add match timeout for user regex patterns ([#47](https://github.com/sgorblex/imap-thingy/issues/47)) ([60d82fb](https://github.com/sgorblex/imap-thingy/commit/60d82fb2a3e3c7592530639d0bccec640ad09d56))
* add OlderThanDays criterion for age relative to run date ([#44](https://github.com/sgorblex/imap-thingy/issues/44)) ([a5ebac3](https://github.com/sgorblex/imap-thingy/commit/a5ebac351a0ef06487f202e65d8928461406944b))
* add SSL context and timeout options and list_folders to accounts ([#45](https://github.com/sgorblex/imap-thingy/issues/45)) ([c7ad5cf](https://github.com/sgorblex/imap-thingy/commit/c7ad5cf4f093e5e89eec92f00298156fbf5250cd))
* allow running IDLE monitor in non-main threads with a stop event ([#46](https://github.com/sgorblex/imap-thingy/issues/46)) ([32f3d26](https://github.com/sgorblex/imap-thingy/commit/32f3d26d273b65eccb75e042de7b91f392ec744f))
* return JSON-compatible run reports from folder and rule runs ([#43](https://github.com/sgorblex/imap-thingy/issues/43)) ([987462f](https://github.com/sgorblex/imap-thingy/commit/987462f20f162154929f0f5c8dbf8f6e833297be))

## [0.6.0](https://github.com/sgorblex/imap-thingy/compare/v0.5.0...v0.6.0) (2026-10-15)


### Features

* add runner for running filter rules once, in parallel, or via IDLE ([#41](https://github.com/sgorblex/imap-thingy/issues/41)) ([dfc8692](https://github.com/sgorblex/imap-thingy/commit/dfc86927d4bdb535a9ee100ba4f08c6ed9568a50))

## [0.5.0](https://github.com/sgorblex/imap-thingy/compare/v0.4.0...v0.5.0) (2026-10-14)


### Features

* add JSON-compatible data specs for filters, criteria and actions ([#39](https://github.com/sgorblex/imap-thingy/issues/39)) ([b83d047](https://github.com/sgorblex/imap-thingy/commit/b83d0475984f022c95feea1e66bf3b6ee844a04b))

## [0.4.0](https://github.com/sgorblex/imap-thingy/compare/v0.3.0...v0.4.0) (2026-10-13)


### Features

* add exponential backoff to IMAP reconnect attempts ([#27](https://github.com/sgorblex/imap-thingy/issues/27)) ([ac4d951](https://github.com/sgorblex/imap-thingy/commit/ac4d95166b1146870aaac96f21228b5bfbb9ac26))
* add py.typed marker for PEP 561 typing support ([#36](https://github.com/sgorblex/imap-thingy/issues/36)) ([bcf2ef9](https://github.com/sgorblex/imap-thingy/commit/bcf2ef9b1918e9a2c368fe60d44cf91ae36e78d5))


### Bug Fixes

* stop installing a top-level tests package ([#34](https://github.com/sgorblex/imap-thingy/issues/34)) ([e9295db](https://github.com/sgorblex/imap-thingy/commit/e9295db77c670fbd21c5f4549f282378cda5e65c))
