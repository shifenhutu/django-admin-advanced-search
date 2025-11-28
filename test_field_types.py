#!/usr/bin/env python3
"""Test script to verify field type-based parsing for date and number fields."""

import re
from datetime import datetime, date
from django.db import models

# Mock field types for testing
class IntegerField:
    pass

class FloatField:
    pass

class DateField:
    pass

class DateTimeField:
    pass

class CharField:
    pass

def get_field_type_mock(field_name):
    """Mock function to simulate getting field types."""
    field_types = {
        'price': IntegerField,
        'rating': FloatField,
        'date': DateField,
        'created_at': DateTimeField,
        'title': CharField,
        'name': CharField
    }
    return field_types.get(field_name)

def parse_advanced_search(text, allowed_fields):
    """Parse search terms using advanced syntax with field type awareness."""
    if not allowed_fields:
        return {'has_advanced': False, 'filters': {}, 'plain_text': text}

    # 正则表达式匹配 field:modifier"value" 或 field:modifier value
    # Groups: 1=field, 2=modifier(==|=|!|>=|<=|>|<), 4=quoted_value, 5=unquoted_value
    pattern = r'(\S+?):((?:==|>=|<=|[=!<>])?)((\"([^\"]*)\")|(\S+))'
    filters = {}
    plain_parts = []
    last_end = 0

    for match in re.finditer(pattern, text):
        field = match.group(1)
        modifier = match.group(2) or ''
        quoted_val = match.group(5)  # Group 5 is quoted value
        unquoted_val = match.group(6)  # Group 6 is unquoted value
        raw_value = quoted_val if quoted_val is not None else unquoted_val
        start, end = match.span()

        # 只处理允许的字段
        if field not in allowed_fields:
            plain_parts.append(match.group(0))
            continue

        # 根据修饰符和字段类型确定查找类型
        if modifier == '==':
            lookup, value = 'exact', raw_value
        elif modifier == '=':
            lookup, value = 'iexact', raw_value
        elif modifier == '!':
            value = raw_value
            if value.startswith('*') and value.endswith('*'):
                lookup, value = 'contains', value[1:-1]
            elif value.startswith('*'):
                lookup, value = 'endswith', value[1:]
            elif value.endswith('*'):
                lookup, value = 'startswith', value[:-1]
            else:
                lookup = 'contains'
        elif modifier == '>=':
            lookup, value = 'gte', raw_value
        elif modifier == '>':
            lookup, value = 'gt', raw_value
        elif modifier == '<=':
            lookup, value = 'lte', raw_value
        elif modifier == '<':
            lookup, value = 'lt', raw_value
        else:
            value = raw_value
            if value.startswith('*') and value.endswith('*'):
                lookup, value = 'icontains', value[1:-1]
            elif value.startswith('*'):
                lookup, value = 'iendswith', value[1:]
            elif value.endswith('*'):
                lookup, value = 'istartswith', value[:-1]
            else:
                lookup = 'icontains'

        filters[field] = (lookup, value)
        # 添加匹配之前的普通文本
        plain_parts.append(text[last_end:start].strip())
        last_end = end

    # 添加最后剩余的普通文本
    plain_parts.append(text[last_end:].strip())
    plain_text = ' '.join(p for p in plain_parts if p).strip()

    return {
        'has_advanced': bool(filters),
        'filters': filters,
        'plain_text': plain_text,
    }

def convert_value_for_field(field_name, value):
    """Convert value to appropriate type based on field type."""
    field_type = get_field_type_mock(field_name)
    
    if field_type is None:
        return None
        
    try:
        # Convert based on field type
        if field_type == IntegerField:
            return int(value)
        elif field_type == FloatField:
            return float(value)
        elif field_type == DateField:
            # Try to parse date
            for fmt in ('%Y-%m-%d',):
                try:
                    return datetime.strptime(value, fmt).date()
                except ValueError:
                    continue
            return value
        elif field_type == DateTimeField:
            # Try to parse datetime
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'):
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            return value
        else:
            return None
    except:
        # If conversion fails, return None to use original value
        return None

def test_parsing():
    """Test the parsing functionality."""
    allowed_fields = ['price', 'rating', 'date', 'created_at', 'title', 'name']
    
    test_cases = [
        'price:>100',
        'price:>=100', 
        'rating:<4.5',
        'rating:<=5.0',
        'date:>2023-01-01',
        'date:>=2023-01-01',
        'created_at:<"2023-12-31 23:59:59"',
        'created_at:<="2023-12-31 23:59:59"',
        'title:python*',
        'name:=john'
    ]
    
    print("Testing advanced search parsing with field type awareness:")
    print("=" * 60)
    
    for text in test_cases:
        result = parse_advanced_search(text, allowed_fields)
        print(f"Input: {text}")
        print(f"  Has advanced: {result['has_advanced']}")
        if result['has_advanced']:
            for field, (lookup, value) in result['filters'].items():
                print(f"  Field: {field}, Lookup: {lookup}, Value: {value}")
                # Test value conversion
                converted_value = convert_value_for_field(field, value)
                if converted_value is not None and converted_value != value:
                    print(f"    Converted value: {converted_value} (type: {type(converted_value).__name__})")
        print()

if __name__ == "__main__":
    test_parsing()