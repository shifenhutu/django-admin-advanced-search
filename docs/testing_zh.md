# 测试指南

## 运行测试

该包使用Django内置的测试框架。运行测试的方法：

```bash
python -m django test tests --settings=tests.settings
```

或者如果您已安装并配置了Django：

```bash
python manage.py test tests
```

## 测试结构

测试位于`tests/`目录中：

- `tests/settings.py` - 运行测试的Django设置
- `tests/test_mixin.py` - `AdvancedSearchMixin`类的测试用例

## 测试用例

测试套件验证以下功能：

1. **解析功能** - 确保搜索词根据语法规则正确解析
2. **字段允许性** - 验证仅允许`search_fields`中的字段以确保安全性
3. **过滤关键字构建** - 检查Django ORM过滤关键字是否正确构造
4. **操作符映射** - 验证操作符是否正确映射到Django ORM查找

## 编写新测试

添加新测试用例的方法：

1. 向`tests/test_mixin.py`添加新的测试方法
2. 遵循现有模式创建带有`search_fields`的模拟admin类
3. 使用Django的`TestCase`断言来验证行为

测试结构示例：

```python
def test_new_feature(self):
    """测试内容描述。"""
    admin = BookAdmin()  # 模拟admin类
    # 执行测试
    result = admin.some_method('test_input')
    # 断言期望行为
    self.assertEqual(result, 'expected_output')
```

## 持续集成

该包包含GitHub Actions配置，用于跨多个Python和Django版本的持续集成测试。测试会在推送到主分支和拉取请求时自动运行。

## 测试覆盖

当前测试套件覆盖：

- 所有搜索语法操作符（`:`、`:=`、`:==`、`:!`、`:*`、`:!*`、`:*`、`:!*`）
- 字段允许性安全检查
- 相关字段处理（例如`author__name`）
- Django ORM的过滤关键字构建
- 错误处理和回退行为

## 手动测试

在Django项目中进行手动测试：

1. 安装包：`pip install django-admin-advanced-search`
2. 添加到`INSTALLED_APPS`
3. 将mixin应用到配置了`search_fields`的模型admin
4. 使用Django Admin界面测试各种搜索查询