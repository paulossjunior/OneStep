from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimestampedModel
import json


class InitiativeType(TimestampedModel):
    """
    Model representing different types of initiatives.
    
    Attributes:
        name (CharField): Type name (Program, Project, Event)
        code (CharField): Type code (program, project, event)
        description (TextField): Type description
        is_active (BooleanField): Whether this type is active
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Display name for the initiative type"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique code for the initiative type"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of this initiative type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this initiative type is active and can be used"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Initiative Type'
        verbose_name_plural = 'Initiative Types'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """
        String representation of the InitiativeType.
        
        Returns:
            str: Name of the initiative type
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the InitiativeType model.
        """
        super().clean()
        
        # Validate that name and code are not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Initiative type name cannot be empty.'})
        
        if not self.code or not self.code.strip():
            raise ValidationError({'code': 'Initiative type code cannot be empty.'})
        
        # Clean up whitespace and normalize code
        if self.name:
            self.name = self.name.strip()
        
        if self.code:
            self.code = self.code.strip().lower()
    
    @classmethod
    def get_default_types(cls):
        """
        Get or create the default initiative types.
        
        Returns:
            tuple: (program_type, project_type, event_type)
        """
        program_type, _ = cls.objects.get_or_create(
            code='program',
            defaults={
                'name': 'Program',
                'description': 'High-level strategic initiatives with long-term goals'
            }
        )
        
        project_type, _ = cls.objects.get_or_create(
            code='project',
            defaults={
                'name': 'Project',
                'description': 'Specific deliverable-focused work with defined scope'
            }
        )
        
        event_type, _ = cls.objects.get_or_create(
            code='event',
            defaults={
                'name': 'Event',
                'description': 'Time-bound activities and gatherings'
            }
        )
        
        return program_type, project_type, event_type


class Initiative(TimestampedModel):
    """
    Initiative model representing programs, projects, or events with hierarchical relationships.
    
    Attributes:
        name (CharField): Initiative name
        description (TextField): Initiative description
        type (CharField): Initiative type (program, project, event)
        start_date (DateField): Initiative start date
        end_date (DateField): Initiative end date (optional)
        parent (ForeignKey): Parent initiative for hierarchical structure
        coordinator (ForeignKey): Person who coordinates this initiative
        campus (ForeignKey): Campus where this initiative is performed
        team_members (ManyToManyField): People who are team members
        students (ManyToManyField): Students participating in this initiative
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Initiative name"
    )
    description = models.TextField(
        blank=True,
        help_text="Initiative description"
    )
    type = models.ForeignKey(
        InitiativeType,
        on_delete=models.PROTECT,
        help_text="Initiative type (Program, Project, Event)"
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Initiative start date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Initiative end date (optional)"
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="Parent initiative for hierarchical structure"
    )
    coordinator = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='coordinated_initiatives',
        help_text="Person who coordinates this initiative"
    )
    campus = models.ForeignKey(
        'organizational_group.Campus',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='initiatives',
        help_text="Campus where this initiative is performed"
    )
    team_members = models.ManyToManyField(
        'people.Person',
        blank=True,
        related_name='team_initiatives',
        help_text="People who are team members of this initiative"
    )
    students = models.ManyToManyField(
        'people.Person',
        blank=True,
        related_name='student_initiatives',
        help_text="Students participating in this initiative"
    )
    knowledge_areas = models.ManyToManyField(
        'organizational_group.KnowledgeArea',
        blank=True,
        related_name='initiatives',
        help_text="Knowledge areas associated with this initiative"
    )
    demanding_partner = models.ForeignKey(
        'organizational_group.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='demanded_initiatives',
        help_text="Organization that demands/requests this initiative"
    )
    partnerships = models.ManyToManyField(
        'organizational_group.OrganizationalUnit',
        blank=True,
        related_name='partnership_initiatives',
        help_text="Organizational units that are partners in this initiative"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Initiative'
        verbose_name_plural = 'Initiatives'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type']),
            models.Index(fields=['start_date']),
            models.Index(fields=['coordinator']),
            models.Index(fields=['parent']),
            models.Index(fields=['campus']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')),
                name='end_date_after_start_date'
            )
        ]
    
    def __str__(self):
        """
        String representation of the Initiative.
        
        Returns:
            str: Name of the initiative
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the Initiative model.
        """
        super().clean()
        
        # Validate that name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Initiative name cannot be empty.'})
        
        # Clean up whitespace
        if self.name:
            self.name = self.name.strip()
        
        # Validate date logic only if both dates are present
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        elif self.end_date and not self.start_date:
            # Allow end_date without start_date, but it's unusual
            pass
        
        # Prevent circular parent relationships
        if self.parent and self.pk:
            if self.parent.pk == self.pk:
                raise ValidationError({
                    'parent': 'An initiative cannot be its own parent.'
                })
            
            # Check for circular reference in the hierarchy
            current_parent = self.parent
            while current_parent:
                if current_parent.pk == self.pk:
                    raise ValidationError({
                        'parent': 'Circular parent relationship detected.'
                    })
                current_parent = current_parent.parent
    
    @property
    def team_count(self):
        """
        Get the count of team members for this initiative.
        
        Returns:
            int: Number of team members
        """
        return self.team_members.count()
    
    @property
    def student_count(self):
        """
        Get the count of students for this initiative.
        
        Returns:
            int: Number of students
        """
        return self.students.count()
    
    @property
    def children_count(self):
        """
        Get the count of child initiatives.
        
        Returns:
            int: Number of child initiatives
        """
        return self.children.count()
    
    @property
    def coordinator_name(self):
        """
        Get the coordinator's name.
        
        Returns:
            str: Coordinator's full name
        """
        return self.coordinator.full_name if self.coordinator else ''
    
    def get_all_children(self):
        """
        Get all descendant initiatives recursively.
        
        Returns:
            QuerySet: All descendant initiatives
        """
        children = list(self.children.all())
        all_children = children[:]
        
        for child in children:
            all_children.extend(child.get_all_children())
        
        return all_children
    
    def get_hierarchy_level(self):
        """
        Get the level of this initiative in the hierarchy (0 = root).
        
        Returns:
            int: Hierarchy level
        """
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    @property
    def external_research_groups(self):
        """
        Get organizational units (external research groups) associated with this initiative.
        
        Returns:
            QuerySet: OrganizationalUnits associated with this initiative
        """
        return self.units.all()
    
    @property
    def external_research_groups_count(self):
        """
        Get the count of external research groups for this initiative.
        
        Returns:
            int: Number of organizational units associated with this initiative
        """
        return self.units.count()
    
    def get_external_research_groups_by_type(self, type_code):
        """
        Get external research groups filtered by organizational type.
        
        Args:
            type_code (str): Type code (e.g., 'research', 'extension')
            
        Returns:
            QuerySet: Filtered organizational units
        """
        return self.units.filter(type__code=type_code)
    
    def get_external_research_groups_by_campus(self, campus):
        """
        Get external research groups filtered by campus.
        
        Args:
            campus: Campus instance or campus name
            
        Returns:
            QuerySet: Filtered organizational units
        """
        if isinstance(campus, str):
            return self.units.filter(campus__name__iexact=campus)
        return self.units.filter(campus=campus)
    
    def add_external_research_group(self, organizational_unit):
        """
        Add an organizational unit as an external research group.
        
        Args:
            organizational_unit: OrganizationalUnit instance to add
        """
        self.units.add(organizational_unit)
    
    def remove_external_research_group(self, organizational_unit):
        """
        Remove an organizational unit from external research groups.
        
        Args:
            organizational_unit: OrganizationalUnit instance to remove
        """
        self.units.remove(organizational_unit)
    
    @property
    def partnerships_count(self):
        """
        Get the count of partnership organizational units for this initiative.
        
        Returns:
            int: Number of partnership organizational units
        """
        return self.partnerships.count()
    
    def get_partnerships_by_type(self, type_code):
        """
        Get partnership organizational units filtered by type.
        
        Args:
            type_code (str): Type code (e.g., 'research', 'extension')
            
        Returns:
            QuerySet: Filtered partnership organizational units
        """
        return self.partnerships.filter(type__code=type_code)
    
    def get_partnerships_by_campus(self, campus):
        """
        Get partnership organizational units filtered by campus.
        
        Args:
            campus: Campus instance or campus name
            
        Returns:
            QuerySet: Filtered partnership organizational units
        """
        if isinstance(campus, str):
            return self.partnerships.filter(campus__name__iexact=campus)
        return self.partnerships.filter(campus=campus)
    
    def add_partnership(self, organizational_unit):
        """
        Add an organizational unit as a partnership.
        
        Args:
            organizational_unit: OrganizationalUnit instance to add
        """
        self.partnerships.add(organizational_unit)
    
    def remove_partnership(self, organizational_unit):
        """
        Remove an organizational unit from partnerships.
        
        Args:
            organizational_unit: OrganizationalUnit instance to remove
        """
        self.partnerships.remove(organizational_unit)


class FailedInitiativeImport(TimestampedModel):
    """
    Model to store failed research project imports from CSV.
    
    Attributes:
        row_number (IntegerField): Row number in the CSV file
        error_reason (TextField): Reason why the import failed
        raw_data (JSONField): Raw CSV row data
        import_date (DateTimeField): When the import was attempted
        resolved (BooleanField): Whether the issue has been resolved
        resolution_notes (TextField): Notes about how the issue was resolved
    """
    
    row_number = models.IntegerField(
        help_text="Row number in the CSV file"
    )
    error_reason = models.TextField(
        help_text="Reason why the import failed"
    )
    raw_data = models.JSONField(
        help_text="Raw CSV row data as JSON"
    )
    import_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the import was attempted"
    )
    resolved = models.BooleanField(
        default=False,
        help_text="Whether the issue has been resolved"
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text="Notes about how the issue was resolved"
    )
    
    class Meta:
        ordering = ['-import_date', 'row_number']
        verbose_name = 'Failed Initiative Import'
        verbose_name_plural = 'Failed Initiative Imports'
        indexes = [
            models.Index(fields=['import_date']),
            models.Index(fields=['resolved']),
            models.Index(fields=['row_number']),
        ]
    
    def __str__(self):
        """
        String representation of the FailedInitiativeImport.
        
        Returns:
            str: Description of the failed import
        """
        title = self.raw_data.get('Titulo', 'Unknown')
        return f"Row {self.row_number}: {title} - {self.error_reason[:50]}"
    
    def get_title(self):
        """
        Get the title from raw data.
        
        Returns:
            str: Initiative title or 'Unknown'
        """
        return self.raw_data.get('Titulo', 'Unknown')
    
    def get_coordinator(self):
        """
        Get the coordinator name from raw data.
        
        Returns:
            str: Coordinator name or 'Unknown'
        """
        return self.raw_data.get('Coordenador', 'Unknown')
    
    def get_coordinator_email(self):
        """
        Get the coordinator email from raw data.
        
        Returns:
            str: Coordinator email or 'Unknown'
        """
        return self.raw_data.get('EmailCoordenador', 'Unknown')
    
    def get_start_date(self):
        """
        Get the start date from raw data.
        
        Returns:
            str: Start date or 'Unknown'
        """
        return self.raw_data.get('Inicio', 'Unknown')
    
    def get_end_date(self):
        """
        Get the end date from raw data.
        
        Returns:
            str: End date or 'Unknown'
        """
        return self.raw_data.get('Fim', 'Unknown')
    
    def get_campus(self):
        """
        Get the campus from raw data.
        
        Returns:
            str: Campus name or 'Unknown'
        """
        return self.raw_data.get('CampusExecucao', 'Unknown')
    
    def mark_resolved(self, notes=''):
        """
        Mark this failed import as resolved.
        
        Args:
            notes (str): Resolution notes
        """
        self.resolved = True
        self.resolution_notes = notes
        self.save()
    
    def get_formatted_data(self):
        """
        Get formatted raw data for display.
        
        Returns:
            str: Formatted JSON string
        """
        return json.dumps(self.raw_data, indent=2, ensure_ascii=False)



class InitiativeCoordinatorChange(TimestampedModel):
    """
    Model to track coordinator changes for initiatives.
    
    Attributes:
        initiative (ForeignKey): The initiative that had a coordinator change
        previous_coordinator (ForeignKey): The previous coordinator
        new_coordinator (ForeignKey): The new coordinator
        change_date (DateTimeField): When the change occurred
        change_reason (TextField): Reason for the change (e.g., "CSV import update")
        changed_by (CharField): Who/what made the change
    """
    
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='coordinator_changes',
        help_text="Initiative that had a coordinator change"
    )
    previous_coordinator = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='previous_coordinated_initiatives',
        help_text="Previous coordinator"
    )
    new_coordinator = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='new_coordinated_initiatives',
        help_text="New coordinator"
    )
    change_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the change occurred"
    )
    change_reason = models.TextField(
        help_text="Reason for the change"
    )
    changed_by = models.CharField(
        max_length=200,
        default='CSV Import',
        help_text="Who or what made the change"
    )
    
    class Meta:
        ordering = ['-change_date']
        verbose_name = 'Initiative Coordinator Change'
        verbose_name_plural = 'Initiative Coordinator Changes'
        indexes = [
            models.Index(fields=['initiative']),
            models.Index(fields=['change_date']),
            models.Index(fields=['previous_coordinator']),
            models.Index(fields=['new_coordinator']),
        ]
    
    def __str__(self):
        """
        String representation of the InitiativeCoordinatorChange.
        
        Returns:
            str: Description of the coordinator change
        """
        return f"{self.initiative.name}: {self.previous_coordinator.full_name} → {self.new_coordinator.full_name}"
    
    def get_previous_coordinator_name(self):
        """
        Get the previous coordinator's name.
        
        Returns:
            str: Previous coordinator's full name
        """
        return self.previous_coordinator.full_name if self.previous_coordinator else 'Unknown'
    
    def get_new_coordinator_name(self):
        """
        Get the new coordinator's name.
        
        Returns:
            str: New coordinator's full name
        """
        return self.new_coordinator.full_name if self.new_coordinator else 'Unknown'



class InitiativeCoordinatorChange(TimestampedModel):
    """
    Model to track coordinator changes for initiatives.
    
    Attributes:
        initiative (ForeignKey): The initiative whose coordinator changed
        previous_coordinator (ForeignKey): The previous coordinator
        new_coordinator (ForeignKey): The new coordinator
        change_date (DateTimeField): When the change occurred
        change_reason (TextField): Reason for the change
        changed_by (CharField): Who made the change (user or system)
    """
    
    initiative = models.ForeignKey(
        Initiative,
        on_delete=models.CASCADE,
        related_name='coordinator_changes',
        help_text="The initiative whose coordinator changed"
    )
    previous_coordinator = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='previous_coordinated_initiatives',
        help_text="The previous coordinator"
    )
    new_coordinator = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='newly_coordinated_initiatives',
        help_text="The new coordinator"
    )
    change_date = models.DateTimeField(
        auto_now_add=True,
        help_text="When the change occurred"
    )
    change_reason = models.TextField(
        blank=True,
        help_text="Reason for the coordinator change"
    )
    changed_by = models.CharField(
        max_length=200,
        default='System',
        help_text="Who made the change (username or 'CSV Import', 'System', etc.)"
    )
    
    class Meta:
        ordering = ['-change_date']
        verbose_name = 'Initiative Coordinator Change'
        verbose_name_plural = 'Initiative Coordinator Changes'
        indexes = [
            models.Index(fields=['initiative']),
            models.Index(fields=['change_date']),
            models.Index(fields=['previous_coordinator']),
            models.Index(fields=['new_coordinator']),
        ]
    
    def __str__(self):
        """
        String representation of the InitiativeCoordinatorChange.
        
        Returns:
            str: Description of the coordinator change
        """
        return f"{self.initiative.name}: {self.previous_coordinator.full_name} → {self.new_coordinator.full_name}"
    
    def get_previous_coordinator_name(self):
        """
        Get the previous coordinator's name.
        
        Returns:
            str: Previous coordinator's full name
        """
        return self.previous_coordinator.full_name if self.previous_coordinator else 'Unknown'
    
    def get_new_coordinator_name(self):
        """
        Get the new coordinator's name.
        
        Returns:
            str: New coordinator's full name
        """
        return self.new_coordinator.full_name if self.new_coordinator else 'Unknown'
