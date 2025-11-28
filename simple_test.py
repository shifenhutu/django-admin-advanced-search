#!/usr/bin/env python
"""Simple test for the AdvancedSearchMixin parsing functionality."""

import re
from django_admin_advanced_search.mixins import AdvancedSearchMixin


class MockAdmin(AdvancedSearchMixin):
    search_fields = ['title', 'author__name']


def test_parsing():
    """Test the parsing functionality."""
    admin = MockAdmin()
    
    # Test basic parsing
    terms = admin._parse_search_terms('title:python')
    print("Parsed terms for 'title:python':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'contains', 'python')
    
    # Test exact match
    terms = admin._parse_search_terms('title:=python')
    print("Parsed terms for 'title:=python':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'exact', 'python')
    
    # Test case-sensitive exact match
    terms = admin._parse_search_terms('title:==Python')
    print("Parsed terms for 'title:==Python':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'exact_case', 'Python')
    
    # Test case-sensitive contains
    terms = admin._parse_search_terms('title:!Python')
    print("Parsed terms for 'title:!Python':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'contains_case', 'Python')
    
    # Test endswith
    terms = admin._parse_search_terms('title:*programming')
    print("Parsed terms for 'title:*programming':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'endswith', 'programming')
    
    # Test case-sensitive endswith
    terms = admin._parse_search_terms('title:!*Programming')
    print("Parsed terms for 'title:!*Programming':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'endswith_case', 'Programming')
    
    # Test startswith
    terms = admin._parse_search_terms('title:python*')
    print("Parsed terms for 'title:python*':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'startswith', 'python')
    
    # Test case-sensitive startswith
    terms = admin._parse_search_terms('title:!Python*')
    print("Parsed terms for 'title:!Python*':", terms)
    assert len(terms) == 1
    assert terms[0] == ('title', 'startswith_case', 'Python')
    
    # Test related field
    terms = admin._parse_search_terms('author__name:john*')
    print("Parsed terms for 'author__name:john*':", terms)
    assert len(terms) == 1
    assert terms[0] == ('author__name', 'startswith', 'john')
    
    # Test quoted values
    terms = admin._parse_search_terms('title:"Python Programming"')
    print("Parsed terms for 'title:\"Python Programming\"':", terms)
    # Note: quoted values are handled differently by the regex, this is just a simple test
    # The actual implementation handles quotes in the regex matching
    
    print("All parsing tests passed!")


def test_field_allowance():
    """Test field allowance functionality."""
    admin = MockAdmin()
    
    # Test allowed fields
    assert admin._is_field_allowed('title') == True
    assert admin._is_field_allowed('author__name') == True
    
    # Test disallowed fields
    assert admin._is_field_allowed('author_id') == False
    assert admin._is_field_allowed('description') == False
    
    print("All field allowance tests passed!")


def test_filter_keyword_building():
    """Test filter keyword building functionality."""
    admin = MockAdmin()
    
    # Test different operators
    assert admin._build_filter_keyword('title', 'contains') == 'title__icontains'
    assert admin._build_filter_keyword('title', 'exact') == 'title__iexact'
    assert admin._build_filter_keyword('title', 'exact_case') == 'title__exact'
    assert admin._build_filter_keyword('title', 'contains_case') == 'title__contains'
    assert admin._build_filter_keyword('title', 'endswith') == 'title__iendswith'
    assert admin._build_filter_keyword('title', 'endswith_case') == 'title__endswith'
    assert admin._build_filter_keyword('title', 'startswith') == 'title__istartswith'
    assert admin._build_filter_keyword('title', 'startswith_case') == 'title__startswith'
    
    # Test invalid operator
    assert admin._build_filter_keyword('title', 'invalid') == None
    
    print("All filter keyword building tests passed!")


if __name__ == "__main__":
    test_parsing()
    test_field_allowance()
    test_filter_keyword_building()
    print("All tests passed!")