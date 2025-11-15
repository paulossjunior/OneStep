"""
Import reporter for CSV import.
"""

from typing import List, Dict


class ImportReporter:
    """
    Tracks and reports import statistics and errors.
    """
    
    def __init__(self):
        self.total_rows = 0
        self.success_count = 0
        self.skip_count = 0
        self.error_count = 0
        self.successes = []
        self.skips = []
        self.errors = []
    
    def add_success(self, row_number: int, project_name: str, message: str = None):
        """
        Record successful import.
        
        Args:
            row_number: Row number in CSV
            project_name: Name of imported project
            message: Optional custom message (e.g., "Updated existing initiative")
        """
        self.success_count += 1
        success_entry = {
            'row': row_number,
            'project': project_name
        }
        if message:
            success_entry['message'] = message
        self.successes.append(success_entry)
    
    def add_skip(self, row_number: int, project_name: str, reason: str):
        """
        Record skipped row.
        
        Args:
            row_number: Row number in CSV
            project_name: Name of project that was skipped
            reason: Reason for skipping
        """
        self.skip_count += 1
        self.skips.append({
            'row': row_number,
            'project': project_name,
            'reason': reason
        })
    
    def add_error(self, row_number: int, error_message: str, row_data: Dict = None):
        """
        Record error.
        
        Args:
            row_number: Row number in CSV
            error_message: Error message
            row_data: Optional row data for debugging
        """
        self.error_count += 1
        error_entry = {
            'row': row_number,
            'message': error_message
        }
        if row_data:
            error_entry['data'] = row_data
        self.errors.append(error_entry)
    
    def set_total_rows(self, total: int):
        """
        Set total number of rows processed.
        
        Args:
            total: Total row count
        """
        self.total_rows = total
    
    def generate_summary(self) -> str:
        """
        Generate summary report.
        
        Returns:
            str: Formatted summary report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("CSV Import Summary")
        lines.append("=" * 60)
        lines.append(f"Total rows processed: {self.total_rows}")
        lines.append(f"Successful imports: {self.success_count}")
        lines.append(f"Skipped (duplicates): {self.skip_count}")
        lines.append(f"Errors: {self.error_count}")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    def get_errors(self) -> List[Dict]:
        """
        Get list of errors for detailed reporting.
        
        Returns:
            List of error dictionaries with row numbers and messages
        """
        return self.errors
    
    def get_skips(self) -> List[Dict]:
        """
        Get list of skipped rows.
        
        Returns:
            List of skip dictionaries
        """
        return self.skips
    
    def get_successes(self) -> List[Dict]:
        """
        Get list of successful imports.
        
        Returns:
            List of success dictionaries
        """
        return self.successes
    
    def has_errors(self) -> bool:
        """
        Check if any errors occurred.
        
        Returns:
            bool: True if errors occurred
        """
        return self.error_count > 0
