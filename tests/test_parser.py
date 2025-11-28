"""Tests for the new modular parser."""

from django.test import TestCase
from django_admin_advanced_search.parser import AdvancedSearchParser
from django_admin_advanced_search.field_types.string import StringFieldParser
from django_admin_advanced_search.field_types.number import NumberFieldParser
from django_admin_advanced_search.field_types.datetime import DateTimeFieldParser
from tests.models import Book


class BookAdminWithModel:
    """Mock admin class with model for testing field type detection."""
    model = Book
    search_fields = ['title', 'author__name', 'price', 'publication_date', 'created_at']


class ParserTest(TestCase):
    """Test cases for the new modular parser."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.admin = BookAdminWithModel()
        self.parser = AdvancedSearchParser(self.admin.model, self.admin.search_fields)
    
    def test_string_field_parsing(self):
        """Test parsing of string fields with various operators."""
        # Test case-insensitive contains (default)
        result = self.parser.parse('title:python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__icontains', result['filters'])
        self.assertEqual(result['filters']['title__icontains'], 'python')
        
        # Test case-insensitive exact
        result = self.parser.parse('title:=python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__iexact', result['filters'])
        self.assertEqual(result['filters']['title__iexact'], 'python')
        
        # Test case-sensitive exact
        result = self.parser.parse('title:==Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__exact', result['filters'])
        self.assertEqual(result['filters']['title__exact'], 'Python')
        
        # Test case-sensitive contains
        result = self.parser.parse('title:!Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__contains', result['filters'])
        self.assertEqual(result['filters']['title__contains'], 'Python')
        
        # Test case-insensitive endswith
        result = self.parser.parse('title:*programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__iendswith', result['filters'])
        self.assertEqual(result['filters']['title__iendswith'], 'programming')
        
        # Test case-sensitive endswith
        result = self.parser.parse('title:!*Programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__endswith', result['filters'])
        self.assertEqual(result['filters']['title__endswith'], 'Programming')
        
        # Test case-insensitive startswith
        result = self.parser.parse('title:python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__istartswith', result['filters'])
        self.assertEqual(result['filters']['title__istartswith'], 'python')
        
        # Test case-sensitive startswith
        result = self.parser.parse('title:!Python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__startswith', result['filters'])
        self.assertEqual(result['filters']['title__startswith'], 'Python')
    
    def test_number_field_parsing(self):
        """Test parsing of number fields with comparison operators."""
        # Test greater than
        result = self.parser.parse('price:>10')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price__gt', result['filters'])
        self.assertEqual(result['filters']['price__gt'], 10)
        
        # Test less than or equal
        result = self.parser.parse('price:<=20.50')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price__lte', result['filters'])
        self.assertEqual(result['filters']['price__lte'], 20.5)
        
        # Test invalid number (should be treated as plain text)
        result = self.parser.parse('price:>invalid')
        # Parsing should not fail, but the term should be treated as plain text
        # since we can't convert 'invalid' to a number
        self.assertFalse(result['has_advanced'])
    
    def test_number_range_parsing(self):
        """Test parsing of number ranges with .. syntax."""
        # Test complete range
        result = self.parser.parse('price:100..200')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price__gte', result['filters'])
        self.assertIn('price__lte', result['filters'])
        self.assertEqual(result['filters']['price__gte'], 100)
        self.assertEqual(result['filters']['price__lte'], 200)
        
        # Test range with only start value
        result = self.parser.parse('price:100..')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price__gte', result['filters'])
        self.assertEqual(result['filters']['price__gte'], 100)
        self.assertNotIn('price__lte', result['filters'])
        
        # Test range with only end value
        result = self.parser.parse('price:..200')
        self.assertTrue(result['has_advanced'])
        self.assertIn('price__lte', result['filters'])
        self.assertEqual(result['filters']['price__lte'], 200)
        self.assertNotIn('price__gte', result['filters'])
    
    def test_date_field_parsing(self):
        """Test parsing of date fields with comparison operators."""
        # Test datetime less than with quoted value (because of space)
        result = self.parser.parse('created_at:<"2023-12-31 23:59:59"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('created_at__lt', result['filters'])
        self.assertEqual(result['filters']['created_at__lt'], '2023-12-31 23:59:59')
        
        # Test date equality with quoted value
        result = self.parser.parse('publication_date:"2023-06-15"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date__exact', result['filters'])
        self.assertEqual(result['filters']['publication_date__exact'], '2023-06-15')
        
        # Test date with unquoted value (without spaces)
        result = self.parser.parse('publication_date:2023-06-15')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date__exact', result['filters'])
        self.assertEqual(result['filters']['publication_date__exact'], '2023-06-15')
    
    def test_date_range_parsing(self):
        """Test parsing of date ranges with .. syntax."""
        # Test complete date range
        result = self.parser.parse('publication_date:2023-01-01..2023-12-31')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date__gte', result['filters'])
        self.assertIn('publication_date__lte', result['filters'])
        self.assertEqual(result['filters']['publication_date__gte'], '2023-01-01')
        self.assertEqual(result['filters']['publication_date__lte'], '2023-12-31')
        
        # Test date range with only start value
        result = self.parser.parse('publication_date:2023-01-01..')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date__gte', result['filters'])
        self.assertEqual(result['filters']['publication_date__gte'], '2023-01-01')
        self.assertNotIn('publication_date__lte', result['filters'])
        
        # Test date range with only end value
        result = self.parser.parse('publication_date:..2023-12-31')
        self.assertTrue(result['has_advanced'])
        self.assertIn('publication_date__lte', result['filters'])
        self.assertEqual(result['filters']['publication_date__lte'], '2023-12-31')
        self.assertNotIn('publication_date__gte', result['filters'])
    
    def test_related_field_search(self):
        """Test search on related fields."""
        # Test author__name:john* (related field startswith)
        result = self.parser.parse('author__name:john*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('author__name__istartswith', result['filters'])
        self.assertEqual(result['filters']['author__name__istartswith'], 'john')
    
    def test_quoted_values_search(self):
        """Test search with quoted values."""
        # Test quoted values
        result = self.parser.parse('title:"Python Programming"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__icontains', result['filters'])
        self.assertEqual(result['filters']['title__icontains'], 'Python Programming')
    
    def test_multiple_conditions(self):
        """Test multiple conditions combination."""
        # Test multiple conditions
        result = self.parser.parse('title:python author__name:john')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__icontains', result['filters'])
        self.assertIn('author__name__icontains', result['filters'])
        self.assertEqual(result['filters']['title__icontains'], 'python')
        self.assertEqual(result['filters']['author__name__icontains'], 'john')
    
    def test_plain_text_fallback(self):
        """Test that non-matching terms are treated as plain text."""
        # Test with a field that's not in search_fields
        result = self.parser.parse('invalid_field:test')
        # Should be treated as plain text since invalid_field is not in search_fields
        self.assertFalse(result['has_advanced'])
        self.assertEqual(result['plain_text'], 'invalid_field:test')
        
        # Test mixed valid and invalid fields
        result = self.parser.parse('title:python invalid_field:test')
        # Valid field should be parsed, invalid should be plain text
        self.assertTrue(result['has_advanced'])
        self.assertIn('title__icontains', result['filters'])
        # The invalid field should appear in plain_text
        self.assertIn('invalid_field:test', result['plain_text'])


class FieldParserTest(TestCase):
    """Test cases for individual field parsers."""
    
    def test_string_field_parser(self):
        """Test string field parser."""
        parser = StringFieldParser()
        
        # Test basic parsing
        result = parser.parse('python', 'title')
        self.assertEqual(result, {'title__icontains': 'python'})
        
        # Test with modifier
        result = parser.parse('python', 'title', '==')
        self.assertEqual(result, {'title__exact': 'python'})
    
    def test_number_field_parser(self):
        """Test number field parser."""
        parser = NumberFieldParser()
        
        # Test integer parsing
        result = parser.parse('10', 'price', '>')
        self.assertEqual(result, {'price__gt': 10})
        
        # Test float parsing
        result = parser.parse('20.5', 'price', '<=')
        self.assertEqual(result, {'price__lte': 20.5})
        
        # Test range parsing
        result = parser.parse('100..200', 'price')
        self.assertEqual(result, {'price__gte': 100, 'price__lte': 200})
        
        # Test range with only start value
        result = parser.parse('100..', 'price')
        self.assertEqual(result, {'price__gte': 100})
        
        # Test range with only end value
        result = parser.parse('..200', 'price')
        self.assertEqual(result, {'price__lte': 200})
        
        # Test invalid number
        with self.assertRaises(ValueError):
            parser.parse('invalid', 'price', '>')
    
    def test_datetime_field_parser(self):
        """Test datetime field parser."""
        parser = DateTimeFieldParser()
        
        # Test basic parsing
        result = parser.parse('2023-12-31', 'created_at', '>=')
        self.assertEqual(result, {'created_at__gte': '2023-12-31'})
        
        # Test range parsing
        result = parser.parse('2023-01-01..2023-12-31', 'publication_date')
        self.assertEqual(result, {'publication_date__gte': '2023-01-01', 'publication_date__lte': '2023-12-31'})
        
        # Test range with only start value
        result = parser.parse('2023-01-01..', 'publication_date')
        self.assertEqual(result, {'publication_date__gte': '2023-01-01'})
        
        # Test range with only end value
        result = parser.parse('..2023-12-31', 'publication_date')
        self.assertEqual(result, {'publication_date__lte': '2023-12-31'})