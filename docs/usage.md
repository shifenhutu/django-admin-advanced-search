# Usage Guide

## Requirements

- Python >= 3.12
- Django >= 5.1

Note: This package has been tested specifically on Django 5.1, 5.2 with Python 3.12, 3.13, 3.14. While it may work on other versions, compatibility is not guaranteed for versions outside this range.

## Installation

Install the package using pip:

```bash
pip install django-admin-advanced-search
```

## Setup

1. Add `django_admin_advanced_search` to your `INSTALLED_APPS` in `settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_admin_advanced_search',
    ...
]
```

2. In your `admin.py`, import and use the `AdvancedSearchMixin`:

```python
from django.contrib import admin
from django_admin_advanced_search.mixins import AdvancedSearchMixin

class MyModelAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['field1', 'field2', 'related_model__field']
    # ... other configurations

admin.site.register(MyModel, MyModelAdmin)
```

## Search Syntax

The package supports the following advanced search syntax in the Django Admin search box:

| Syntax | Description | Example | Matches |
|--------|-------------|---------|---------|
| `field:value` | Case-insensitive contains | `name:john` | Fields containing "john" (case-insensitive) |
| `field:=value` | Case-insensitive exact | `name:=john` | Fields exactly equal to "john" (case-insensitive) |
| `field:==value` | Case-sensitive exact | `name:==John` | Fields exactly equal to "John" (case-sensitive) |
| `field:!value` | Case-sensitive contains | `name:!John` | Fields containing "John" (case-sensitive) |
| `field:*suffix` | Case-insensitive ends with | `name:*son` | Fields ending with "son" (case-insensitive) |
| `field:!*suffix` | Case-sensitive ends with | `name:!*son` | Fields ending with "son" (case-sensitive) |
| `field:prefix*` | Case-insensitive starts with | `name:john*` | Fields starting with "john" (case-insensitive) |
| `field:!prefix*` | Case-sensitive starts with | `name:!John*` | Fields starting with "John" (case-sensitive) |
| `field:>value` | Greater than (numbers/dates) | `price:>100` | Fields greater than 100 |
| `field:>=value` | Greater than or equal (numbers/dates) | `date:>=2023-01-01` | Fields greater than or equal to 2023-01-01 |
| `field:<value` | Less than (numbers/dates) | `price:<1000` | Fields less than 1000 |
| `field:<=value` | Less than or equal (numbers/dates) | `date:<=2023-12-31` | Fields less than or equal to 2023-12-31 |
| `field:"quoted value"` | Values with spaces (dates/times) | `created_at:<"2023-12-31 23:59:59"` | Fields less than 2023-12-31 23:59:59 |
| `"quoted values"` | Exact phrase matching | `name:"John Doe"` | Fields containing the exact phrase "John Doe" |

## Security

The mixin only allows searching on fields explicitly listed in `search_fields` for security reasons. This prevents users from searching on unintended fields.

## Examples

Given a model like this:

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    publication_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

You can configure the admin like this:

```python
class BookAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['title', 'author__name', 'author__email', 'price', 'publication_date', 'created_at']
    
admin.site.register(Book, BookAdmin)
```

Then in the Django Admin search box, you can use:

- `title:django*` - Books with titles starting with "django" (case-insensitive)
- `author__name:*smith` - Books by authors whose names end with "smith" (case-insensitive)
- `title:==Learning Python` - Books with the exact title "Learning Python" (case-sensitive)
- `title:"Python Programming"` - Books with titles containing the exact phrase "Python Programming"
- `title:python author__name:john` - Books with titles containing "python" AND authors whose names contain "john"
- `price:>29.99` - Books with price greater than 29.99
- `publication_date:>=2023-01-01` - Books published on or after January 1, 2023
- `created_at:<"2023-12-31 23:59:59"` - Books created before December 31, 2023 11:59:59 PM (note the quotes around the datetime value with spaces)

## Combining Multiple Conditions

You can combine multiple search conditions by simply separating them with spaces. The package will apply all conditions using AND logic:

- `title:python author__name:john` - Books with titles containing "python" AND authors whose names contain "john"
- `title:"Python Programming" publication_date:=2020` - Books with titles containing "Python Programming" AND published in 2020
- `author__name:john* title:*programming` - Books by authors whose names start with "john" AND titles ending with "programming"
- `price:>29.99 publication_date:>=2023-01-01` - Books with price greater than 29.99 AND published on or after January 1, 2023

## Fallback Behavior

If the search term doesn't match any of the advanced syntax patterns, or if parsing fails, the mixin falls back to Django's default search behavior, ensuring compatibility and reliability.

For number and date fields, if the provided value cannot be converted to the appropriate type (e.g., providing a non-numeric value for a numeric field), the mixin will also fall back to plain text search instead of throwing an error.
