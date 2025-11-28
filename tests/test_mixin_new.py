"""Tests for the AdvancedSearchMixin."""

from django.test import TestCase
from django.contrib.admin import AdminSite
from django_admin_advanced_search.mixins import AdvancedSearchMixin
from tests.models import Author, Book


class BookAdmin(AdvancedSearchMixin):
    """Mock admin class for testing."""
    search_fields = ['title', 'author__name', 'price', 'publication_date']
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)


class AdvancedSearchMixinTest(TestCase):
    """Test cases for AdvancedSearchMixin."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create test data
        self.author = Author.objects.create(name="John Doe")
        self.book1 = Book.objects.create(
            title="Python Programming",
            author=self.author,
            price=29.99,
            publication_date="2023-01-01"
        )
        self.book2 = Book.objects.create(
            title="Java Programming",
            author=self.author,
            price=39.99,
            publication_date="2023-06-01"
        )
    
    def test_get_search_results(self):
        """Test the get_search_results method."""
        admin_site = AdminSite()
        admin = BookAdmin(Book, admin_site)
        
        # Test basic search
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), 'Python'
        )
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Python Programming")
        
        # Test field-specific search
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), 'title:Python*'
        )
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Python Programming")
        
        # Test price search
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), 'price:>30'
        )
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Java Programming")
        
        # Test multiple conditions
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), 'title:*Programming price:<35'
        )
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().title, "Python Programming")
        
        # Test empty search
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), ''
        )
        self.assertEqual(queryset.count(), 2)  # Both books
        
        # Test non-matching search
        queryset, may_have_duplicates = admin.get_search_results(
            None, Book.objects.all(), 'title:NonExistent'
        )
        self.assertEqual(queryset.count(), 0)