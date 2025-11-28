"""Tests for field type detection in AdvancedSearchMixin."""

from django.test import TestCase
from django_admin_advanced_search.mixins import AdvancedSearchMixin
from tests.models import Book


class BookAdminWithModel(AdvancedSearchMixin):
    """Mock admin class with model for testing field type detection."""
    model = Book
    search_fields = ['title', 'author__name', 'price', 'publication_date', 'created_at']


class FieldTypesTest(TestCase):
    """Test cases for field type detection."""
    
    def test_get_field_type(self):
        """Test field type detection."""
        admin = BookAdminWithModel()
        
        # Test string field
        self.assertEqual(admin._get_field_type('title'), 'str')
        
        # Test related string field
        self.assertEqual(admin._get_field_type('author__name'), 'str')
        
        # Test number field
        self.assertEqual(admin._get_field_type('price'), 'number')
        
        # Test date field
        self.assertEqual(admin._get_field_type('publication_date'), 'date')
        
        # Test datetime field
        self.assertEqual(admin._get_field_type('created_at'), 'datetime')

    def test_number_field_parsing(self):
        """Test parsing of number fields with comparison operators."""
        admin = BookAdminWithModel()
        
        # Test greater than
        result = admin._parse_advanced_search('price:>10')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price', result['filters'])
        self.assertEqual(result['filters']['price'], ('gt', 10))
        
        # Test less than or equal
        result = admin._parse_advanced_search('price:<=20.50')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price', result['filters'])
        self.assertEqual(result['filters']['price'], ('lte', 20.5))
        
        # Test invalid number (should fallback to plain text)
        result = admin._parse_advanced_search('price:>invalid')
        self.assertFalse(result['has_advanced'])

    def test_date_field_parsing(self):
        """Test parsing of date fields with comparison operators."""
        admin = BookAdminWithModel()
        
        # Test date greater than with quoted value (because of space)
        result = admin._parse_advanced_search('created_at:<"2023-12-31 23:59:59"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('created_at', result['filters'])
        
        # Test date equality with quoted value
        result = admin._parse_advanced_search('publication_date:"2023-06-15"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date', result['filters'])
        
        # Test date with unquoted value (without spaces)
        result = admin._parse_advanced_search('publication_date:2023-06-15')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date', result['filters'])