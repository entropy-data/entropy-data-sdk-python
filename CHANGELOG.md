# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- `assets.assign_tag` and `assets.unassign_tag` keep the slashes of a hierarchical tag id such as `governance/PII`
  in the request path; the encoded form was rejected by the server

## [0.1.0] - 2026-10-13

### Added

- Typed client for every area of the Entropy Data API, built on httpx and pydantic
- Connector framework: connector registration, assets synchronizer, event listener with one handler method per event
  type, in-memory and remote state repositories
- Model generation from the OpenAPI spec with stable names for nested objects
- Enums accept values the SDK does not know yet instead of failing validation
- Resource ids are validated and percent-encoded; connection failures are retried
- List calls return a `Page` with `has_next`; the generic layer exposes the `location-html` header of write calls
- Connectors register on `start()` with retries, skip assets that only differ in server-side fields, and can decide
  through `EventHandler.on_error` whether to skip or retry a failing event
