from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from apps.core.models import TimestampedModel


class Person(TimestampedModel):
    """
    Person model representing individuals who can coordinate or participate in initiatives.
    
    Attributes:
        name (CharField): Person's full name
        email (EmailField): Person's email address (unique)
    """
    
    name = models.CharField(
        max_length=200,
        help_text="Person's full name"
    )
    email = models.EmailField(
        unique=True,
        help_text="Person's email address (must be unique)"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Person'
        verbose_name_plural = 'People'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        """
        String representation of the Person.
        
        Returns:
            str: Name of the person
        """
        return self.name
    
    @property
    def full_name(self):
        """
        Property that returns the person's full name.
        
        Returns:
            str: Full name (same as name field)
        """
        return self.name
    
    def clean(self):
        """
        Custom validation for the Person model.
        """
        super().clean()
        
        # Validate that name is not empty after stripping whitespace
        if not self.name or not self.name.strip():
            raise ValidationError({'name': 'Name cannot be empty.'})
        
        # Clean up whitespace
        if self.name:
            self.name = self.name.strip()
        
        # Validate email uniqueness (case-insensitive)
        if self.email:
            self.email = self.email.lower()
            existing_person = Person.objects.filter(email__iexact=self.email).exclude(pk=self.pk).first()
            if existing_person:
                raise ValidationError({'email': 'A person with this email already exists.'})
    
    def get_coordinated_initiatives_count(self):
        """
        Get the count of initiatives this person coordinates.
        
        Returns:
            int: Number of initiatives coordinated by this person
        """
        return getattr(self, 'coordinated_initiatives', self.__class__.objects.none()).count()
    
    def get_team_initiatives_count(self):
        """
        Get the count of initiatives this person is a team member of.
        
        Returns:
            int: Number of initiatives this person is a team member of
        """
        return getattr(self, 'team_initiatives', self.__class__.objects.none()).count()