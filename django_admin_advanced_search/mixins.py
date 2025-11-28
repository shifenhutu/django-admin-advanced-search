"""Advanced search functionality for Django Admin."""

import re
from datetime import datetime
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _


class AdvancedSearchMixin:
    """Mixin to add advanced search functionality to Django Admin.
    
    This mixin extends the default Django Admin search functionality
    with advanced syntax supporting field-specific searches.
    """

    def get_search_results(self, request, queryset, search_term):
        """
        Apply advanced search syntax to queryset.
        
        Supports the following syntax:
        - field:value → case-insensitive contains
        - field:=value → case-insensitive exact
        - field:==value → case-sensitive exact
        - field:!value → case-sensitive contains
        - field:*suffix → case-insensitive endswith
        - field:!*suffix → case-sensitive endswith
        - field:prefix* → case-insensitive startswith
        - field:!prefix* → case-sensitive startswith
        - field:>value → greater than (for numbers and dates)
        - field:>=value → greater than or equal (for numbers and dates)
        - field:<value → less than (for numbers and dates)
        - field:<=value → less than or equal (for numbers and dates)
        - "quoted values" → exact phrase matching
        
        Only fields in search_fields are allowed for security.
        Falls back to default search if parsing fails.
        """
        search_term = search_term.strip()
        if not search_term:
            return super().get_search_results(request, queryset, search_term)

        try:
            parsed = self._parse_advanced_search(search_term)
        except Exception:
            # 解析失败 → 回退到默认行为
            return super().get_search_results(request, queryset, search_term)

        if parsed['has_advanced']:
            qs = queryset
            for field, (lookup, value) in parsed['filters'].items():
                # Try to convert value to appropriate type based on field type
                converted_value = self._convert_value_for_field(field, value)
                if converted_value is not None:
                    value = converted_value
                
                qs = qs.filter(**{f"{field}__{lookup}": value})
            return qs.distinct(), False
        else:
            return super().get_search_results(request, queryset, parsed['plain_text'])
    
    def _convert_value_for_field(self, field_name, value):
        """Convert value to appropriate type based on field type."""
        # Get the model from the admin class
        if not hasattr(self, 'model') or not self.model:
            return None
            
        try:
            # Handle related fields (e.g., author__name)
            if '__' in field_name:
                parts = field_name.split('__')
                model = self.model
                for part in parts[:-1]:
                    field = model._meta.get_field(part)
                    if hasattr(field, 'related_model'):
                        model = field.related_model
                    else:
                        return None
                field_name = parts[-1]
                
            # Get the actual field
            field = model._meta.get_field(field_name)
            
            # Convert based on field type
            if isinstance(field, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField)):
                return int(value)
            elif isinstance(field, (models.FloatField, models.DecimalField)):
                return float(value)
            elif isinstance(field, (models.DateField, models.DateTimeField)):
                # Try to parse date/datetime
                # Handle common date formats
                for fmt in ('%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f'):
                    try:
                        if isinstance(field, models.DateTimeField):
                            return datetime.strptime(value, fmt)
                        else:
                            # For DateField, we only need the date part
                            dt = datetime.strptime(value, fmt)
                            return dt.date()
                    except ValueError:
                        continue
                # If no format matched, return as is
                return value
            else:
                return None
        except:
            # If conversion fails, return None to use original value
            return None
    
    def _parse_advanced_search(self, text):
        """Parse search terms using advanced syntax."""
        allowed_fields = set(getattr(self, 'search_fields', []))
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

            # 根据字段类型确定如何处理
            field_type = self._get_field_type(field)
            
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
    
    def _get_field_type(self, field_path):
        """Determine field type: 'str', 'number', 'date', 'datetime'."""
        try:
            parts = field_path.split("__")
            model = self.model
            for part in parts[:-1]:
                rel = model._meta.get_field(part)
                if hasattr(rel, "related_model"):
                    model = rel.related_model
                else:
                    return "str"
            final_field = model._meta.get_field(parts[-1])

            if isinstance(final_field, models.DateTimeField):
                return "datetime"
            elif isinstance(final_field, models.DateField):
                return "date"
            elif isinstance(
                final_field,
                (models.IntegerField, models.FloatField, models.DecimalField),
            ):
                return "number"
            else:
                return "str"
        except (Exception, AttributeError):
            return "str"
    
    def _is_field_allowed(self, field_name):
        """Check if a field is in search_fields."""
        if not hasattr(self, 'search_fields') or not self.search_fields:
            return False
            
        # Handle related fields (e.g., author__name)
        if '__' in field_name:
            # Check if the root field (before first __) is in search_fields
            root_field = field_name.split('__')[0]
            return any(
                sf == field_name or sf.startswith(root_field + '__') or sf == root_field
                for sf in self.search_fields
            )
        else:
            # Direct field lookup
            return field_name in self.search_fields
    
    def _apply_field_filter(self, queryset, field_name, operator, value):
        """Apply a filter to the queryset based on operator."""
        if field_name is None:
            # This is a general search term, use default search behavior
            return self._apply_default_search(queryset, value)
        
        # Build the filter keyword
        filter_keyword = self._build_filter_keyword(field_name, operator)
        
        # Apply the filter
        if filter_keyword:
            try:
                queryset = queryset.filter(**{filter_keyword: value})
            except Exception:
                # If filter fails, skip this term
                pass
        
        return queryset
    
    def _build_filter_keyword(self, field_name, operator):
        """Build the Django filter keyword based on field and operator."""
        operator_map = {
            'contains': 'icontains',
            'exact': 'iexact',
            'exact_case': 'exact',
            'contains_case': 'contains',
            'endswith': 'iendswith',
            'endswith_case': 'endswith',
            'startswith': 'istartswith',
            'startswith_case': 'startswith',
            'gt': 'gt',
            'gte': 'gte',
            'lt': 'lt',
            'lte': 'lte',
        }
        
        if operator in operator_map:
            return field_name + '__' + operator_map[operator]
        return None
    
    def _apply_default_search(self, queryset, value):
        """Apply default search behavior to all search_fields."""
        if not hasattr(self, 'search_fields') or not self.search_fields:
            return queryset
            
        # Use the default Django admin search logic
        orm_lookups = [f'{field_name}__icontains' for field_name in self.search_fields]
        conditions = []
        for lookup in orm_lookups:
            conditions.append(models.Q(**{lookup: value}))
        
        if conditions:
            queryset = queryset.filter(models.Q(*conditions, _connector=models.Q.OR))
        
        return queryset