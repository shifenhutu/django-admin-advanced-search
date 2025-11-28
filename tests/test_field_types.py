"""Tests for field type detection in AdvancedSearchMixin."""

from django.test import TestCase
from django_admin_advanced_search.field_types.string import StringFieldParser
from django_admin_advanced_search.field_types.number import NumberFieldParser
from django_admin_advanced_search.field_types.datetime import DateTimeFieldParser
from tests.models import Book


class FieldTypesTest(TestCase):
    """Test cases for field type detection."""
    
    def test_field_parser_support(self):
        """Test that field parsers correctly identify supported fields."""
        # Test string field parser
        from django.db import models
        string_field = models.CharField(max_length=100)
        self.assertTrue(StringFieldParser.supports(string_field))
        
        # Test number field parser
        int_field = models.IntegerField()
        float_field = models.FloatField()
        self.assertTrue(NumberFieldParser.supports(int_field))
        self.assertTrue(NumberFieldParser.supports(float_field))
        
        # Test datetime field parser
        date_field = models.DateField()
        datetime_field = models.DateTimeField()
        self.assertTrue(DateTimeFieldParser.supports(date_field))
        self.assertTrue(DateTimeFieldParser.supports(datetime_field))
    
    def test_string_field_parsing(self):
        """Test parsing of string fields with various operators."""
        parser = StringFieldParser()
        
        # Test case-insensitive contains (default)
        result = parser.parse('python', 'title')
        self.assertEqual(result, {'title__icontains': 'python'})
        
        # Test case-insensitive exact
        result = parser.parse('python', 'title', '=')
        self.assertEqual(result, {'title__iexact': 'python'})
        
        # Test case-sensitive exact
        result = parser.parse('Python', 'title', '==')
        self.assertEqual(result, {'title__exact': 'Python'})
    
    def test_number_field_parsing(self):
        """Test parsing of number fields with comparison operators."""
        parser = NumberFieldParser()
        
        # Test greater than
        result = parser.parse('10', 'price', '>')
        self.assertEqual(result, {'price__gt': 10})
        
        # Test less than or equal
        result = parser.parse('20.50', 'price', '<=')
        self.assertEqual(result, {'price__lte': 20.5})
        
        # Test invalid number (should raise ValueError)
        with self.assertRaises(ValueError):
            parser.parse('invalid', 'price', '>')
    
    def test_datetime_field_parsing(self):
        """Test parsing of date fields with comparison operators."""
        parser = DateTimeFieldParser()
        
        # Test datetime less than
        result = parser.parse('2023-12-31 23:59:59', 'created_at', '<')
        self.assertEqual(result, {'created_at__lt': '2023-12-31 23:59:59'})
        
        # Test date equality
        result = parser.parse('2023-06-15', 'publication_date', '=')
        self.assertEqual(result, {'publication_date__exact': '2023-06-15'})