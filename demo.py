#!/usr/bin/env python3
"""
Demo script to showcase the advanced search functionality for Django Admin.
This script demonstrates the new features for date and number field support.
"""

import re
from datetime import datetime, date
from decimal import Decimal

# Import our mixin (in a real Django project, this would be imported differently)
# For this demo, we'll simulate the functionality

def demo_field_type_detection():
    """Demonstrate field type detection."""
    print("=== Field Type Detection Demo ===")
    print("The mixin can detect field types and apply appropriate parsing rules:")
    print()
    
    # Simulate field types
    field_types = {
        'title': 'str',
        'description': 'str',
        'price': 'number',
        'rating': 'number',
        'publication_date': 'date',
        'created_at': 'datetime',
        'updated_at': 'datetime'
    }
    
    for field, field_type in field_types.items():
        print(f"Field '{field}' detected as type: {field_type}")
    
    print()

def demo_search_syntax():
    """Demonstrate the search syntax for different field types."""
    print("=== Search Syntax Demo ===")
    print("Different field types support different operators:")
    print()
    
    print("1. String fields:")
    print("   title:python              # Case-insensitive contains")
    print("   title:=python             # Case-insensitive exact")
    print("   title:==Python            # Case-sensitive exact")
    print("   title:*python             # Case-insensitive ends with")
    print("   title:!*Python            # Case-sensitive ends with")
    print("   title:python*             # Case-insensitive starts with")
    print("   title:!Python*            # Case-sensitive starts with")
    print()
    
    print("2. Number fields:")
    print("   price:>29.99              # Greater than")
    print("   price:>=19.99             # Greater than or equal")
    print("   price:<99.99              # Less than")
    print("   price:<=59.99             # Less than or equal")
    print("   price:=29.99              # Equal")
    print("   price:==29.99             # Equal (same as =)")
    print()
    
    print("3. Date/DateTime fields:")
    print("   publication_date:2023-06-15        # Exact date")
    print("   publication_date:>2023-01-01       # After date")
    print("   publication_date:>=2023-01-01      # On or after date")
    print("   publication_date:<2023-12-31       # Before date")
    print("   publication_date:<=2023-12-31      # On or before date")
    print("   created_at:<\"2023-12-31 23:59:59\"  # Before datetime (quoted because of space)")
    print()

def demo_regex_parsing():
    """Demonstrate how the regex parsing works."""
    print("=== Regex Parsing Demo ===")
    print("The regex pattern used to parse search terms:")
    print()
    
    pattern = r'(\S+?):((?:==|>=|<=|[=<!>])?)((\"([^\"]*)\")|(\S+))'
    print(f"Pattern: {pattern}")
    print()
    
    examples = [
        'title:python',
        'price:>29.99',
        'publication_date:2023-06-15',
        'created_at:<"2023-12-31 23:59:59"'
    ]
    
    print("Example matches:")
    for example in examples:
        match = re.search(pattern, example)
        if match:
            groups = match.groups()
            print(f"  {example}")
            print(f"    Field: {groups[0]}")
            print(f"    Operator: '{groups[1]}'")
            print(f"    Quoted value: {groups[4]!r}")
            print(f"    Unquoted value: {groups[5]!r}")
            print(f"    Used value: {groups[4] or groups[5]!r}")
        else:
            print(f"  {example} - NO MATCH")
        print()

def demo_error_handling():
    """Demonstrate error handling."""
    print("=== Error Handling Demo ===")
    print("The mixin gracefully handles various error conditions:")
    print()
    
    print("1. Invalid field names are treated as plain text:")
    print("   invalid_field:value  →  Falls back to plain text search")
    print()
    
    print("2. Invalid values for typed fields are treated as plain text:")
    print("   price:not_a_number   →  Falls back to plain text search")
    print()
    
    print("3. Unsupported operators for field types are ignored:")
    print("   price:*29.99         →  Falls back to plain text search")
    print()

if __name__ == "__main__":
    print("Django Admin Advanced Search Mixin - Demo")
    print("=" * 50)
    print()
    
    demo_field_type_detection()
    demo_search_syntax()
    demo_regex_parsing()
    demo_error_handling()
    
    print("=== Summary ===")
    print("Key improvements in this version:")
    print("1. Automatic field type detection (string, number, date, datetime)")
    print("2. Type-specific parsing rules")
    print("3. Support for comparison operators on number and date fields")
    print("4. Proper handling of datetime values with spaces (use quotes)")
    print("5. Graceful fallback to plain text search for invalid syntax")
    print()
    print("Remember: DateTime values with spaces must be quoted!")
    print("Example: created_at:<\"2023-12-31 23:59:59\"")