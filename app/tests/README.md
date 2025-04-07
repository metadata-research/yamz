# Yamz Testing Guide

This directory contains tests for the Yamz application. There are several different testing approaches implemented here.

## Testing Approaches

### 1. Basic Tests (`test_basic.py`)

The simplest tests focus on direct assertions without complex database interactions. They use:

- Simple model instantiation for testing defaults and attributes
- Mocking to isolate components and avoid actual database access
- Patching Flask's render_template for testing routes

These tests are fastest and most reliable, as they don't depend on complex setup or database state.

### 2. Unittest Tests (`tests.py`)

These tests use Python's unittest framework with more complex database interactions, using:

- In-memory SQLite database for tests
- Custom SQLite-compatible model definitions 
- Temporary database that gets created and destroyed for each test suite

### 3. Pytest Tests (`test_pytest_*.py`)

These tests use Pytest for a more modern testing approach with:

- Fixtures for test setup and teardown
- Parametrized tests for testing many cases at once
- Better error reporting and debugging

## Running Tests

The `run_tests.sh` script provides a convenient way to run tests with various options:

```bash
# Run all tests
./app/tests/run_tests.sh

# Run only unit tests
./app/tests/run_tests.sh -u

# Run only pytest tests
./app/tests/run_tests.sh -p

# Run tests with verbose output
./app/tests/run_tests.sh -v

# Run tests with coverage report
./app/tests/run_tests.sh -c
```

## Testing Strategy

### When to use each approach:

- **Basic tests**: For simple validation of models, functions, and routes
- **Unittest tests**: For testing database interactions and relationships
- **Pytest tests**: For more complex test cases with parameterization

### Testing Database Models

When testing models with PostgreSQL-specific features:

1. Create SQLite-compatible model classes for testing
2. Use SQLite-only features in tests
3. Mock complex database interactions where possible

### Common Challenges

#### PostgreSQL-specific Features

The application uses PostgreSQL-specific features like TSVECTOR that don't work in SQLite. For testing:

- Use string replacements via monkey patching
- Skip text search tests in SQLite environments
- Use more basic queries for search-related tests

#### Relationships and Foreign Keys

Test relationships carefully:

- Ensure models have proper foreign key constraints defined
- Use explicit primaryjoin and secondaryjoin when needed
- For complex relationships, consider using mocks instead of real database objects

## Writing New Tests

When adding new tests:

1. Start with basic model/function tests
2. Add route tests with mocked dependencies
3. Add integration tests for critical features
4. Consider the trade-offs between test complexity and coverage

Remember: Good tests are readable, fast, and reliable. Prefer simpler tests that run quickly and consistently over complex tests that may be brittle.
