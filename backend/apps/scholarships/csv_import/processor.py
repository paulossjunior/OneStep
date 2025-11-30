"""
Main processor for scholarship CSV import.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from .parser import CSVParser
from .validator import ScholarshipValidator
from .reporter import ImportReporter
from .handlers import (
    ScholarshipTypeHandler,
    PersonHandler,
    CampusHandler,
    OrganizationHandler,
    InitiativeHandler
)
from apps.scholarships.models import Scholarship, FailedScholarshipImport


class ScholarshipImportProcessor:
    """
    Orchestrates the scholarship CSV import process.
    """
    
    def __init__(self):
        self.parser = CSVParser()
        self.validator = ScholarshipValidator()
        self.reporter = ImportReporter()
        self.type_handler = ScholarshipTypeHandler()
        self.person_handler = PersonHandler()
        self.campus_handler = CampusHandler()
        self.organization_handler = OrganizationHandler()
        self.initiative_handler = InitiativeHandler()
    
    def save_failed_import(self, row_number: int, error_reason: str, row_data: dict):
        """
        Save a failed import to the database.
        
        Args:
            row_number: Row number in CSV
            error_reason: Reason for failure
            row_data: Raw CSV row data
        """
        try:
            FailedScholarshipImport.objects.create(
                row_number=row_number,
                error_reason=error_reason,
                raw_data=row_data
            )
        except Exception as e:
            # If we can't save the failed import, just log it
            print(f"Failed to save failed import record: {str(e)}")
    
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
    
    def process_row(self, row: dict, row_number: int):
        """
        Process a single CSV row.
        
        Args:
            row: Dictionary of column values
            row_number: Row number for error reporting
        """
        # Validate row
        validation_result = self.validator.validate_row(row)
        if not validation_result.is_valid:
            error_msg = "; ".join(validation_result.errors)
            self.reporter.add_error(row_number, error_msg, row)
            self.save_failed_import(row_number, error_msg, row)
            return
        
        # Process row with transaction
        try:
            with transaction.atomic():
                # Parse dates
                start_date = self.validator.parse_date(row['Inicio'])
                end_date = self.validator.parse_date(row.get('Fim', ''))
                
                # Parse value
                value = self.validator.parse_value(row['Valor'])
                
                # Get or create scholarship type (defaults to "Not Informed" if blank)
                programa = row.get('Programa', '').strip()
                scholarship_type = self.type_handler.get_or_create_type(programa)
                
                # Get or create campus
                campus = self.campus_handler.get_or_create_campus(row['CampusExecucao'])
                if not campus:
                    error_msg = f"Could not create campus: {row['CampusExecucao']}"
                    self.reporter.add_error(row_number, error_msg, row)
                    self.save_failed_import(row_number, error_msg, row)
                    return
                
                # Get or create supervisor
                supervisor = None
                if row.get('Orientador') and row.get('OrientadorEmail'):
                    supervisor = self.person_handler.get_or_create_person(
                        row['Orientador'],
                        row['OrientadorEmail']
                    )
                
                # Get or create student
                student = None
                if row.get('Orientado') and row.get('OrientadoEmail'):
                    student = self.person_handler.get_or_create_person(
                        row['Orientado'],
                        row['OrientadoEmail']
                    )
                
                if not student:
                    error_msg = "Could not create student (Orientado)"
                    self.reporter.add_error(row_number, error_msg, row)
                    self.save_failed_import(row_number, error_msg, row)
                    return
                
                # Get or create sponsor (defaults to "Not Informed" if blank)
                ag_financiadora = row.get('AgFinanciadora', '').strip()
                sponsor = self.organization_handler.get_or_create_organization(ag_financiadora)
                
                # Get initiative
                initiative = None
                if row.get('TituloPJ'):
                    initiative = self.initiative_handler.get_initiative_by_name(row['TituloPJ'])
                
                # Generate title
                title = row.get('TituloPT', '').strip()
                if not title:
                    # Generate title from available data
                    title = f"Scholarship - {student.name if student else 'Unknown'}"
                
                # Check for duplicate
                existing = Scholarship.objects.filter(
                    student=student,
                    start_date=start_date,
                    supervisor=supervisor
                ).first()
                
                if existing:
                    self.reporter.add_skip(
                        row_number,
                        title,
                        f"Duplicate: same student, start date, and supervisor"
                    )
                    return
                
                # Create scholarship
                scholarship = Scholarship(
                    title=title,
                    type=scholarship_type,
                    campus=campus,
                    start_date=start_date,
                    end_date=end_date,
                    supervisor=supervisor,
                    student=student,
                    value=value,
                    sponsor=sponsor,
                    initiative=initiative
                )
                
                # Validate and save
                scholarship.full_clean()
                scholarship.save()
                
                # Record success
                self.reporter.add_success(row_number, title)
                
        except ValidationError as e:
            error_msg = "; ".join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
            full_error = f"Validation error: {error_msg}"
            self.reporter.add_error(row_number, full_error, row)
            self.save_failed_import(row_number, full_error, row)
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.reporter.add_error(row_number, error_msg, row)
            self.save_failed_import(row_number, error_msg, row)
