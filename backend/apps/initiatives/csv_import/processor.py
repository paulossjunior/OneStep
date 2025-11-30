"""
Processor for research project CSV import.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .parser import CSVParser
from .validator import ResearchProjectValidator
from .person_handler import PersonHandler
from .initiative_handler import InitiativeHandler
from .group_handler import GroupHandler
from .reporter import ImportReporter
from apps.initiatives.models import FailedInitiativeImport


class ResearchProjectImportProcessor:
    """
    Orchestrates the research project CSV import process.
    """
    
    def __init__(self):
        self.parser = CSVParser()
        self.validator = ResearchProjectValidator()
        self.person_handler = PersonHandler()
        self.initiative_handler = InitiativeHandler()
        self.group_handler = GroupHandler()
        self.reporter = ImportReporter()
    
    def save_failed_import(self, row_number: int, error_reason: str, row_data: dict):
        """
        Save a failed import to the database.
        
        Args:
            row_number: Row number in CSV
            error_reason: Reason for failure
            row_data: Raw CSV row data
        """
        try:
            FailedInitiativeImport.objects.create(
                row_number=row_number,
                error_reason=error_reason,
                raw_data=row_data
            )
        except Exception as e:
            # If we can't save the failed import, just log it
            print(f"Failed to save failed import record: {str(e)}")
    
    def process_csv(self, file_path) -> ImportReporter:
        """
        Process CSV file and import research projects.
        
        Args:
            file_path: Path to CSV file or file-like object
            
        Returns:
            ImportReporter: Reporter with import statistics
        """
        row_number = 0
        
        try:
            for row in self.parser.parse_file(file_path):
                row_number += 1
                self.process_row(row, row_number)
        except Exception as e:
            self.reporter.add_error(
                row_number if row_number > 0 else 0,
                f"Fatal error processing CSV: {str(e)}"
            )
        
        self.reporter.set_total_rows(row_number)
        return self.reporter
    
    @transaction.atomic
    def process_row(self, row: dict, row_number: int):
        """
        Process a single CSV row within a transaction.
        
        Args:
            row: Dictionary containing row data
            row_number: Row number in CSV
        """
        try:
            # Validate row
            validation_result = self.validator.validate_row(row)
            if not validation_result.is_valid:
                error_msg = "; ".join(validation_result.errors)
                self.reporter.add_error(row_number, error_msg, row)
                self.save_failed_import(row_number, error_msg, row)
                return
            
            # Parse dates
            start_date = self.validator.parse_date(row['Inicio'])
            end_date = self.validator.parse_date(row['Fim'])
            
            # Create or get coordinator
            try:
                coordinator = self.person_handler.get_or_create_person(
                    name=row['Coordenador'],
                    email=row['EmailCoordenador']
                )
            except ValidationError as ve:
                error_msg = f"Invalid coordinator email '{row['EmailCoordenador']}': {str(ve)}"
                self.reporter.add_error(row_number, error_msg, row)
                self.save_failed_import(row_number, error_msg, row)
                return
            
            # Get or create campus from CampusExecucao
            campus = None
            if row.get('CampusExecucao'):
                campus = self.group_handler.get_or_create_campus(row['CampusExecucao'])
            
            # Create or get existing initiative
            initiative, is_existing, coordinator_changed = self.initiative_handler.create_or_get_initiative(
                name=row['Titulo'],
                description=row.get('', ''),  # Description field if exists
                start_date=start_date,
                end_date=end_date,
                coordinator=coordinator,
                campus=campus
            )
            
            # Track if this is an update to existing initiative
            if is_existing:
                # Will add team members and students to existing initiative
                # Coordinator may have been changed as well
                pass
            
            # Process team members (Pesquisadores)
            if row.get('Pesquisadores'):
                team_member_names = self.person_handler.parse_people_list(row['Pesquisadores'])
                for name in team_member_names:
                    person = self.person_handler.get_or_create_person(name=name)
                    initiative.team_members.add(person)
            
            # Process students (Estudantes)
            if row.get('Estudantes'):
                student_names = self.person_handler.parse_people_list(row['Estudantes'])
                for name in student_names:
                    person = self.person_handler.get_or_create_person(name=name)
                    initiative.students.add(person)
            
            # Process knowledge area (AreaConhecimento)
            if row.get('AreaConhecimento'):
                knowledge_area = self.group_handler.get_or_create_knowledge_area(row['AreaConhecimento'])
                if knowledge_area:
                    initiative.knowledge_areas.add(knowledge_area)
            
            # Process organizational unit (GrupoPesquisa)
            if row.get('GrupoPesquisa'):
                # First try to find existing unit
                unit = self.group_handler.get_organizational_unit(row['GrupoPesquisa'])
                
                # If not found, create it using CampusExecucao
                if not unit:
                    campus_name = row.get('CampusExecucao', '').strip()
                    ka = knowledge_area if row.get('AreaConhecimento') else None
                    unit = self.group_handler.get_or_create_external_research_group(
                        name=row['GrupoPesquisa'],
                        knowledge_area=ka,
                        campus_name=campus_name
                    )
                
                if unit:
                    # Add initiative to unit's initiatives
                    unit.initiatives.add(initiative)
                    # Sync knowledge areas from initiatives to unit
                    unit.sync_knowledge_areas_from_initiatives()
            
            # Process partnerships (GrupoPesquisaExterno)
            if row.get('GrupoPesquisaExterno'):
                # Parse multiple partnership groups (comma-separated)
                partnership_groups = [g.strip() for g in row['GrupoPesquisaExterno'].split(',') if g.strip()]
                
                for group_name in partnership_groups:
                    # Get knowledge area for the partnership (use initiative's knowledge area if available)
                    ka = knowledge_area if row.get('AreaConhecimento') else None
                    
                    # Get campus from CampusExecucao
                    campus_name = row.get('CampusExecucao', '').strip()
                    
                    # Create or get partnership organizational unit
                    # Uses CampusExecucao as campus and creates without leadership
                    partnership_unit = self.group_handler.get_or_create_external_research_group(
                        name=group_name,
                        knowledge_area=ka,
                        campus_name=campus_name
                    )
                    
                    if partnership_unit:
                        # Add organizational unit as a partnership
                        initiative.add_partnership(partnership_unit)
            
            # Process demanding partner (ParceiroDemandante)
            if row.get('ParceiroDemandante'):
                # Create or get demanding partner organization
                demanding_partner = self.group_handler.get_or_create_demanding_partner_organization(
                    name=row['ParceiroDemandante']
                )
                
                if demanding_partner:
                    # Set the demanding partner for this initiative
                    initiative.demanding_partner = demanding_partner
                    initiative.save()
            
            # Report success with appropriate message
            if is_existing:
                if coordinator_changed:
                    self.reporter.add_success(
                        row_number, 
                        row['Titulo'],
                        message="Updated existing initiative: coordinator changed and team members/students added"
                    )
                else:
                    self.reporter.add_success(
                        row_number, 
                        row['Titulo'],
                        message="Updated existing initiative with new team members/students"
                    )
            else:
                self.reporter.add_success(row_number, row['Titulo'])
            
        except ValidationError as e:
            # Don't re-raise - just log the error and continue
            error_msg = str(e)
            if hasattr(e, 'message_dict'):
                error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
            full_error = f"Validation error: {error_msg}"
            self.reporter.add_error(row_number, full_error, row)
            self.save_failed_import(row_number, full_error, row)
            # Don't re-raise - transaction will rollback automatically
        
        except IntegrityError as e:
            error_msg = f"Database integrity error: {str(e)}"
            self.reporter.add_error(row_number, error_msg, row)
            self.save_failed_import(row_number, error_msg, row)
            # Don't re-raise - transaction will rollback automatically
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.reporter.add_error(row_number, error_msg, row)
            self.save_failed_import(row_number, error_msg, row)
            # Don't re-raise - transaction will rollback automatically
