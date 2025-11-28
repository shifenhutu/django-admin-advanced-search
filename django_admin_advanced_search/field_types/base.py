"""Base field parser for advanced search."""


class BaseFieldParser:
    """Base class for field parsers."""
    
    @classmethod
    def supports(cls, field):
        """Check if this parser supports the given field."""
        raise NotImplementedError
    
    def parse(self, value_str, field_name, modifier=''):
        """Parse a value string for the field.
        
        Args:
            value_str: The string value to parse
            field_name: The name of the field
            modifier: The modifier operator (=, ==, !, >, <, etc.)
            
        Returns:
            dict: A dictionary of filter conditions, or None if parsing failed
        """
        raise NotImplementedError