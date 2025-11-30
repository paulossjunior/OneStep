"""
Import reporter for tracking statistics and errors.
"""

from typing import List, Dict


class ImportReporter:
    """
    Tracks import statistics and errors.
    """
    
    def __init__(self):
        self.total_rows = 0
        self.success_count = 0
        self.skip_count = 0
        self.error_count = 0
        self._errors = []
        self._skips = []
        self._successes = []
    
    def set_total_rows(self, count: int):
        """Set total number of rows processed."""
        self.total_rows = count
    
    def add_success(self, row_number: int, title: str):
        """Record successful import."""
        self.success_count += 1
        self._successes.append({
            'row': row_number,
            'title': title
        })
    
    def add_skip(self, row_number: int, title: str, reason: str):
        """Record skipped row."""
        self.skip_count += 1
        self._skips.append({
            'row': row_number,
            'title': title,
            'reason': reason
        })
    
    def add_error(self, row_number: int, message: str, row_data: dict = None):
        """Record error."""
        self.error_count += 1
        self._errors.append({
            'row': row_number,
            'message': message,
            'data': row_data
        })
    
    def get_errors(self) -> List[Dict]:
        """Get list of errors."""
        return self._errors
    
    def get_skips(self) -> List[Dict]:
        """Get list of skipped rows."""
        return self._skips
    
    def get_successes(self) -> List[Dict]:
        """Get list of successful imports."""
        return self._successes
    
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return self.error_count > 0
    
    def generate_summary(self) -> str:
        """Generate summary report."""
        lines = []
        lines.append("=" * 60)
        lines.append("SCHOLARSHIP IMPORT SUMMARY")
        lines.append("=" * 60)
        lines.append(f"Total rows processed: {self.total_rows}")
        lines.append(f"Successfully imported: {self.success_count}")
        lines.append(f"Skipped (duplicates): {self.skip_count}")
        lines.append(f"Errors: {self.error_count}")
        lines.append("=" * 60)
        return "\n".join(lines)
