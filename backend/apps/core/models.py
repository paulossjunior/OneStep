from django.db import models
from django.core.exceptions import ValidationError


class TimestampedModel(models.Model):
    """
    Abstract base model that provides timestamp fields for all models.
    
    Attributes:
        created_at (DateTimeField): Timestamp when the record was created
        updated_at (DateTimeField): Timestamp when the record was last updated
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the record was last updated"
    )
    
    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        """
        Override save method to run full_clean validation before saving.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class BaseManager(models.Manager):
    """
    Base manager class with common query methods.
    """
    
    def active(self):
        """
        Return queryset of active records (can be overridden by subclasses).
        """
        return self.get_queryset()
    
    def created_between(self, start_date, end_date):
        """
        Return records created between two dates.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            
        Returns:
            QuerySet: Filtered queryset
        """
        return self.get_queryset().filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )