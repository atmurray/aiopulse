# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-08-01

### Changed
- Minimum Python version is now 3.10
- Modernized asyncio patterns (removed loop parameter deprecation)
- Updated type hints to Python 3.10+ syntax
- Improved error handling with bounds checking
- Extracted CallbackMixin for shared callback logic
- Updated CI/CD with testing and type checking
- Organized protocol constants with enums

### Deprecated
- `loop` parameter in Hub.__init__() and Hub.discover() - will be removed in v0.6.0

### Fixed
- Duplicate InvalidResponseException catch in hub.py
- Unsafe lock management in send_command()
- Missing bounds checking in response parsers

### Added
- CallbackMixin for shared callback logic
- HubEntity base class for hub entities
- Type annotations throughout codebase
- mypy type checking support
- GitHub Actions release workflow

## [0.4.7] - Previous release
