# Generated migration to allow zero scholarship values

from django.db import migrations, models
from django.db.models import Q, F


class Migration(migrations.Migration):

    dependencies = [
        ('scholarships', '0003_populate_default_scholarship_types'),
    ]

    operations = [
        # Remove old constraint that required value > 0
        migrations.RemoveConstraint(
            model_name='scholarship',
            name='scholarship_value_positive',
        ),
        # Add new constraint that allows value >= 0
        migrations.AddConstraint(
            model_name='scholarship',
            constraint=models.CheckConstraint(
                check=Q(value__gte=0),
                name='scholarship_value_non_negative'
            ),
        ),
    ]
