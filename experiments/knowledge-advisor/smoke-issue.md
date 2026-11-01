# Fixture: scheduled customer export

## Request

Create a scheduled job that exports selected customers to an external HTTP API. The process reads several fields from the Customer table and saves the API credential in setup. Administrators should be able to rerun a failed export.

## Known context

- The proposed implementation is an AL extension for Business Central.
- No deployed Business Central version, country, API authentication scheme, retry policy, or error-handling requirements have been supplied.
- This is a synthetic issue for a read-only smoke test; it is not an implementation specification.
