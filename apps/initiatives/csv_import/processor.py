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
                return
            
            # Create or skip initiative
            initiative, is_duplicate = self.initiative_handler.create_or_skip_initiative(
                name=row['Titulo'],
                description=row.get('', ''),  # Description field if exists
                start_date=start_date,
                end_date=end_date,
                coordinator=coordinator
            )
            
            if is_duplicate:
                self.reporter.add_skip(
                    row_number,
                    row['Titulo'],
                    f"Duplicate: same name and coordinator"
                )
                return
            
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
                unit = self.group_handler.get_organizational_unit(row['GrupoPesquisa'])
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
                    
                    # Create or get partnership organizational unit
                    partnership_unit = self.group_handler.get_or_create_external_research_group(
                        name=group_name,
                        knowledge_area=ka
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
            
            self.reporter.add_success(row_number, row['Titulo'])
            
        except ValidationError as e:
            # Don't re-raise - just log the error and continue
            error_msg = str(e)
            if hasattr(e, 'message_dict'):
                error_msg = '; '.join([f"{k}: {', '.join(v)}" for k, v in e.message_dict.items()])
            self.reporter.add_error(
                row_number,
                f"Validation error: {error_msg}",
                row
            )
            # Don't re-raise - transaction will rollback automatically
        
        except IntegrityError as e:
            self.reporter.add_error(
                row_number,
                f"Database integrity error: {str(e)}",
                row
            )
            # Don't re-raise - transaction will rollback automatically
        
        except Exception as e:
            self.reporter.add_error(
                row_number,
                f"Unexpected error: {str(e)}",
                row
            )
            # Don't re-raise - transaction will rollback automatically
