#!/usr/bin/env python3
"""Test script to verify regex parsing for date and number fields."""

import re

def test_regex():
    # Updated pattern with proper ordering for >= and <=
    # Fixed pattern to correctly capture >= and <= operators
    pattern = r'(\S+?):((?:==|>=|<=|[=!<>])?)((\"([^\"]*)\")|(\S+))'
    
    test_cases = [
        'price:>100',
        'price:>=100', 
        'date:<2023-01-01',
        'date:<=2023-12-31',
        'title:python',  # Basic case
        'name:=john',    # Exact match
        'title:==Python' # Case-sensitive exact
    ]
    
    print("Testing regex pattern:", pattern)
    print()
    
    for text in test_cases:
        match = re.search(pattern, text)
        if match:
            field = match.group(1)
            modifier = match.group(2) or ''
            # Get the value (either quoted or unquoted)
            quoted_val = match.group(5)  # Group 5 is quoted value
            unquoted_val = match.group(6)  # Group 6 is unquoted value
            value = quoted_val if quoted_val is not None else unquoted_val
            
            print(f"Text: {text}")
            print(f"  Field: {field}")
            print(f"  Modifier: '{modifier}'")
            print(f"  Value: {value}")
            print()
        else:
            print(f"No match for: {text}")
            print()

def test_current_implementation():
    """Test the current implementation in the mixin."""
    print("=== Testing Current Implementation ===")
    
    # Simulate the current pattern from the mixin
    pattern = r'(\S+?):((?:==|>=|<=|[=!<>])?)((\"([^\"]*)\")|(\S+))'
    
    # Test cases that should work with our date/number field support
    test_cases = [
        'price:>100',
        'price:>=100',
        'quantity:<50',
        'quantity:<=25',
        'date:>2023-01-01',
        'date:>=2023-01-01',
        'created_at:<2023-12-31',
        'created_at:<=2023-12-31'
    ]
    
    for text in test_cases:
        match = re.search(pattern, text)
        if match:
            field = match.group(1)
            modifier = match.group(2) or ''
            quoted_val = match.group(5)
            unquoted_val = match.group(6)
            value = quoted_val if quoted_val is not None else unquoted_val
            
            print(f"Text: {text}")
            print(f"  Field: {field}")
            print(f"  Modifier: '{modifier}'")
            print(f"  Value: {value}")
            
            # Test the mapping logic
            lookup_map = {
                '==': 'exact',
                '=': 'iexact',
                '!': 'contains',  # This is more complex in the actual implementation
                '>': 'gt',
                '>=': 'gte',
                '<': 'lt',
                '<=': 'lte',
                '': 'icontains'  # default
            }
            
            lookup = lookup_map.get(modifier, 'icontains')
            print(f"  Mapped lookup: {lookup}")
            print()
        else:
            print(f"No match for: {text}")
            print()

if __name__ == "__main__":
    test_regex()
    test_current_implementation()