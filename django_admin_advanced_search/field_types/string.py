"""String field parser for advanced search."""

from django.db import models
from .base import BaseFieldParser


class StringFieldParser(BaseFieldParser):
    """Parser for string fields."""
    
    @classmethod
    def supports(cls, field):
        """Check if this parser supports the given field."""
        return isinstance(field, (models.CharField, models.TextField, models.EmailField, models.URLField))
    
    def parse(self, value_str, field_name, modifier=''):
        """Parse a string value."""
        value = value_str.strip()
        
        # 根据修饰符和通配符确定查找类型
        if modifier == '==':
            lookup, value = 'exact', value
        elif modifier == '=':
            lookup, value = 'iexact', value
        elif modifier == '!':
            if value.startswith('*') and value.endswith('*'):
                lookup, value = 'contains', value[1:-1]
            elif value.startswith('*'):
                lookup, value = 'endswith', value[1:]
            elif value.endswith('*'):
                lookup, value = 'startswith', value[:-1]
            else:
                lookup = 'contains'
        else:
            # 默认情况或无修饰符
            if value.startswith('*') and value.endswith('*'):
                lookup, value = 'icontains', value[1:-1]
            elif value.startswith('*'):
                lookup, value = 'iendswith', value[1:]
            elif value.endswith('*'):
                lookup, value = 'istartswith', value[:-1]
            else:
                lookup = 'icontains'
        
        return {f"{field_name}__{lookup}": value}