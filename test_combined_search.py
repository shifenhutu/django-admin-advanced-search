#!/usr/bin/env python
"""Test script to verify combined advanced and plain text search."""

import os
import sys
import django
from django.conf import settings

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
if not settings.configured:
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'django_admin_advanced_search',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        USE_TZ=True,
    )

django.setup()

from django.db import models
from django.contrib.admin import ModelAdmin
from django.contrib.admin.sites import AdminSite
from django_admin_advanced_search.mixins import AdvancedSearchMixin

# Create a simple model for testing
class Person(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    class Meta:
        app_label = 'test'

# Create a test admin class
class PersonAdmin(AdvancedSearchMixin, ModelAdmin):
    search_fields = ['name', 'description']
    
    def __init__(self):
        super().__init__(Person, AdminSite())

def test_combined_search():
    """Test combined advanced and plain text search."""
    admin = PersonAdmin()
    
    # Test the parser directly first
    from django_admin_advanced_search.parser import parse_advanced_search
    result = parse_advanced_search('name:=john lisa', ['name', 'description'])
    print("Parsed result:", result)
    
    # Test with a simple queryset
    # Just verify the method doesn't crash
    try:
        # Create a mock request object
        class MockRequest:
            pass
            
        request = MockRequest()
        
        # Create a simple queryset
        queryset = Person.objects.all()
        
        # Test the search method
        result_queryset, may_have_duplicates = admin.get_search_results(
            request, queryset, 'name:=john lisa'
        )
        print("Search completed successfully")
        print("Result queryset:", result_queryset)
        print("May have duplicates:", may_have_duplicates)
        
    except Exception as e:
        print("Error occurred:", str(e))
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_combined_search()