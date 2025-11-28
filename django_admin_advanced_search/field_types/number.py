"""Number field parser for advanced search."""

from django.db import models
from .base import BaseFieldParser


class NumberFieldParser(BaseFieldParser):
    """Parser for number fields."""
    
    @classmethod
    def supports(cls, field):
        """Check if this parser supports the given field."""
        return isinstance(field, (models.IntegerField, models.FloatField, models.DecimalField, models.PositiveIntegerField, models.PositiveSmallIntegerField, models.BigIntegerField, models.SmallIntegerField))
    
    def parse(self, value_str, field_name, modifier=''):
        """Parse a number value."""
        value = value_str.strip()
        
        # 尝试转换为数字
        try:
            if '.' in value or 'e' in value.lower():
                num_val = float(value)
            else:
                num_val = int(value)
        except (ValueError, TypeError):
            # 如果无法转换为数字，抛出异常让调用者处理
            raise ValueError(f"Cannot convert '{value}' to a number")
        
        # 根据修饰符确定查找类型
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
            lookup, value = 'exact', num_val
        
        return {f"{field_name}__{lookup}": value}