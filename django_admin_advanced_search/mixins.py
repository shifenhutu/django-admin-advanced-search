"""Advanced search functionality for Django Admin."""

from django.contrib import admin
from django.db import models
from .parser import AdvancedSearchParser
from .utils import convert_value_for_field


class AdvancedSearchMixin(admin.ModelAdmin):
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
            # Ensure we have a model attribute
            if not hasattr(self, 'model') or not self.model:
                # Try to get model from queryset
                self.model = queryset.model
            
            parser = AdvancedSearchParser(self.model, self.search_fields)
            result = parser.parse(search_term)
        except Exception:
            # 解析失败 → 回退到默认行为
            return super().get_search_results(request, queryset, search_term)

        if result['has_advanced']:
            qs = queryset
            for field_key, value in result['filters'].items():
                # Extract field name and lookup from the key (e.g., "title__icontains")
                if '__' in field_key:
                    field_name = '__'.join(field_key.split('__')[:-1])
                else:
                    field_name = field_key
                
                # Try to convert value to appropriate type based on field type
                try:
                    converted_value = convert_value_for_field(
                        self.model._meta.get_field(field_name.split('__')[0]), 
                        value
                    )
                    if converted_value is not None:
                        value = converted_value
                except:
                    # If conversion fails, use original value
                    pass
                
                qs = qs.filter(**{field_key: value})
            return qs.distinct(), False
        else:
            return super().get_search_results(request, queryset, result['plain_text'])