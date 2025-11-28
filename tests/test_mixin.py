"""Tests for the AdvancedSearchMixin."""

from django.test import TestCase
from django_admin_advanced_search.mixins import AdvancedSearchMixin


class BookAdmin(AdvancedSearchMixin):
    """Mock admin class for testing."""
    search_fields = ['title', 'author__name', 'price', 'publication_date']


class AdvancedSearchMixinTest(TestCase):
    """Test cases for AdvancedSearchMixin."""
    
    def test_contains_search(self):
        """Test case-insensitive contains search."""
        admin = BookAdmin()
        # Test field:value (case-insensitive contains)
        result = admin._parse_advanced_search('title:python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
    
    def test_exact_search(self):
        """Test case-insensitive exact search."""
        admin = BookAdmin()
        # Test field:=value (case-insensitive exact)
        result = admin._parse_advanced_search('title:=python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iexact', 'python'))
    
    def test_exact_case_search(self):
        """Test case-sensitive exact search."""
        admin = BookAdmin()
        # Test field:==value (case-sensitive exact)
        result = admin._parse_advanced_search('title:==Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('exact', 'Python'))
    
    def test_contains_case_search(self):
        """Test case-sensitive contains search."""
        admin = BookAdmin()
        # Test field:!value (case-sensitive contains)
        result = admin._parse_advanced_search('title:!Python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('contains', 'Python'))
    
    def test_endswith_search(self):
        """Test case-insensitive endswith search."""
        admin = BookAdmin()
        # Test field:*suffix (case-insensitive endswith)
        result = admin._parse_advanced_search('title:*programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('iendswith', 'programming'))
    
    def test_endswith_case_search(self):
        """Test case-sensitive endswith search."""
        admin = BookAdmin()
        # Test field:!*suffix (case-sensitive endswith)
        result = admin._parse_advanced_search('title:!*Programming')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('endswith', 'Programming'))
    
    def test_startswith_search(self):
        """Test case-insensitive startswith search."""
        admin = BookAdmin()
        # Test field:prefix* (case-insensitive startswith)
        result = admin._parse_advanced_search('title:python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('istartswith', 'python'))
    
    def test_startswith_case_search(self):
        """Test case-sensitive startswith search."""
        admin = BookAdmin()
        # Test field:!prefix* (case-sensitive startswith)
        result = admin._parse_advanced_search('title:!Python*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('startswith', 'Python'))
    
    def test_related_field_search(self):
        """Test search on related fields."""
        admin = BookAdmin()
        # Test author__name:john* (related field startswith)
        result = admin._parse_advanced_search('author__name:john*')
        self.assertTrue(result['has_advanced'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['author__name'], ('istartswith', 'john'))
    
    def test_quoted_values_search(self):
        """Test search with quoted values."""
        admin = BookAdmin()
        # Test quoted values
        result = admin._parse_advanced_search('title:"Python Programming"')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'Python Programming'))
    
    def test_multiple_conditions(self):
        """Test multiple conditions combination."""
        admin = BookAdmin()
        # Test multiple conditions
        result = admin._parse_advanced_search('title:python author__name:john')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertIn('author__name', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        self.assertEqual(result['filters']['author__name'], ('icontains', 'john'))
    
    def test_field_whitelist_security(self):
        """Test that only whitelisted fields can be searched."""
        admin = BookAdmin()
        # Test allowed fields
        self.assertTrue(admin._is_field_allowed('title'))
        self.assertTrue(admin._is_field_allowed('author__name'))
        
        # Test disallowed fields
        self.assertFalse(admin._is_field_allowed('author_id'))
        self.assertFalse(admin._is_field_allowed('description'))
    
    def test_filter_keyword_building(self):
        """Test filter keyword building functionality."""
        admin = BookAdmin()
        # Test different operators
        self.assertEqual(admin._build_filter_keyword('title', 'contains'), 'title__icontains')
        self.assertEqual(admin._build_filter_keyword('title', 'exact'), 'title__iexact')
        self.assertEqual(admin._build_filter_keyword('title', 'exact_case'), 'title__exact')
        self.assertEqual(admin._build_filter_keyword('title', 'contains_case'), 'title__contains')
        self.assertEqual(admin._build_filter_keyword('title', 'endswith'), 'title__iendswith')
        self.assertEqual(admin._build_filter_keyword('title', 'endswith_case'), 'title__endswith')
        self.assertEqual(admin._build_filter_keyword('title', 'startswith'), 'title__istartswith')
        self.assertEqual(admin._build_filter_keyword('title', 'startswith_case'), 'title__startswith')
        # Test comparison operators
        self.assertEqual(admin._build_filter_keyword('price', 'gt'), 'price__gt')
        self.assertEqual(admin._build_filter_keyword('price', 'gte'), 'price__gte')
        self.assertEqual(admin._build_filter_keyword('price', 'lt'), 'price__lt')
        self.assertEqual(admin._build_filter_keyword('price', 'lte'), 'price__lte')
        
        # Test invalid operator
        self.assertIsNone(admin._build_filter_keyword('title', 'invalid'))
    
    def test_comparison_operators_with_strings(self):
        """Test that comparison operators work with string fields when field type detection fails."""
        admin = BookAdmin()
        # Test field:>value with string field (fallback behavior)
        result = admin._parse_advanced_search('title:>python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        # When field type detection fails, it falls back to string handling
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        
        # Test field:>=value with string field (fallback behavior)
        result = admin._parse_advanced_search('title:>=python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        
        # Test field:<value with string field (fallback behavior)
        result = admin._parse_advanced_search('title:<python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))
        
        # Test field:<=value with string field (fallback behavior)
        result = admin._parse_advanced_search('title:<=python')
        self.assertTrue(result['has_advanced'])
        self.assertIn('title', result['filters'])
        self.assertEqual(result['filters']['title'], ('icontains', 'python'))