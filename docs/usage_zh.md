# 使用指南

## 要求

- Python >= 3.12
- Django >= 5.1

注意：此包已在 Django 5.1, 5.2 和 Python 3.12 上进行了专门测试。虽然它可能在其他版本上工作，但不保证在此范围之外的版本兼容性。

## 安装

使用pip安装该包：

```bash
pip install django-admin-advanced-search
```

## 设置

1. 在`settings.py`中的`INSTALLED_APPS`添加`django_admin_advanced_search`：

```python
INSTALLED_APPS = [
    ...
    'django_admin_advanced_search',
    ...
]
```

2. 在`admin.py`中导入并使用`AdvancedSearchMixin`：

```python
from django.contrib import admin
from django_admin_advanced_search.mixins import AdvancedSearchMixin

class MyModelAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['field1', 'field2', 'related_model__field']
    # ... 其他配置

admin.site.register(MyModel, MyModelAdmin)
```

## 搜索语法

该包在Django Admin搜索框中支持以下高级搜索语法：

| 语法 | 描述 | 示例 | 匹配内容 |
|------|------|------|----------|
| `field:value` | 大小写不敏感包含 | `name:john` | 包含"john"的字段（大小写不敏感） |
| `field:=value` | 大小写不敏感精确匹配 | `name:=john` | 精确等于"john"的字段（大小写不敏感） |
| `field:==value` | 大小写敏感精确匹配 | `name:==John` | 精确等于"John"的字段（大小写敏感） |
| `field:!value` | 大小写敏感包含 | `name:!John` | 包含"John"的字段（大小写敏感） |
| `field:*suffix` | 大小写不敏感后缀匹配 | `name:*son` | 以"son"结尾的字段（大小写不敏感） |
| `field:!*suffix` | 大小写敏感后缀匹配 | `name:!*son` | 以"son"结尾的字段（大小写敏感） |
| `field:prefix*` | 大小写不敏感前缀匹配 | `name:john*` | 以"john"开头的字段（大小写不敏感） |
| `field:!prefix*` | 大小写敏感前缀匹配 | `name:!John*` | 以"John"开头的字段（大小写敏感） |


## 安全性

出于安全原因，该mixin只允许搜索在`search_fields`中明确列出的字段。这可以防止用户搜索非预期的字段。

## 示例

给定如下模型：

```python
class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    publication_date = models.DateField()
```

您可以按如下方式配置admin：

```python
class BookAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['title', 'author__name', 'author__email']
    
admin.site.register(Book, BookAdmin)
```

然后在Django Admin搜索框中，您可以使用：

- `title:django*` - 标题以"django"开头的书籍（大小写不敏感）
- `author__name:*smith` - 作者姓名以"smith"结尾的书籍（大小写不敏感）
- `title:==Learning Python` - 标题精确为"Learning Python"的书籍（大小写敏感）
- `title:"Python Programming"` - 标题包含精确短语"Python Programming"的书籍
- `title:python author__name:john` - 标题包含"python"且作者姓名包含"john"的书籍

## 组合多个条件

您可以通过简单地用空格分隔来组合多个搜索条件。包将使用AND逻辑应用所有条件：

- `title:python author__name:john` - 标题包含"python"且作者姓名包含"john"的书籍
- `title:"Python Programming" publication_date:=2020` - 标题包含"Python Programming"且出版年份为2020的书籍
- `author__name:john* title:*programming` - 作者姓名以"john"开头且标题以"programming"结尾的书籍

## 回退行为

如果搜索词不匹配任何高级语法模式，或者解析失败，该mixin会回退到Django的默认搜索行为，确保兼容性和可靠性。
