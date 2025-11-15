"""
Bulk CSV import handler for processing multiple CSV files.
"""

import os
import zipfile
from typing import List, Dict, Any
from django.core.files.uploadedfile import UploadedFile
from pathlib import Path


class BulkImportHandler:
    """
    Handles bulk CSV imports from multiple files or ZIP archives.
    """
    
    SUPPORTED_EXTENSIONS = ['.csv']
    SUPPORTED_ARCHIVE_EXTENSIONS = ['.zip']
    
    def __init__(self):
        self.files = []
        self.errors = []
    
    def process_upload(self, uploaded_file: UploadedFile) -> List[Dict[str, Any]]:
        """
        Process uploaded file(s) - can be a single CSV or ZIP containing multiple CSVs.
        
        Args:
            uploaded_file: Uploaded file from Django form
            
        Returns:
            List of dictionaries with file info: {'name': str, 'content': file-like object}
        """
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        if file_extension in self.SUPPORTED_ARCHIVE_EXTENSIONS:
            return self._process_zip_file(uploaded_file)
        elif file_extension in self.SUPPORTED_EXTENSIONS:
            return self._process_single_csv(uploaded_file)
        else:
            self.errors.append(f"Unsupported file type: {file_extension}")
            return []
    
    def _process_single_csv(self, uploaded_file: UploadedFile) -> List[Dict[str, Any]]:
        """
        Process a single CSV file.
        
        Args:
            uploaded_file: Uploaded CSV file
            
        Returns:
            List with single file info dictionary
        """
        return [{
            'name': uploaded_file.name,
            'content': uploaded_file,
            'size': uploaded_file.size
        }]
    
    def _process_zip_file(self, uploaded_file: UploadedFile) -> List[Dict[str, Any]]:
        """
        Extract and process CSV files from ZIP archive.
        
        Args:
            uploaded_file: Uploaded ZIP file
            
        Returns:
            List of file info dictionaries for each CSV in the archive
        """
        csv_files = []
        
        try:
            with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
                # Get list of CSV files in the archive
                csv_file_names = [
                    name for name in zip_ref.namelist()
                    if name.lower().endswith('.csv') and not name.startswith('__MACOSX')
                ]
                
                if not csv_file_names:
                    self.errors.append("No CSV files found in ZIP archive")
                    return []
                
                # Extract each CSV file
                for csv_name in csv_file_names:
                    try:
                        csv_content = zip_ref.read(csv_name)
                        
                        # Create a file-like object from the content
                        from io import BytesIO
                        csv_file = BytesIO(csv_content)
                        csv_file.name = csv_name
                        
                        csv_files.append({
                            'name': csv_name,
                            'content': csv_file,
                            'size': len(csv_content)
                        })
                    except Exception as e:
                        self.errors.append(f"Error extracting {csv_name}: {str(e)}")
                
        except zipfile.BadZipFile:
            self.errors.append("Invalid ZIP file")
        except Exception as e:
            self.errors.append(f"Error processing ZIP file: {str(e)}")
        
        return csv_files
    
    def get_errors(self) -> List[str]:
        """
        Get list of errors encountered during processing.
        
        Returns:
            List of error messages
        """
        return self.errors
    
    def has_errors(self) -> bool:
        """
        Check if any errors occurred.
        
        Returns:
            bool: True if errors occurred
        """
        return len(self.errors) > 0


class BulkImportReporter:
    """
    Aggregates import results from multiple CSV files.
    """
    
    def __init__(self):
        self.file_results = []
        self.total_files = 0
        self.successful_files = 0
        self.failed_files = 0
        self.total_rows = 0
        self.total_successes = 0
        self.total_errors = 0
        self.total_skips = 0
    
    def add_file_result(self, filename: str, reporter: Any):
        """
        Add results from a single file import.
        
        Args:
            filename: Name of the CSV file
            reporter: ImportReporter instance with results
        """
        self.total_files += 1
        self.total_rows += reporter.total_rows
        self.total_successes += reporter.success_count
        self.total_errors += reporter.error_count
        self.total_skips += reporter.skip_count
        
        if reporter.error_count == 0:
            self.successful_files += 1
        else:
            self.failed_files += 1
        
        self.file_results.append({
            'filename': filename,
            'total_rows': reporter.total_rows,
            'successes': reporter.success_count,
            'errors': reporter.error_count,
            'skips': reporter.skip_count,
            'reporter': reporter
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of all imports.
        
        Returns:
            Dictionary with summary statistics
        """
        return {
            'total_files': self.total_files,
            'successful_files': self.successful_files,
            'failed_files': self.failed_files,
            'total_rows': self.total_rows,
            'total_successes': self.total_successes,
            'total_errors': self.total_errors,
            'total_skips': self.total_skips,
            'file_results': self.file_results
        }
    
    def generate_summary_text(self) -> str:
        """
        Generate human-readable summary text.
        
        Returns:
            str: Formatted summary
        """
        lines = []
        lines.append("=" * 70)
        lines.append("BULK CSV IMPORT SUMMARY")
        lines.append("=" * 70)
        lines.append(f"Files processed: {self.total_files}")
        lines.append(f"  - Successful: {self.successful_files}")
        lines.append(f"  - With errors: {self.failed_files}")
        lines.append("")
        lines.append(f"Total rows processed: {self.total_rows}")
        lines.append(f"  - Successful imports: {self.total_successes}")
        lines.append(f"  - Skipped (duplicates): {self.total_skips}")
        lines.append(f"  - Errors: {self.total_errors}")
        lines.append("=" * 70)
        
        if self.file_results:
            lines.append("")
            lines.append("PER-FILE RESULTS:")
            lines.append("-" * 70)
            for result in self.file_results:
                lines.append(f"\n{result['filename']}:")
                lines.append(f"  Rows: {result['total_rows']}")
                lines.append(f"  Success: {result['successes']}")
                lines.append(f"  Errors: {result['errors']}")
                lines.append(f"  Skipped: {result['skips']}")
        
        return "\n".join(lines)
