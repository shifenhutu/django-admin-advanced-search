# Django Admin 高级搜索

[![PyPI](https://img.shields.io/pypi/v/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)
[![License](https://img.shields.io/pypi/l/django-admin-advanced-search)](https://github.com/shifenhutu/django-admin-advanced-search/blob/main/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/django-admin-advanced-search)](https://pypi.org/project/django-admin-advanced-search/)

Django Admin 界面的高级搜索功能，可直接在搜索栏中实现强大的过滤功能。

[English README](README.md)

## 功能特性

- 增强的 Django Admin 搜索能力，支持高级语法
- 支持字段特定搜索和多种操作符
- 支持大小写敏感和大小写不敏感的匹配选项
- 支持引号值的精确短语匹配
- 支持多个条件的AND逻辑组合
- 与现有 Django Admin 界面无缝集成
- 数据库级别的过滤实现，性能优化
- 自动字段类型检测（字符串、数字、日期、时间）
- 针对不同字段类型的解析规则
- 支持数字和日期字段的比较操作符

## 要求

- Python >= 3.12
- Django >= 5.1

注意：此包已在 Django 5.1, 5.2 和 Python 3.12, 3.13, 3.14 上进行了专门测试。虽然它可能在其他版本上工作，但不保证在此范围之外的版本兼容性。

## 安装

```bash
pip install django-admin-advanced-search
```

## 使用方法

1. 将 `django_admin_advanced_search` 添加到你的 `INSTALLED_APPS` 中：

```python
INSTALLED_APPS = [
    ...
    'django_admin_advanced_search',
    ...
]
```

2. 在你的管理类中使用高级搜索：

```python
from django.contrib import admin
from django_admin_advanced_search.mixins import AdvancedSearchMixin

class MyModelAdmin(AdvancedSearchMixin, admin.ModelAdmin):
    search_fields = ['name', 'description', 'author__name']  # 可搜索的字段
    # 你的其他管理配置

admin.site.register(MyModel, MyModelAdmin)
```

## 搜索语法

| 语法 | 描述 | 示例 | SQL 等价 |
|------|------|------|----------|
| `field:value` | 大小写不敏感包含 | `name:john` | `name ILIKE '%john%'` |
| `field:=value` | 大小写不敏感精确匹配 | `name:=john` | `name ILIKE 'john'` |
| `field:==value` | 大小写敏感精确匹配 | `name:==John` | `name = 'John'` |
| `field:!value` | 大小写敏感包含 | `name:!john` | `name LIKE '%john%'` |
| `field:*suffix` | 大小写不敏感后缀匹配 | `name:*son` | `name ILIKE '%son'` |
| `field:!*suffix` | 大小写敏感后缀匹配 | `name:!*son` | `name LIKE '%son'` |
| `field:prefix*` | 大小写不敏感前缀匹配 | `name:john*` | `name ILIKE 'john%'` |
| `field:!prefix*` | 大小写敏感前缀匹配 | `name:!john*` | `name LIKE 'john%'` |
| `field:>value` | 大于（数字/日期） | `price:>100` | `price > 100` |
| `field:>=value` | 大于等于（数字/日期） | `date:>=2023-01-01` | `date >= '2023-01-01'` |
| `field:<value` | 小于（数字/日期） | `price:<1000` | `price < 1000` |
| `field:<=value` | 小于等于（数字/日期） | `date:<=2023-12-31` | `date <= '2023-12-31'` |
| `field:"quoted value"` | 包含空格的值（日期/时间） | `created_at:<"2023-12-31 23:59:59"` | `created_at < '2023-12-31 23:59:59'` |
| `"quoted values"` | 精确短语匹配 | `name:"John Doe"` | `name ILIKE 'John Doe'` |

## 示例

- `title:django*` - 标题以"django"开头的项目（大小写不敏感）
- `author__name:*smith` - 作者姓名以"smith"结尾的项目（大小写不敏感）
- `title:==Learning Python` - 标题精确为"Learning Python"的项目（大小写敏感）
- `title:"Python Programming"` - 标题包含精确短语"Python Programming"的项目
- `title:python author__name:john` - 标题包含"python"且作者姓名包含"john"的项目
- `price:>29.99` - 价格大于29.99的项目
- `publication_date:>=2023-01-01` - 2023年1月1日或之后发布的项目
- `created_at:<"2023-12-31 23:59:59"` - 2023年12月31日晚上11:59:59之前创建的项目（注意包含空格的时间值需要用引号包围）

## 文档

- [使用指南 (中文)](docs/usage_zh.md) | [Usage Guide (English)](docs/usage.md)
- [测试指南 (中文)](docs/testing_zh.md) | [Testing Guide (English)](docs/testing.md)

## 数据库排序和性能说明

- 该包生成数据库级别的过滤器，确保最佳性能
- 对于大小写不敏感的操作，包使用数据库的原生大小写不敏感比较操作符
- 确保数据库列具有适当的排序规则设置以获得最佳性能
- 复杂的多字段搜索可能会生成复杂的 SQL 查询；考虑在经常搜索的字段上添加数据库索引
- 使用相关字段查找时（例如 `author__name:john`），确保外键关系正确建立索引
- 对于数字和日期字段，包会自动检测字段类型并应用适当的比较操作符
- 包含空格的日期时间值必须用引号包围才能正确解析（例如 `created_at:<"2023-12-31 23:59:59"`)

## 贡献

欢迎贡献！请随时提交 Pull Request。

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

该项目采用 MIT 许可证 - 详情请见 [LICENSE](LICENSE) 文件。

项目链接: [https://github.com/shifenhutu/django-admin-advanced-search](https://github.com/shifenhutu/django-admin-advanced-search)