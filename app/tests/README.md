# YAMZ Testing Documentation

This directory contains tests for the YAMZ application. The tests are designed to work with SQLite, making them easy to run in any environment without needing PostgreSQL.

## Testing Strategy

Our testing approach focuses on validating core functionality with basic tests that:

1. Confirm essential pages load correctly
2. Verify term creation and retrieval works
3. Test browsing capabilities
4. Validate basic search functionality

## Test Files

- `test_basic.py` - Core functionality tests that work with SQLite
- `conftest.py` - Test fixtures and database setup/teardown logic

## Running the Tests

From the project root directory:

```bash
# Run all tests with default output
./app/tests/run_tests.sh -p

# Run tests with verbose output
./app/tests/run_tests.sh -p -v

# Run tests with coverage reporting
./app/tests/run_tests.sh -p -c
```

## Understanding the Tests

### Database Compatibility

The tests use SQLite instead of PostgreSQL for simplicity. The main compatibility challenge is that PostgreSQL uses TSVECTOR for full-text search, which SQLite doesn't support. The `conftest.py` file contains patches that allow the Term model to work with SQLite during testing.

### Session Handling

The tests carefully manage SQLAlchemy sessions to prevent "detached instance" errors. Each test closes and reopens sessions as needed to ensure test isolation.

### Enum Handling

The app uses PostgreSQL enums, which behave differently in SQLite. Our tests work around this by comparing string representations rather than direct equality.

## Adding New Tests

When adding new tests:

1. Add them to `test_basic.py` to maintain compatibility with SQLite
2. Avoid direct dependencies on PostgreSQL-specific features like TSVECTOR
3. Use string comparisons for enums (`str(term.status)` instead of direct equality)
4. Be mindful of session handling to prevent detached instance errors
