from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q, F, CheckConstraint
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from apps.core.models import TimestampedModel


class ScholarshipType(TimestampedModel):
    """
    Represents a type/category of scholarship.
    
    Attributes:
        name: Display name (e.g., "Research Scholarship")
        code: Unique code (e.g., "research")
        description: Detailed description
        is_active: Whether this type is currently active
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Display name of the scholarship type"
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique code for the scholarship type"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the scholarship type"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this scholarship type is currently active"
    )
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = "Scholarship Type"
        verbose_name_plural = "Scholarship Types"
    
    def __str__(self):
        """Return string representation of the scholarship type."""
        return self.name
    
    def clean(self):
        """
        Validate the scholarship type data.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        # Validate name is not empty or whitespace only
        if self.name and not self.name.strip():
            raise ValidationError({
                'name': 'Name cannot be empty or contain only whitespace.'
            })
        
        # Validate code is not empty or whitespace only
        if self.code and not self.code.strip():
            raise ValidationError({
                'code': 'Code cannot be empty or contain only whitespace.'
            })
        
        # Normalize name and code by stripping whitespace
        if self.name:
            self.name = self.name.strip()
        if self.code:
            self.code = self.code.strip().lower()
    
    def scholarship_count(self):
        """
        Return the count of scholarships associated with this type.
        
        Returns:
            int: Number of scholarships of this type
        """
        return self.scholarships.count()


class Scholarship(TimestampedModel):
    """
    Represents a scholarship award.
    
    Attributes:
        title: Descriptive name for the scholarship
        type: Type of scholarship
        campus: Campus where scholarship is executed
        start_date: Scholarship start date
        end_date: Scholarship end date (optional)
        supervisor: Person supervising the scholarship
        student: Person receiving the scholarship
        value: Monthly scholarship value in BRL
        sponsor: Organization sponsoring the scholarship (optional)
        initiative: Related initiative/project (optional)
    """
    title = models.CharField(
        max_length=300,
        help_text="Descriptive name for the scholarship"
    )
    type = models.ForeignKey(
        ScholarshipType,
        on_delete=models.PROTECT,
        related_name='scholarships',
        help_text="Type of scholarship"
    )
    campus = models.ForeignKey(
        'organizational_group.Campus',
        on_delete=models.PROTECT,
        related_name='scholarships',
        help_text="Campus where scholarship is executed"
    )
    start_date = models.DateField(
        help_text="Scholarship start date"
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scholarship end date (optional)"
    )
    supervisor = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='supervised_scholarships',
        help_text="Person supervising the scholarship"
    )
    student = models.ForeignKey(
        'people.Person',
        on_delete=models.PROTECT,
        related_name='received_scholarships',
        help_text="Person receiving the scholarship"
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Monthly scholarship value in BRL"
    )
    sponsor = models.ForeignKey(
        'organizational_group.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sponsored_scholarships',
        help_text="Organization sponsoring the scholarship (optional)"
    )
    initiative = models.ForeignKey(
        'initiatives.Initiative',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='scholarships',
        help_text="Related initiative/project (optional)"
    )
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'Scholarship'
        verbose_name_plural = 'Scholarships'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['campus']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
            models.Index(fields=['student']),
            models.Index(fields=['supervisor']),
            models.Index(fields=['type']),
            models.Index(fields=['initiative']),
            models.Index(fields=['sponsor']),
        ]
        constraints = [
            CheckConstraint(
                check=Q(end_date__gte=F('start_date')) | Q(end_date__isnull=True),
                name='scholarship_end_date_after_start_date'
            ),
            CheckConstraint(
                check=Q(value__gt=0),
                name='scholarship_value_positive'
            ),
        ]
    
    def __str__(self):
        """Return string representation of the scholarship."""
        return f"{self.title} - {self.student.name}"
    
    def clean(self):
        """
        Validate the scholarship data.
        
        Raises:
            ValidationError: If validation fails
        """
        super().clean()
        
        errors = {}
        
        # Validate title is not empty or whitespace only
        if self.title and not self.title.strip():
            errors['title'] = 'Title cannot be empty or contain only whitespace.'
        
        # Normalize title by stripping whitespace
        if self.title:
            self.title = self.title.strip()
        
        # Validate that supervisor and student are different people
        if self.supervisor_id and self.student_id and self.supervisor_id == self.student_id:
            errors['student'] = 'Supervisor and student must be different people.'
        
        # Validate date logic
        if self.end_date and self.start_date:
            if self.end_date < self.start_date:
                errors['end_date'] = 'End date must be after or equal to start date.'
        
        # Validate start_date is not too far in the future (within 10 years)
        if self.start_date:
            max_future_date = date.today() + timedelta(days=365 * 10)
            if self.start_date > max_future_date:
                errors['start_date'] = 'Start date cannot be more than 10 years in the future.'
        
        # Validate end_date is not more than 10 years after start_date
        if self.start_date and self.end_date:
            max_end_date = self.start_date + timedelta(days=365 * 10)
            if self.end_date > max_end_date:
                errors['end_date'] = 'End date cannot be more than 10 years after start date.'
        
        # Validate value is positive
        if self.value is not None and self.value <= 0:
            errors['value'] = 'Scholarship value must be greater than zero.'
        
        # Validate that type is active when creating new scholarship
        if self.type_id and not self.pk:  # Only check on creation
            if hasattr(self.type, 'is_active') and not self.type.is_active:
                errors['type'] = 'Cannot create scholarship with inactive scholarship type.'
        
        # Check for overlapping scholarships for the same student
        if self.student_id and self.start_date:
            overlapping_query = Scholarship.objects.filter(
                student_id=self.student_id
            ).exclude(pk=self.pk)
            
            # Filter for overlapping date ranges
            if self.end_date:
                # This scholarship has an end date
                overlapping_query = overlapping_query.filter(
                    Q(
                        # Other scholarship has no end date and starts before this one ends
                        Q(end_date__isnull=True) & Q(start_date__lte=self.end_date)
                    ) |
                    Q(
                        # Other scholarship has end date and ranges overlap
                        Q(end_date__isnull=False) &
                        Q(start_date__lte=self.end_date) &
                        Q(end_date__gte=self.start_date)
                    )
                )
            else:
                # This scholarship has no end date (ongoing)
                overlapping_query = overlapping_query.filter(
                    Q(end_date__isnull=True) |  # Other ongoing scholarships
                    Q(end_date__gte=self.start_date)  # Other scholarships that end after this starts
                )
            
            if overlapping_query.exists():
                overlapping = overlapping_query.first()
                errors['student'] = (
                    f'Student {self.student.name} already has an overlapping scholarship: '
                    f'"{overlapping.title}" ({overlapping.start_date} to '
                    f'{overlapping.end_date or "ongoing"}).'
                )
        
        if errors:
            raise ValidationError(errors)
    
    def duration_months(self):
        """
        Calculate scholarship duration in months.
        
        Returns:
            int: Duration in months
        """
        if not self.start_date:
            return 0
        
        if not self.end_date:
            # Ongoing scholarship - calculate from start to today
            end = timezone.now().date()
        else:
            end = self.end_date
        
        # Calculate months difference
        years_diff = end.year - self.start_date.year
        months_diff = end.month - self.start_date.month
        total_months = years_diff * 12 + months_diff
        
        # Add 1 if the end day is >= start day (inclusive month counting)
        if end.day >= self.start_date.day:
            total_months += 1
        
        return max(0, total_months)
    
    def is_active(self):
        """
        Check if scholarship is currently active.
        
        Returns:
            bool: True if scholarship is active, False otherwise
        """
        today = timezone.now().date()
        
        if self.start_date > today:
            return False  # Not started yet
        
        if self.end_date and self.end_date < today:
            return False  # Already ended
        
        return True  # Active
    
    def total_value(self):
        """
        Calculate total scholarship value (value * duration).
        
        Returns:
            Decimal: Total scholarship value
        """
        months = self.duration_months()
        if self.value:
            return self.value * Decimal(months)
        return Decimal('0.00')
