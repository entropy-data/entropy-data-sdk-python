# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - unreleased

### Added

- Typed client for every area of the Entropy Data API, built on httpx and pydantic
- Connector framework: connector registration, assets synchronizer, event listener with one handler method per event
  type, in-memory and remote state repositories
- Model generation from the OpenAPI spec with stable names for nested objects
