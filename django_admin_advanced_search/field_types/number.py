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
        
        # 处理区间语法 (e.g., 100..200)
        if '..' in value:
            parts = value.split('..')
            if len(parts) == 2:
                start_val = parts[0].strip()
                end_val = parts[1].strip()
                filters = {}
                
                # 处理起始值
                if start_val:
                    try:
                        if '.' in start_val or 'e' in start_val.lower():
                            num_val = float(start_val)
                        else:
                            num_val = int(start_val)
                        filters[f"{field_name}__gte"] = num_val
                    except (ValueError, TypeError):
                        raise ValueError(f"Cannot convert '{start_val}' to a number")
                
                # 处理结束值
                if end_val:
                    try:
                        if '.' in end_val or 'e' in end_val.lower():
                            num_val = float(end_val)
                        else:
                            num_val = int(end_val)
                        filters[f"{field_name}__lte"] = num_val
                    except (ValueError, TypeError):
                        raise ValueError(f"Cannot convert '{end_val}' to a number")
                
                return filters
        
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