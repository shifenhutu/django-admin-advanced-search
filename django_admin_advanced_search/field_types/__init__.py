"""Field type parsers for advanced search."""

from .string import StringFieldParser
from .number import NumberFieldParser
from .datetime import DateTimeFieldParser

# 注册所有字段解析器
PARSERS = [StringFieldParser, NumberFieldParser, DateTimeFieldParser]


def get_field_parser(field):
    """Get appropriate parser for a field."""
    for Parser in PARSERS:
        if Parser.supports(field):
            return Parser()
    # 默认回退到字符串解析器
    return StringFieldParser()