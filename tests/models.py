"""Test models for django-admin-advanced-search."""

from django.db import models


class Author(models.Model):
    """Test author model."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    
    class Meta:
        app_label = 'tests'


class Book(models.Model):
    """Test book model."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    publication_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'tests'