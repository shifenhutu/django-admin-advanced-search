#!/usr/bin/env python3
"""Improved parser implementation with field type awareness."""

import re
from datetime import datetime, date
from decimal import Decimal, InvalidOperation


class MockModel:
    """Mock Django model for testing."""
    pass


class MockField:
    """Mock Django field for testing."""
    def __init__(self, field_type):
        self.field_type = field_type


def get_field_type_mock(field_path):
    """Mock function to simulate getting field types."""
    field_types = {
        'price': 'number',
        'rating': 'number',
        'date': 'date',
        'created_at': 'datetime',
        'title': 'str',
        'name': 'str'
    }
    return field_types.get(field_path, 'str')


def parse_advanced_search(text, allowed_fields, get_field_type_func=None):
    """Parse search terms using advanced syntax with field type awareness."""
    if not allowed_fields:
        return {'has_advanced': False, 'filters': {}, 'plain_text': text}

    # 正则表达式匹配 field:modifier"value" 或 field:modifier value
    # Groups: 1=field, 2=modifier(==|=|!|>=|<=|>|<), 4=quoted_value, 5=unquoted_value
    pattern = r'(\S+?):((?:==|>=|<=|[=!<>])?)((\"([^\"]*)\")|(\S+))'
    filters = {}
    plain_parts = []
    last_end = 0

    # Use mock function if not provided
    if get_field_type_func is None:
        get_field_type_func = get_field_type_mock

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

        # 根据字段类型确定如何处理
        field_type = get_field_type_func(field)
        
        # 根据修饰符和字段类型确定查找类型
        if field_type == 'number':
            # 处理数字字段
            try:
                # 尝试转换为数字
                if '.' in raw_value or 'e' in raw_value.lower():
                    num_val = float(raw_value)
                else:
                    num_val = int(raw_value)
                
                if modifier == '>=':
                    lookup, value = 'gte', num_val
                elif modifier == '>':
                    lookup, value = 'gt', num_val
                elif modifier == '<=':
                    lookup, value = 'lte', num_val
                elif modifier == '<':
                    lookup, value = 'lt', num_val
                elif modifier in ('=', '==', ''):
                    lookup, value = 'exact', num_val
                else:
                    # 对于数字字段，忽略通配符等不适用的修饰符
                    continue
            except (ValueError, TypeError):
                # 如果无法转换为数字，跳过这个条件
                plain_parts.append(match.group(0))
                continue
                
        elif field_type in ('date', 'datetime'):
            # 处理日期/时间字段
            # 对于日期字段，我们直接使用值，让Django处理转换
            if modifier == '>=':
                lookup, value = 'gte', raw_value
            elif modifier == '>':
                lookup, value = 'gt', raw_value
            elif modifier == '<=':
                lookup, value = 'lte', raw_value
            elif modifier == '<':
                lookup, value = 'lt', raw_value
            elif modifier in ('=', '==', ''):
                lookup, value = 'exact', raw_value
            else:
                # 对于日期字段，忽略通配符等不适用的修饰符
                continue
        else:
            # 处理字符串字段
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
        'created_at:<2023-12-31 23:59:59',
        'created_at:<=2023-12-31 23:59:59',
        'title:python*',
        'name:=john',
        'invalid_field:>100',  # Should be treated as plain text
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
                field_type = get_field_type_mock(field)
                if field_type == 'number' and isinstance(value, (int, float)):
                    print(f"    Converted number: {value} (type: {type(value).__name__})")
        else:
            print(f"  Plain text: '{result['plain_text']}'")
        print()


if __name__ == "__main__":
    test_parsing()