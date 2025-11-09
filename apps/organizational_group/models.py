from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from apps.core.models import TimestampedModel
from datetime import date


class Organization(TimestampedModel):
    """
    Represents an organization that contains organizational units.
    
    Attributes:
        name (CharField): Organization name
        description (TextField): Organization description
    """
    
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Organization name"
    )
    description = models.TextField(
        blank=True,
        help_text="Organization description"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        """
        String representation of the Organization.
        
        Returns:
            str: Name of the organization
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the Organization model.
        """
        super().clean()
        
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Organization name cannot be empty.'})
        
        if self.name:
            self.name = self.name.strip()
    
    def unit_count(self):
        """
        Returns count of organizational units in this organization.
        
        Returns:
            int: Number of organizational units
        """
        return self.units.count()


class OrganizationalType(TimestampedModel):
    """
    Represents the type of an organizational unit (e.g., Research, Extension).
    
    Attributes:
        name (CharField): Type name
        code (CharField): Type code
        description (TextField): Type description
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Type name (e.g., Research, Extension)"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Type code (e.g., research, extension)"
    )
    description = models.TextField(
        blank=True,
        help_text="Type description"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Organizational Type'
        verbose_name_plural = 'Organizational Types'
        indexes = [
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        """
        String representation of the OrganizationalType.
        
        Returns:
            str: Name of the type
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the OrganizationalType model.
        """
        super().clean()
        
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Type name cannot be empty.'})
        
        if not self.code or not self.code.strip():
            raise ValidationError({'code': 'Type code cannot be empty.'})
        
        if self.name:
            self.name = self.name.strip()
        
        if self.code:
            self.code = self.code.strip().lower()


class KnowledgeArea(TimestampedModel):
    """
    Represents an academic or research domain that categorizes organizational groups.
    
    Attributes:
        name (CharField): Unique knowledge area name
        description (TextField): Optional detailed description
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Knowledge area name"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the knowledge area"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Knowledge Area'
        verbose_name_plural = 'Knowledge Areas'
        indexes = [
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        """
        String representation of the KnowledgeArea.
        
        Returns:
            str: Name of the knowledge area
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the KnowledgeArea model.
        
        Validates:
            - Name is not empty after stripping whitespace
            - Case-insensitive uniqueness of name
        """
        super().clean()
        
        # Validate that name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Knowledge area name cannot be empty.'})
        
        # Clean up whitespace
        if self.name:
            self.name = self.name.strip()
        
        # Validate case-insensitive uniqueness
        if self.name:
            existing = KnowledgeArea.objects.filter(
                name__iexact=self.name
            ).exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({
                    'name': f'Knowledge area with name "{self.name}" already exists (case-insensitive).'
                })
    
    def group_count(self):
        """
        Returns count of organizational groups in this knowledge area.
        
        Returns:
            int: Number of organizational groups in this knowledge area
        """
        # Check if the reverse relationship exists (will be added in task 2)
        if hasattr(self, 'groups'):
            return self.groups.count()
        return 0


class Campus(TimestampedModel):
    """
    Represents a university campus location.
    
    Attributes:
        name (CharField): Full campus name
        code (CharField): Short campus code/identifier
        location (CharField): Physical location or address
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Full campus name"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Short campus code/identifier"
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        help_text="Physical location or address"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Campus'
        verbose_name_plural = 'Campuses'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        """
        String representation of the Campus.
        
        Returns:
            str: Name of the campus
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the Campus model.
        """
        super().clean()
        
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Campus name cannot be empty.'})
        
        if not self.code or not self.code.strip():
            raise ValidationError({'code': 'Campus code cannot be empty.'})
        
        if self.name:
            self.name = self.name.strip()
        
        if self.code:
            self.code = self.code.strip().upper()
    
    def group_count(self):
        """
        Returns count of organizational groups on this campus.
        
        Returns:
            int: Number of organizational groups on this campus
        """
        return self.groups.count()


class OrganizationalUnitLeadership(TimestampedModel):
    """
    Through model tracking leadership relationships with history.
    
    Attributes:
        unit (ForeignKey): Reference to the OrganizationalUnit
        person (ForeignKey): Reference to the Person who is a leader
        start_date (DateField): Date when leadership began
        end_date (DateField): Date when leadership ended (null if ongoing)
        is_active (BooleanField): Whether this is an active leadership
    """
    
    unit = models.ForeignKey(
        'OrganizationalUnit',
        on_delete=models.CASCADE,
        help_text="Organizational unit being led"
    )
    person = models.ForeignKey(
        'people.Person',
        on_delete=models.CASCADE,
        help_text="Person who is a leader"
    )
    start_date = models.DateField(
        help_text="Date when leadership began"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date when leadership ended (null if ongoing)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this is an active leadership"
    )
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Organizational Unit Leadership'
        verbose_name_plural = 'Organizational Unit Leaderships'
        indexes = [
            models.Index(fields=['unit', 'is_active']),
            models.Index(fields=['person']),
            models.Index(fields=['start_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['unit', 'person', 'start_date'],
                name='unique_unit_person_start_date'
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')) | models.Q(end_date__isnull=True),
                name='end_date_after_start_date_leadership'
            )
        ]
    
    def __str__(self):
        """
        String representation of the OrganizationalUnitLeadership.
        
        Returns:
            str: Description of the leadership relationship
        """
        status = "Active" if self.is_active else "Inactive"
        return f"{self.person.name} - {self.unit.name} ({status})"
    
    def clean(self):
        """
        Custom validation for the OrganizationalUnitLeadership model.
        """
        super().clean()
        
        # Validate date logic
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        
        # Validate that if end_date is set, is_active should be False
        if self.end_date and self.is_active:
            raise ValidationError({
                'is_active': 'Leadership with an end date should not be marked as active.'
            })
        
        # Check for duplicate active leaders
        if self.is_active and self.unit_id and self.person_id:
            existing_active = OrganizationalUnitLeadership.objects.filter(
                unit=self.unit,
                person=self.person,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError({
                    'person': 'This person is already an active leader of this organizational unit.'
                })


class OrganizationalUnit(TimestampedModel):
    """
    Represents an organizational unit within an organization.
    
    Attributes:
        name (CharField): Full organizational unit name
        short_name (CharField): Abbreviated organizational unit name
        url (URLField): Organizational unit website URL (optional)
        type (ForeignKey): Organizational unit type (Research, Extension, etc.)
        organization (ForeignKey): Parent organization
        knowledge_area (ForeignKey): Primary knowledge area (deprecated - use knowledge_areas)
        campus (ForeignKey): University campus affiliation
        leaders (ManyToManyField): People who lead the organizational unit (through OrganizationalUnitLeadership)
        members (ManyToManyField): People who are members of the organizational unit
        initiatives (ManyToManyField): Initiatives associated with the organizational unit
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Full organizational unit name"
    )
    short_name = models.CharField(
        max_length=50,
        help_text="Abbreviated organizational unit name"
    )
    url = models.URLField(
        blank=True,
        help_text="Organizational unit website URL (optional)"
    )
    type = models.ForeignKey(
        'OrganizationalType',
        on_delete=models.PROTECT,
        related_name='units',
        help_text="Organizational unit type (Research, Extension, etc.)"
    )
    organization = models.ForeignKey(
        'Organization',
        on_delete=models.PROTECT,
        related_name='units',
        help_text="Parent organization"
    )
    knowledge_area = models.ForeignKey(
        'KnowledgeArea',
        on_delete=models.PROTECT,
        related_name='units',
        null=True,
        blank=True,
        help_text="Primary knowledge area (deprecated - use knowledge_areas)"
    )
    campus = models.ForeignKey(
        'Campus',
        on_delete=models.PROTECT,
        related_name='units',
        help_text="University campus affiliation"
    )
    
    # Many-to-many relationships
    knowledge_areas = models.ManyToManyField(
        'KnowledgeArea',
        related_name='related_units',
        blank=True,
        help_text="Knowledge areas associated with this unit (from related initiatives)"
    )
    leaders = models.ManyToManyField(
        'people.Person',
        through='OrganizationalUnitLeadership',
        related_name='led_units',
        help_text="People who lead the organizational unit"
    )
    members = models.ManyToManyField(
        'people.Person',
        related_name='member_units',
        blank=True,
        help_text="People who are members of the organizational unit"
    )
    initiatives = models.ManyToManyField(
        'initiatives.Initiative',
        related_name='units',
        blank=True,
        help_text="Initiatives associated with the organizational unit"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Organizational Unit'
        verbose_name_plural = 'Organizational Units'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['short_name']),
            models.Index(fields=['type']),
            models.Index(fields=['organization']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['short_name', 'organization'],
                name='unique_short_name_organization'
            )
        ]
    
    def __str__(self):
        """
        String representation of the OrganizationalUnit.
        
        Returns:
            str: Name of the organizational unit
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the OrganizationalUnit model.
        """
        super().clean()
        
        # Validate that name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Organizational unit name cannot be empty.'})
        
        # Validate that short_name is not empty after stripping whitespace
        if not self.short_name or not self.short_name.strip():
            raise ValidationError({'short_name': 'Short name cannot be empty.'})
        
        # Validate that type is provided
        if not self.type_id:
            raise ValidationError({'type': 'Organizational unit type is required.'})
        
        # Validate that organization is provided
        if not self.organization_id:
            raise ValidationError({'organization': 'Organization is required.'})
        
        # Clean up whitespace
        if self.name:
            self.name = self.name.strip()
        
        if self.short_name:
            self.short_name = self.short_name.strip()
        
        # Validate URL format if provided
        if self.url:
            validator = URLValidator()
            try:
                validator(self.url)
            except ValidationError:
                raise ValidationError({'url': 'Enter a valid URL.'})
        
        # Validate unique constraint for short_name + organization
        if self.short_name and self.organization_id:
            existing_unit = OrganizationalUnit.objects.filter(
                short_name__iexact=self.short_name,
                organization_id=self.organization_id
            ).exclude(pk=self.pk)
            
            if existing_unit.exists():
                raise ValidationError({
                    'short_name': f'An organizational unit with short name "{self.short_name}" already exists in organization "{self.organization.name}".'
                })
    
    def get_current_leaders(self):
        """
        Returns QuerySet of current leaders (is_active=True).
        
        Returns:
            QuerySet: Current leaders of the organizational unit
        """
        return self.leaders.filter(
            organizationalunitleadership__is_active=True,
            organizationalunitleadership__unit=self
        ).distinct()
    
    def get_historical_leaders(self):
        """
        Returns QuerySet of all leaders including past ones.
        
        Returns:
            QuerySet: All leaders (current and historical)
        """
        return self.leaders.all().distinct()
    
    def add_leader(self, person, start_date=None):
        """
        Adds a person as a leader with optional start date.
        
        Args:
            person (Person): Person to add as leader
            start_date (date, optional): Leadership start date. Defaults to today.
            
        Returns:
            OrganizationalUnitLeadership: The created leadership relationship
            
        Raises:
            ValidationError: If the person is already an active leader
        """
        if start_date is None:
            start_date = date.today()
        
        # Check if person is already an active leader
        existing_active = OrganizationalUnitLeadership.objects.filter(
            unit=self,
            person=person,
            is_active=True
        )
        
        if existing_active.exists():
            raise ValidationError(
                f'{person.name} is already an active leader of {self.name}.'
            )
        
        # Create the leadership relationship
        leadership = OrganizationalUnitLeadership.objects.create(
            unit=self,
            person=person,
            start_date=start_date,
            is_active=True
        )
        
        return leadership
    
    def remove_leader(self, person, end_date=None):
        """
        Removes a person as leader by setting end_date and is_active=False.
        
        Args:
            person (Person): Person to remove as leader
            end_date (date, optional): Leadership end date. Defaults to today.
            
        Raises:
            ValidationError: If the person is not an active leader
        """
        if end_date is None:
            end_date = date.today()
        
        # Find the active leadership
        try:
            leadership = OrganizationalUnitLeadership.objects.get(
                unit=self,
                person=person,
                is_active=True
            )
        except OrganizationalUnitLeadership.DoesNotExist:
            raise ValidationError(
                f'{person.name} is not an active leader of {self.name}.'
            )
        
        # Update the leadership to mark it as inactive
        leadership.end_date = end_date
        leadership.is_active = False
        leadership.save()
    
    def leader_count(self):
        """
        Returns count of current leaders.
        
        Returns:
            int: Number of current leaders
        """
        return self.get_current_leaders().count()
    
    def member_count(self):
        """
        Returns count of members.
        
        Returns:
            int: Number of members
        """
        return self.members.count()
    
    def initiative_count(self):
        """
        Returns count of associated initiatives.
        
        Returns:
            int: Number of associated initiatives
        """
        return self.initiatives.count()
    
    def sync_knowledge_areas_from_initiatives(self):
        """
        Synchronize knowledge areas from associated initiatives.
        
        This method collects all unique knowledge areas from initiatives
        associated with this unit and updates the knowledge_areas field.
        """
        # Get all knowledge areas from associated initiatives
        knowledge_area_ids = set()
        for initiative in self.initiatives.all():
            for ka in initiative.knowledge_areas.all():
                knowledge_area_ids.add(ka.id)
        
        # Update the knowledge_areas field
        self.knowledge_areas.set(knowledge_area_ids)
    
    def get_all_knowledge_areas(self):
        """
        Get all knowledge areas (both primary and from initiatives).
        
        Returns:
            QuerySet: All knowledge areas associated with this unit
        """
        from apps.organizational_group.models import KnowledgeArea
        
        # Combine primary knowledge area with knowledge areas from initiatives
        ka_ids = set(self.knowledge_areas.values_list('id', flat=True))
        if self.knowledge_area_id:
            ka_ids.add(self.knowledge_area_id)
        
        return KnowledgeArea.objects.filter(id__in=ka_ids)


# Backward compatibility aliases
OrganizationalGroup = OrganizationalUnit
OrganizationalGroupLeadership = OrganizationalUnitLeadership
