from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimestampedModel


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
        team_members (ManyToManyField): People who are team members
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
    team_members = models.ManyToManyField(
        'people.Person',
        blank=True,
        related_name='team_initiatives',
        help_text="People who are team members of this initiative"
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