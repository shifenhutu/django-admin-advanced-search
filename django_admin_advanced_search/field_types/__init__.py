"""Field type parsers for advanced search.

This module provides parsers for different field types:
- StringFieldParser: Handles string fields with wildcard and exact match support
- NumberFieldParser: Handles number fields with comparison operators and range support (e.g., 100..200)
- DateTimeFieldParser: Handles date/datetime fields with comparison operators and range support (e.g., 2023-01-01..2023-12-31)
"""

from .string import StringFieldParser
from .number import NumberFieldParser
from .datetime import DateTimeFieldParser

# 注册所有字段解析器
PARSERS = [StringFieldParser, NumberFieldParser, DateTimeFieldParser]


def get_field_parser(field):
    """Get appropriate parser for a field.
    
    Args:
        field: A Django model field instance
        
    Returns:
        An instance of the appropriate field parser
    """
    for Parser in PARSERS:
        if Parser.supports(field):
            return Parser()
    # 默认回退到字符串解析器
    return StringFieldParser()