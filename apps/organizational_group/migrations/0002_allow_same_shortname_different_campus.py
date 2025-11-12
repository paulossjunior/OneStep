# Generated migration to allow same short_name on different campuses

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizational_group', '0001_initial'),
    ]

    operations = [
        # Remove old constraint
        migrations.RemoveConstraint(
            model_name='organizationalunit',
            name='unique_short_name_organization',
        ),
        # Add new constraint that includes campus
        migrations.AddConstraint(
            model_name='organizationalunit',
            constraint=models.UniqueConstraint(
                fields=['short_name', 'organization', 'campus'],
                name='unique_short_name_organization_campus'
            ),
        ),
    ]
