from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from apps.core.models import TimestampedModel


class PersonEmail(TimestampedModel):
    """
    Email addresses associated with a Person.
    
    Allows a person to have multiple email addresses.
    
    Attributes:
        person (ForeignKey): Person this email belongs to
        email (EmailField): Email address (unique)
        is_primary (BooleanField): Whether this is the primary email
    """
    
    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='emails',
        help_text="Person this email belongs to"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address (must be unique across all people)"
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary email for this person"
    )
    
    class Meta:
        ordering = ['-is_primary', 'email']
        verbose_name = 'Person Email'
        verbose_name_plural = 'Person Emails'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['person', 'is_primary']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['person', 'email'],
                name='unique_person_email'
            )
        ]
    
    def __str__(self):
        """
        String representation of the PersonEmail.
        
        Returns:
            str: Email address
        """
        return self.email
    
    def clean(self):
        """
        Custom validation for the PersonEmail model.
        """
        super().clean()
        
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure only one primary email per person.
        """
        if self.is_primary:
            # Set all other emails for this person to non-primary
            PersonEmail.objects.filter(person=self.person, is_primary=True).update(is_primary=False)
        
        super().save(*args, **kwargs)


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
        blank=True,
        null=True,
        help_text="Person's primary email address (optional)"
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
        
        # Normalize email if provided
        if self.email:
            self.email = self.email.lower().strip()
    
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