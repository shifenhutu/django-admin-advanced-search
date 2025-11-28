"""Utility functions for advanced search."""

from datetime import datetime, date


def parse_date(value_str, is_datetime=True):
    """Parse a date string into a datetime or date object.
    
    Args:
        value_str: The date string to parse
        is_datetime: Whether to return a datetime (True) or date (False) object
        
    Returns:
        datetime or date object, or the original string if parsing fails
    """
    # Handle common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(value_str, fmt)
            if is_datetime:
                return dt
            else:
                return dt.date()
        except ValueError:
            continue
    
    # If no format matched, return as is
    return value_str


def convert_value_for_field(field, value):
    """Convert value to appropriate type based on field type.
    
    Args:
        field: The Django model field
        value: The value to convert
        
    Returns:
        The converted value, or None if conversion is not needed or fails
    """
    from django.db import models
    
    try:
        # Convert based on field type
        if isinstance(field, (models.IntegerField, models.BigIntegerField, models.SmallIntegerField, models.PositiveIntegerField, models.PositiveSmallIntegerField)):
            return int(value)
        elif isinstance(field, (models.FloatField, models.DecimalField)):
            return float(value)
        elif isinstance(field, models.DateTimeField):
            # Try to parse datetime
            return parse_date(value, is_datetime=True)
        elif isinstance(field, models.DateField):
            # Try to parse date
            return parse_date(value, is_datetime=False)
        else:
            return None
    except:
        # If conversion fails, return None to use original value
        return None