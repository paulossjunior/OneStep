"""
Import processor for CSV import.
"""

from typing import Dict
from django.db import transaction
from django.core.exceptions import ValidationError
from .parser import CSVParser
from .validator import DataValidator
from .campus_handler import CampusHandler
from .knowledge_area_handler import KnowledgeAreaHandler
from .person_handler import PersonHandler
from .group_handler import GroupHandler
from .reporter import ImportReporter


class ImportProcessor:
    """
    Orchestrates the CSV import process.
    """
    
    def __init__(self):
        self.parser = CSVParser()
        self.validator = DataValidator()
        self.campus_handler = CampusHandler()
        self.knowledge_area_handler = KnowledgeAreaHandler()
        self.person_handler = PersonHandler()
        self.group_handler = GroupHandler()
        self.reporter = ImportReporter()
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text to title case (first letter uppercase, rest lowercase).
        
        Args:
            text: Text to normalize
            
        Returns:
            str: Normalized text with proper capitalization
        """
        if not text:
            return text
        
        # Split by spaces and capitalize each word
        words = text.strip().split()
        normalized_words = [word.capitalize() for word in words]
        return ' '.join(normalized_words)
    
    def process_csv(self, file_path):
        """
        Process entire CSV file.
        
        Args:
            file_path: Path to CSV file or file-like object
            
        Returns:
            ImportReporter: Reporter with statistics and errors
        """
        row_number = 0
        
        try:
            for row in self.parser.parse_file(file_path):
                row_number += 1
                self.process_row(row, row_number)
        except Exception as e:
            self.reporter.add_error(
                row_number if row_number > 0 else 0,
                f"Fatal error reading CSV: {str(e)}"
            )
        
        self.reporter.set_total_rows(row_number)
        return self.reporter
    
    def process_row(self, row: Dict[str, str], row_number: int):
        """
        Process a single CSV row.
        
        Args:
            row: Dictionary of column values
            row_number: Row number for error reporting
        """
        # Validate row
        validation_result = self.validator.validate_row(row, row_number)
        if not validation_result.is_valid:
            for error in validation_result.errors:
                self.reporter.add_error(row_number, error, row)
            return
        
        # Process row with transaction
        try:
            with transaction.atomic():
                # Normalize text fields (first letter uppercase, rest lowercase)
                campus_name = self.normalize_text(row.get('Unidade', ''))
                knowledge_area_name = self.normalize_text(row.get('AreaConhecimento', ''))
                group_name = self.normalize_text(row.get('Nome', ''))
                
                # Get or create Campus
                campus = self.campus_handler.get_or_create_campus(campus_name)
                
                # Get or create KnowledgeArea
                knowledge_area = self.knowledge_area_handler.get_or_create_knowledge_area(
                    knowledge_area_name
                )
                
                # Parse and get or create leaders
                leaders_str = row.get('Lideres', '')
                leaders = []
                if leaders_str:
                    leader_tuples = self.person_handler.parse_leaders(leaders_str)
                    for name, email in leader_tuples:
                        try:
                            # Normalize person name
                            normalized_name = self.normalize_text(name)
                            person = self.person_handler.get_or_create_person(normalized_name, email)
                            leaders.append(person)
                        except ValidationError as e:
                            self.reporter.add_error(
                                row_number,
                                f"Invalid leader '{name} ({email})': {str(e)}",
                                row
                            )
                            return
                
                # Normalize repository URL (add https:// if missing)
                repository_url = row.get('repositorio', '')
                if repository_url:
                    repository_url = self.validator.normalize_url(repository_url)
                
                # Create or skip group
                group, created = self.group_handler.create_or_skip_group(
                    short_name=row.get('Sigla', ''),
                    name=group_name,
                    campus=campus,
                    knowledge_area=knowledge_area,
                    repository_url=repository_url,
                    site_url=row.get('Site', '')
                )
                
                if not created:
                    self.reporter.add_skip(
                        row_number,
                        group.name,
                        f"Group with short_name '{group.short_name}' already exists on campus '{campus.name}'"
                    )
                    return
                
                # Assign leaders
                if leaders:
                    self.group_handler.assign_leaders(group, leaders)
                
                # Record success
                self.reporter.add_success(row_number, group.name)
                
        except ValidationError as e:
            self.reporter.add_error(
                row_number,
                f"Validation error: {str(e)}",
                row
            )
        except Exception as e:
            self.reporter.add_error(
                row_number,
                f"Unexpected error: {str(e)}",
                row
            )
