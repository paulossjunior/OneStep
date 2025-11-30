"""
Serializers for the scholarships app.
"""
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal
from datetime import date, timedelta
from drf_spectacular.utils import extend_schema_field
from apps.scholarships.models import ScholarshipType, Scholarship
from apps.people.models import Person
from apps.organizational_group.models import Organization, Campus
from apps.initiatives.models import Initiative


class ScholarshipTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for ScholarshipType with all fields and scholarship count.
    """
    scholarship_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ScholarshipType
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_active',
            'scholarship_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'scholarship_count']
    
    @extend_schema_field(serializers.IntegerField)
    def get_scholarship_count(self, obj) -> int:
        """Get the count of scholarships for this type."""
        return obj.scholarship_count()


class PersonBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Person with minimal fields.
    """
    class Meta:
        model = Person
        fields = ['id', 'name', 'email']
        read_only_fields = ['id', 'name', 'email']


class OrganizationBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Organization with minimal fields.
    """
    class Meta:
        model = Organization
        fields = ['id', 'name']
        read_only_fields = ['id', 'name']


class CampusBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Campus with minimal fields.
    """
    class Meta:
        model = Campus
        fields = ['id', 'name', 'code']
        read_only_fields = ['id', 'name', 'code']


class InitiativeBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for Initiative with minimal fields.
    """
    class Meta:
        model = Initiative
        fields = ['id', 'name', 'type']
        read_only_fields = ['id', 'name', 'type']


class ScholarshipSerializer(serializers.ModelSerializer):
    """
    Serializer for Scholarship with all fields and computed properties.
    Includes nested basic information for related objects.
    """
    type = ScholarshipTypeSerializer(read_only=True)
    campus = CampusBasicSerializer(read_only=True)
    supervisor = PersonBasicSerializer(read_only=True)
    student = PersonBasicSerializer(read_only=True)
    sponsor = OrganizationBasicSerializer(read_only=True)
    initiative = InitiativeBasicSerializer(read_only=True)
    
    # Computed properties
    duration_months = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'type',
            'campus',
            'start_date',
            'end_date',
            'supervisor',
            'student',
            'value',
            'sponsor',
            'initiative',
            'duration_months',
            'is_active',
            'total_value',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'duration_months',
            'is_active',
            'total_value',
            'created_at',
            'updated_at'
        ]
    
    @extend_schema_field(serializers.IntegerField)
    def get_duration_months(self, obj) -> int:
        """Get the duration in months."""
        return obj.duration_months()
    
    @extend_schema_field(serializers.BooleanField)
    def get_is_active(self, obj) -> bool:
        """Check if scholarship is currently active."""
        return obj.is_active()
    
    @extend_schema_field(serializers.DecimalField(max_digits=12, decimal_places=2))
    def get_total_value(self, obj) -> str:
        """Get the total scholarship value."""
        return str(obj.total_value())


class ScholarshipDetailSerializer(ScholarshipSerializer):
    """
    Detailed serializer for Scholarship with full nested objects.
    Extends ScholarshipSerializer with more detailed related object information.
    """
    pass


class ScholarshipCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating scholarships.
    Uses IDs for foreign key relationships.
    """
    
    class Meta:
        model = Scholarship
        fields = [
            'id',
            'title',
            'type',
            'campus',
            'start_date',
            'end_date',
            'supervisor',
            'student',
            'value',
            'sponsor',
            'initiative'
        ]
        read_only_fields = ['id']
    
    def validate_title(self, value):
        """
        Validate that title is not empty or whitespace only.
        """
        if not value or not value.strip():
            raise serializers.ValidationError('Title cannot be empty or contain only whitespace.')
        return value.strip()
    
    def validate_value(self, value):
        """
        Validate that scholarship value is greater than zero.
        
        Requirements: 7.1
        """
        if value is None:
            raise serializers.ValidationError('Scholarship value is required.')
        
        if value <= 0:
            raise serializers.ValidationError('Scholarship value must be greater than zero.')
        
        return value
    
    def validate_start_date(self, value):
        """
        Validate that start_date is not too far in the future (within 10 years).
        
        Requirements: 7.2
        """
        if value:
            max_future_date = date.today() + timedelta(days=365 * 10)
            if value > max_future_date:
                raise serializers.ValidationError(
                    'Start date cannot be more than 10 years in the future.'
                )
        return value
    
    def validate(self, data):
        """
        Validate the entire scholarship data.
        
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
        """
        # Get values from data or instance (for updates)
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        supervisor = data.get('supervisor')
        student = data.get('student')
        scholarship_type = data.get('type')
        
        # For updates, get existing values if not provided
        if self.instance:
            start_date = start_date or self.instance.start_date
            end_date = end_date if 'end_date' in data else self.instance.end_date
            supervisor = supervisor or self.instance.supervisor
            student = student or self.instance.student
            scholarship_type = scholarship_type or self.instance.type
        
        # Validate end_date is after or equal to start_date
        if end_date and start_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        
        # Validate end_date is not more than 10 years after start_date (Requirement 7.3)
        if start_date and end_date:
            max_end_date = start_date + timedelta(days=365 * 10)
            if end_date > max_end_date:
                raise serializers.ValidationError({
                    'end_date': 'End date cannot be more than 10 years after start date.'
                })
        
        # Validate that supervisor and student are different people
        if supervisor and student:
            if supervisor.id == student.id:
                raise serializers.ValidationError({
                    'student': 'Supervisor and student must be different people.'
                })
        
        # Validate that type is active when creating new scholarship
        if scholarship_type and not self.instance:
            if not scholarship_type.is_active:
                raise serializers.ValidationError({
                    'type': 'Cannot create scholarship with inactive scholarship type.'
                })
        
        # Check for overlapping scholarships for the same student (Requirement 7.4)
        if student and start_date:
            overlapping_query = Scholarship.objects.filter(
                student=student
            )
            
            # Exclude current instance if updating
            if self.instance:
                overlapping_query = overlapping_query.exclude(pk=self.instance.pk)
            
            # Filter for overlapping date ranges
            if end_date:
                # This scholarship has an end date
                from django.db.models import Q
                overlapping_query = overlapping_query.filter(
                    Q(
                        # Other scholarship has no end date and starts before this one ends
                        Q(end_date__isnull=True) & Q(start_date__lte=end_date)
                    ) |
                    Q(
                        # Other scholarship has end date and ranges overlap
                        Q(end_date__isnull=False) &
                        Q(start_date__lte=end_date) &
                        Q(end_date__gte=start_date)
                    )
                )
            else:
                # This scholarship has no end date (ongoing)
                overlapping_query = overlapping_query.filter(
                    Q(end_date__isnull=True) |  # Other ongoing scholarships
                    Q(end_date__gte=start_date)  # Other scholarships that end after this starts
                )
            
            if overlapping_query.exists():
                overlapping = overlapping_query.first()
                raise serializers.ValidationError({
                    'student': (
                        f'Student {student.name} already has an overlapping scholarship: '
                        f'"{overlapping.title}" ({overlapping.start_date} to '
                        f'{overlapping.end_date or "ongoing"}).'
                    )
                })
        
        return data
    
    def create(self, validated_data):
        """
        Create a new scholarship instance.
        Calls model's full_clean() to ensure all model validations are run.
        """
        scholarship = Scholarship(**validated_data)
        try:
            scholarship.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        scholarship.save()
        return scholarship
    
    def update(self, instance, validated_data):
        """
        Update an existing scholarship instance.
        Calls model's full_clean() to ensure all model validations are run.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        try:
            instance.full_clean()
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        
        instance.save()
        return instance
