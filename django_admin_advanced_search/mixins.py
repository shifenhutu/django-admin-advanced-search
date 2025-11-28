"""Advanced search functionality for Django Admin."""

import re
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _

# 123 test

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
                qs = qs.filter(**{f"{field}__{lookup}": value})
            return qs.distinct(), False
        else:
            return super().get_search_results(request, queryset, parsed['plain_text'])
    
    def _parse_advanced_search(self, text):
        """Parse search terms using advanced syntax."""
        allowed_fields = set(getattr(self, 'search_fields', []))
        if not allowed_fields:
            return {'has_advanced': False, 'filters': {}, 'plain_text': text}

        # 正则表达式匹配 field:modifier"value" 或 field:modifier value
        # Groups: 1=field, 2=modifier(==|=|!), 4=quoted_value, 5=unquoted_value
        pattern = r'(\S+?):((?:==|[=!])?)("([^"]*)"|(\S+))'
        filters = {}
        plain_parts = []
        last_end = 0

        for match in re.finditer(pattern, text):
            field = match.group(1)
            modifier = match.group(2) or ''
            quoted_val = match.group(4)
            unquoted_val = match.group(5)
            raw_value = quoted_val or unquoted_val
            start, end = match.span()

            # 只处理允许的字段
            if field not in allowed_fields:
                plain_parts.append(match.group(0))
                continue

            # 根据修饰符确定查找类型
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