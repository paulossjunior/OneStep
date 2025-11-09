from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from apps.core.models import TimestampedModel
from datetime import date


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


class OrganizationalGroupLeadership(TimestampedModel):
    """
    Through model tracking leadership relationships with history.
    
    Attributes:
        group (ForeignKey): Reference to the OrganizationalGroup
        person (ForeignKey): Reference to the Person who is a leader
        start_date (DateField): Date when leadership began
        end_date (DateField): Date when leadership ended (null if ongoing)
        is_active (BooleanField): Whether this is an active leadership
    """
    
    group = models.ForeignKey(
        'OrganizationalGroup',
        on_delete=models.CASCADE,
        help_text="Organizational group being led"
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
        verbose_name = 'Organizational Group Leadership'
        verbose_name_plural = 'Organizational Group Leaderships'
        indexes = [
            models.Index(fields=['group', 'is_active']),
            models.Index(fields=['person']),
            models.Index(fields=['start_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'person', 'start_date'],
                name='unique_group_person_start_date'
            ),
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F('start_date')) | models.Q(end_date__isnull=True),
                name='end_date_after_start_date_leadership'
            )
        ]
    
    def __str__(self):
        """
        String representation of the OrganizationalGroupLeadership.
        
        Returns:
            str: Description of the leadership relationship
        """
        status = "Active" if self.is_active else "Inactive"
        return f"{self.person.name} - {self.group.name} ({status})"
    
    def clean(self):
        """
        Custom validation for the OrganizationalGroupLeadership model.
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
        if self.is_active and self.group_id and self.person_id:
            existing_active = OrganizationalGroupLeadership.objects.filter(
                group=self.group,
                person=self.person,
                is_active=True
            ).exclude(pk=self.pk)
            
            if existing_active.exists():
                raise ValidationError({
                    'person': 'This person is already an active leader of this organizational group.'
                })


class OrganizationalGroup(TimestampedModel):
    """
    Represents a university research or organizational group.
    
    Attributes:
        name (CharField): Full organizational group name
        short_name (CharField): Abbreviated organizational group name
        url (URLField): Organizational group website URL (optional)
        type (CharField): Organizational group type (Research or Extension)
        knowledge_area (CharField): Field of study or research domain
        campus (ForeignKey): University campus affiliation
        leaders (ManyToManyField): People who lead the organizational group (through OrganizationalGroupLeadership)
        members (ManyToManyField): People who are members of the organizational group
        initiatives (ManyToManyField): Initiatives associated with the organizational group
    """
    
    TYPE_RESEARCH = 'research'
    TYPE_EXTENSION = 'extension'
    TYPE_CHOICES = [
        (TYPE_RESEARCH, 'Research'),
        (TYPE_EXTENSION, 'Extension'),
    ]
    
    name = models.CharField(
        max_length=200,
        help_text="Full organizational group name"
    )
    short_name = models.CharField(
        max_length=50,
        help_text="Abbreviated organizational group name"
    )
    url = models.URLField(
        blank=True,
        help_text="Organizational group website URL (optional)"
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Organizational group type (Research or Extension)"
    )
    knowledge_area = models.ForeignKey(
        'KnowledgeArea',
        on_delete=models.PROTECT,
        related_name='groups',
        help_text="Knowledge area foreign key"
    )
    campus = models.ForeignKey(
        'Campus',
        on_delete=models.PROTECT,
        related_name='groups',
        help_text="University campus affiliation"
    )
    
    # Many-to-many relationships
    leaders = models.ManyToManyField(
        'people.Person',
        through='OrganizationalGroupLeadership',
        related_name='led_groups',
        help_text="People who lead the organizational group"
    )
    members = models.ManyToManyField(
        'people.Person',
        related_name='member_groups',
        blank=True,
        help_text="People who are members of the organizational group"
    )
    initiatives = models.ManyToManyField(
        'initiatives.Initiative',
        related_name='groups',
        blank=True,
        help_text="Initiatives associated with the organizational group"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Organizational Group'
        verbose_name_plural = 'Organizational Groups'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['short_name']),
            models.Index(fields=['type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['short_name', 'campus'],
                name='unique_short_name_campus_id'
            )
        ]
    
    def __str__(self):
        """
        String representation of the OrganizationalGroup.
        
        Returns:
            str: Name of the organizational group
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the OrganizationalGroup model.
        """
        super().clean()
        
        # Validate that name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Organizational group name cannot be empty.'})
        
        # Validate that short_name is not empty after stripping whitespace
        if not self.short_name or not self.short_name.strip():
            raise ValidationError({'short_name': 'Short name cannot be empty.'})
        
        # Validate that type is provided
        if not self.type:
            raise ValidationError({'type': 'Organizational group type is required.'})
        
        # Validate that knowledge_area FK exists
        if not self.knowledge_area_id:
            raise ValidationError({'knowledge_area': 'Knowledge area is required.'})
        
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
        
        # Validate unique constraint for short_name + campus
        if self.short_name and self.campus_id:
            existing_group = OrganizationalGroup.objects.filter(
                short_name__iexact=self.short_name,
                campus_id=self.campus_id
            ).exclude(pk=self.pk)
            
            if existing_group.exists():
                raise ValidationError({
                    'short_name': f'An organizational group with short name "{self.short_name}" already exists on campus "{self.campus.name}".'
                })
    
    def get_current_leaders(self):
        """
        Returns QuerySet of current leaders (is_active=True).
        
        Returns:
            QuerySet: Current leaders of the organizational group
        """
        return self.leaders.filter(
            organizationalgroupleadership__is_active=True,
            organizationalgroupleadership__group=self
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
            OrganizationalGroupLeadership: The created leadership relationship
            
        Raises:
            ValidationError: If the person is already an active leader
        """
        if start_date is None:
            start_date = date.today()
        
        # Check if person is already an active leader
        existing_active = OrganizationalGroupLeadership.objects.filter(
            group=self,
            person=person,
            is_active=True
        )
        
        if existing_active.exists():
            raise ValidationError(
                f'{person.name} is already an active leader of {self.name}.'
            )
        
        # Create the leadership relationship
        leadership = OrganizationalGroupLeadership.objects.create(
            group=self,
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
            leadership = OrganizationalGroupLeadership.objects.get(
                group=self,
                person=person,
                is_active=True
            )
        except OrganizationalGroupLeadership.DoesNotExist:
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
