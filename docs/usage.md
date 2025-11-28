# Usage Guide

## Requirements

- Python >= 3.12
- Django >= 5.1

Note: This package has been tested specifically on Django 5.1, 5.2 with Python 3.12. While it may work on other versions, compatibility is not guaranteed for versions outside this range.

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
    publication_date = models.DateField()
```

You can configure the admin like this:

```python
class BookAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['title', 'author__name', 'author__email']
    
admin.site.register(Book, BookAdmin)
```

Then in the Django Admin search box, you can use:

- `title:django*` - Books with titles starting with "django" (case-insensitive)
- `author__name:*smith` - Books by authors whose names end with "smith" (case-insensitive)
- `title:==Learning Python` - Books with the exact title "Learning Python" (case-sensitive)
- `title:"Python Programming"` - Books with titles containing the exact phrase "Python Programming"
- `title:python author__name:john` - Books with titles containing "python" AND authors whose names contain "john"

## Combining Multiple Conditions

You can combine multiple search conditions by simply separating them with spaces. The package will apply all conditions using AND logic:

- `title:python author__name:john` - Books with titles containing "python" AND authors whose names contain "john"
- `title:"Python Programming" publication_date:=2020` - Books with titles containing "Python Programming" AND published in 2020
- `author__name:john* title:*programming` - Books by authors whose names start with "john" AND titles ending with "programming"

## Fallback Behavior

If the search term doesn't match any of the advanced syntax patterns, or if parsing fails, the mixin falls back to Django's default search behavior, ensuring compatibility and reliability.
