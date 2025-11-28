"""Django Admin Advanced Search Package

This package provides advanced search functionality for Django Admin interface.
"""

__version__ = '0.1.2'
__author__ = 'shifenhutu'
__email__ = 'shifenhutu@example.com'
__license__ = 'MIT'

# Export main mixin
from .mixins import AdvancedSearchMixin

# Export parser for potential reuse
from .parser import AdvancedSearchParser

# Export field type parsers
from .field_types import get_field_parser
from .field_types.base import BaseFieldParser
from .field_types.string import StringFieldParser
from .field_types.number import NumberFieldParser
from .field_types.datetime import DateTimeFieldParser

# Export utilities
from .utils import convert_value_for_field, parse_date

__all__ = [
    'AdvancedSearchMixin',
    'AdvancedSearchParser',
    'get_field_parser',
    'BaseFieldParser',
    'StringFieldParser',
    'NumberFieldParser',
    'DateTimeFieldParser',
    'convert_value_for_field',
    'parse_date',
]