"""Advanced search parser for Django Admin."""

import re
from django.db import models
from .field_types import get_field_parser


class AdvancedSearchParser:
    """Parse search terms using advanced syntax with field type awareness."""
    
    def __init__(self, model, search_fields):
        self.model = model
        self.search_fields = search_fields or []
        self.field_info = self._build_field_info()
    
    def _build_field_info(self):
        """Build field information mapping."""
        info = {}
        for field_path in self.search_fields:
            parts = field_path.split("__")
            model = self.model
            for part in parts[:-1]:
                rel = model._meta.get_field(part)
                model = getattr(rel, 'related_model', model)
            final_field = model._meta.get_field(parts[-1])
            info[field_path] = final_field
        return info
    
    def parse(self, text):
        """Parse search terms using advanced syntax."""
        if not self.search_fields:
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
            
            # 添加匹配之前的普通文本
            plain_parts.append(text[last_end:start])
            
            # 只处理允许的字段
            if field not in self.field_info:
                # 添加整个匹配项作为普通文本
                plain_parts.append(text[start:end])
                last_end = end
                continue
            
            # 根据字段类型确定如何处理
            field_obj = self.field_info[field]
            parser = get_field_parser(field_obj)
            
            try:
                # 解析值
                result = parser.parse(raw_value, field, modifier)
                if result:
                    filters.update(result)
                else:
                    # 添加匹配项作为普通文本
                    plain_parts.append(text[start:end])
            except ValueError:
                # 如果解析失败，将整个匹配项作为普通文本
                plain_parts.append(text[start:end])
            
            last_end = end
        
        # 添加最后剩余的普通文本
        plain_parts.append(text[last_end:])
        plain_text = ' '.join(p.strip() for p in plain_parts if p.strip()).strip()
        
        return {
            'has_advanced': bool(filters),
            'filters': filters,
            'plain_text': plain_text,
        }