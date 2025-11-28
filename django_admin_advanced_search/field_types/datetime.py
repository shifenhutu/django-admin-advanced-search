"""DateTime field parser for advanced search."""

from datetime import datetime, date
from django.db import models
from .base import BaseFieldParser


class DateTimeFieldParser(BaseFieldParser):
    """Parser for datetime fields."""
    
    @classmethod
    def supports(cls, field):
        """Check if this parser supports the given field."""
        return isinstance(field, (models.DateTimeField, models.DateField))
    
    def parse(self, value_str, field_name, modifier=''):
        """Parse a datetime value."""
        value = value_str.strip()
        
        # 根据修饰符确定查找类型
        if modifier == '>=':
            lookup, value = 'gte', value
        elif modifier == '>':
            lookup, value = 'gt', value
        elif modifier == '<=':
            lookup, value = 'lte', value
        elif modifier == '<':
            lookup, value = 'lt', value
        elif modifier in ('=', '==', ''):
            lookup, value = 'exact', value
        else:
            # 对于日期字段，忽略通配符等不适用的修饰符
            lookup, value = 'exact', value
        
        return {f"{field_name}__{lookup}": value}