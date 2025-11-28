# Testing Guide

## Running Tests

This package uses Django's built-in testing framework. To run the tests:

```bash
python -m django test tests --settings=tests.settings
```

Or if you have Django installed and configured:

```bash
python manage.py test tests
```

## Test Structure

The tests are located in the `tests/` directory:

- `tests/settings.py` - Django settings for running tests
- `tests/test_mixin.py` - Test cases for the `AdvancedSearchMixin` class

## Test Cases

The test suite validates the following functionality:

1. **Parsing functionality** - Ensures that search terms are correctly parsed according to the syntax rules
2. **Field allowance** - Verifies that only fields in `search_fields` are allowed for security
3. **Filter keyword building** - Checks that Django ORM filter keywords are correctly constructed
4. **Operator mapping** - Validates that operators are correctly mapped to Django ORM lookups

## Writing New Tests

To add new test cases:

1. Add new test methods to `tests/test_mixin.py`
2. Follow the existing pattern of creating a mock admin class with `search_fields`
3. Use Django's `TestCase` assertions to validate behavior

Example test structure:

```python
def test_new_feature(self):
    """Description of what is being tested."""
    admin = BookAdmin()  # Mock admin class
    # Perform the test
    result = admin.some_method('test_input')
    # Assert expected behavior
    self.assertEqual(result, 'expected_output')
```

## Continuous Integration

The package includes GitHub Actions configuration for continuous integration testing across multiple Python and Django versions. Tests are automatically run on pushes to the main branch and pull requests.

## Test Coverage

The current test suite covers:

- All search syntax operators (`:`, `:=`, `:==`, `:!`, `:*`, `:!*`, `:*`, `:!*)
- Field allowance security checks
- Related field handling (e.g., `author__name`)
- Filter keyword construction for Django ORM
- Error handling and fallback behavior

## Manual Testing

For manual testing in a Django project:

1. Install the package: `pip install django-admin-advanced-search`
2. Add to `INSTALLED_APPS`
3. Apply the mixin to a model admin with `search_fields` configured
4. Use the Django Admin interface to test various search queries