"""
CSV Parser for research project data.
"""

import csv
from typing import Iterator, Dict


class CSVParser:
    """
    Parses CSV files containing research project data.
    """
    
    def parse_file(self, file_path) -> Iterator[Dict[str, str]]:
        """
        Parse CSV file and yield rows as dictionaries.
        
        Args:
            file_path: Path to CSV file or file-like object
            
        Yields:
            Dictionary mapping column names to values
            
        Raises:
            Exception: If file cannot be parsed
        """
        # Handle both file paths and file-like objects
        if isinstance(file_path, str):
            file_handle = open(file_path, 'r', encoding='utf-8-sig')
            should_close = True
        else:
            # File-like object (e.g., from admin upload)
            file_handle = file_path
            should_close = False
            # Decode if needed
            if hasattr(file_handle, 'read') and isinstance(file_handle.read(0), bytes):
                import io
                content = file_handle.read().decode('utf-8-sig')
                file_handle = io.StringIO(content)
        
        try:
            reader = csv.DictReader(file_handle)
            
            for row in reader:
                # Strip whitespace from all values
                cleaned_row = {}
                for key, value in row.items():
                    # Clean key
                    clean_key = key.strip() if key else key
                    # Clean value - handle None and ensure it's a string
                    if value is None:
                        clean_value = ''
                    elif isinstance(value, str):
                        clean_value = value.strip()
                    else:
                        clean_value = str(value).strip()
                    cleaned_row[clean_key] = clean_value
                yield cleaned_row
        finally:
            if should_close:
                file_handle.close()
