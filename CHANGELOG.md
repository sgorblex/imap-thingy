# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-01-XX

### Changed - Major Refactoring

This release includes a comprehensive refactoring of the codebase to improve maintainability, extensibility, and code organization.

#### Criteria System Refactoring

- **Breaking Change**: Criteria are now class-based instead of factory functions
  - Old: `from_is("email@example.com")`
  - New: `FromIs("email@example.com")`
  - All criteria classes follow PascalCase naming convention
  - Criteria are now organized into domain-specific modules:
    - `filters/criteria/address.py` - Address-based criteria (From, To, CC, BCC)
    - `filters/criteria/subject.py` - Subject-based criteria
    - `filters/criteria/date.py` - Date-based criteria
    - `filters/criteria/duplicate.py` - Duplicate detection
    - `filters/criteria/base.py` - Base criterion classes

#### Actions System Refactoring

- **Breaking Change**: Actions are now class-based instead of factory functions
  - Old: `move_to("folder")`, `mark_as_read()`, `trash()`
  - New: `MoveTo("folder")`, `MarkAsRead()`, `Trash()`
  - Actions are organized in `filters/actions/` module:
    - `filters/actions/base.py` - Base Action class
    - `filters/actions/imap.py` - IMAP-specific actions

#### Module Organization

- Split large `criterion_filter.py` (401 lines) into focused modules:
  - `filters/criterion.py` - CriterionFilter implementation
  - `filters/criteria/` - All criteria classes
  - `filters/actions/` - All action classes
- Improved separation of concerns
- Better import structure and organization

#### API Changes

- All criteria classes are now available from `imap_thingy.filters`:
  - `FromIs`, `FromContains`, `FromMatches`, `FromMatchesName`
  - `ToIs`, `ToContains`, `ToMatches`
  - `CcIs`, `CcContains`, `CcMatches`
  - `BccIs`, `BccContains`, `BccMatches`
  - `SubjectIs`, `SubjectContains`, `SubjectMatches`
  - `OlderThan`, `SelectAll`, `DuplicateCriterion`
- All action classes are available from `imap_thingy.filters`:
  - `MoveTo`, `Trash`, `MarkAsRead`, `MarkAsUnread`
- `CriterionFilter` and `DuplicateFilter` remain unchanged in functionality
- `apply_filters()` function moved to `filters/utils.py` but still available from `filters` module

### Added

- `SelectAll` criterion class for matching all messages
- Better type hints throughout the codebase
- Improved code organization and maintainability
- Test structure foundation

### Migration Guide

To migrate from 0.1.0 to 0.2.0:

1. **Update criterion imports and usage:**
   ```python
   # Old
   from imap_thingy.filters.criterion_filter import from_is, subject_matches
   criterion = from_is("email@example.com") & subject_matches(r"pattern")

   # New
   from imap_thingy.filters import FromIs, SubjectMatches
   criterion = FromIs("email@example.com") & SubjectMatches(r"pattern")
   ```

2. **Update action imports and usage:**
   ```python
   # Old
   from imap_thingy.filters.criterion_filter import move_to, mark_as_read
   action = mark_as_read() & move_to("folder")

   # New
   from imap_thingy.filters import MarkAsRead, MoveTo
   action = MarkAsRead() & MoveTo("folder")
   ```

3. **Update CriterionFilter import:**
   ```python
   # Old
   from imap_thingy.filters.criterion_filter import CriterionFilter

   # New
   from imap_thingy.filters import CriterionFilter
   ```

All functionality remains the same - only the API naming has changed from functions to classes.

## [0.1.0] - Previous Release

Initial release with function-based criteria and actions API.

