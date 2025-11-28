#!/usr/bin/env python
"""Test runner for django-admin-advanced-search."""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    # Run only the new tests
    failures = test_runner.run_tests(["tests.test_mixin_new", "tests.test_parser", "tests.test_field_types"])
    sys.exit(bool(failures))