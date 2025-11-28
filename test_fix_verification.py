#!/usr/bin/env python
"""Test script to verify the fix for combined advanced and plain text search."""

from django_admin_advanced_search.parser import parse_advanced_search

def test_fix():
    """Test that the fix correctly handles combined advanced and plain text search."""
    
    # Test case 1: Advanced search with trailing plain text
    result = parse_advanced_search('name:=john lisa', ['name'])
    print("Test 1 - 'name:=john lisa':")
    print("  Result:", result)
    print("  Has advanced:", result['has_advanced'])
    print("  Filters:", result['filters'])
    print("  Plain text:", repr(result['plain_text']))
    print()
    
    # Test case 2: Plain text with advanced search
    result = parse_advanced_search('lisa name:=john', ['name'])
    print("Test 2 - 'lisa name:=john':")
    print("  Result:", result)
    print("  Has advanced:", result['has_advanced'])
    print("  Filters:", result['filters'])
    print("  Plain text:", repr(result['plain_text']))
    print()
    
    # Test case 3: Multiple advanced searches with plain text
    result = parse_advanced_search('name:=john description:developer lisa', ['name', 'description'])
    print("Test 3 - 'name:=john description:developer lisa':")
    print("  Result:", result)
    print("  Has advanced:", result['has_advanced'])
    print("  Filters:", result['filters'])
    print("  Plain text:", repr(result['plain_text']))
    print()
    
    # Test case 4: Only plain text
    result = parse_advanced_search('john lisa', ['name'])
    print("Test 4 - 'john lisa':")
    print("  Result:", result)
    print("  Has advanced:", result['has_advanced'])
    print("  Filters:", result['filters'])
    print("  Plain text:", repr(result['plain_text']))
    print()

if __name__ == "__main__":
    test_fix()