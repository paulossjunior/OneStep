from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Person


class PersonSerializer(serializers.ModelSerializer):
    """
    Serializer for Person model with validation and computed fields.
    
    Provides serialization for Person CRUD operations with proper validation
    and additional computed fields for API responses.
    """
    
    # Read-only computed fields
    full_name = serializers.CharField(
        read_only=True,
        help_text="Person's full name (same as name field)"
    )
    coordinated_count = serializers.SerializerMethodField(
        help_text="Number of initiatives this person coordinates"
    )
    team_count = serializers.SerializerMethodField(
        help_text="Number of initiatives this person is a team member of"
    )
    student_count = serializers.SerializerMethodField(
        help_text="Number of initiatives this person is a student in"
    )
    
    class Meta:
        model = Person
        fields = [
            'id',
            'name',
            'email',
            'full_name',
            'coordinated_count',
            'team_count',
            'student_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'full_name']
    
    def get_coordinated_count(self, obj):
        """
        Get the count of initiatives this person coordinates.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            int: Number of coordinated initiatives
        """
        if hasattr(obj, 'coordinated_initiatives'):
            return obj.coordinated_initiatives.count()
        return 0
    
    def get_team_count(self, obj):
        """
        Get the count of initiatives this person is a team member of.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            int: Number of team memberships
        """
        if hasattr(obj, 'team_initiatives'):
            return obj.team_initiatives.count()
        return 0
    
    def get_student_count(self, obj):
        """
        Get the count of initiatives this person is a student in.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            int: Number of student participations
        """
        if hasattr(obj, 'student_initiatives'):
            return obj.student_initiatives.count()
        return 0
    
    def validate_email(self, value):
        """
        Validate email field with case-insensitive uniqueness check.
        
        Args:
            value (str): Email value to validate
            
        Returns:
            str: Validated and normalized email
            
        Raises:
            serializers.ValidationError: If email already exists
        """
        if value:
            # Normalize email to lowercase
            value = value.lower().strip()
            
            # Check for existing email (case-insensitive)
            existing_person = Person.objects.filter(email__iexact=value)
            if self.instance:
                existing_person = existing_person.exclude(pk=self.instance.pk)
            
            if existing_person.exists():
                raise serializers.ValidationError("A person with this email already exists.")
        
        return value
    
    def validate_name(self, value):
        """
        Validate name field.
        
        Args:
            value (str): Name value to validate
            
        Returns:
            str: Validated and cleaned name
            
        Raises:
            serializers.ValidationError: If name is empty after stripping
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        return value.strip()
    

    
    def validate(self, data):
        """
        Object-level validation.
        
        Args:
            data (dict): Validated data dictionary
            
        Returns:
            dict: Validated data
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        # Create a temporary instance for model validation
        instance = self.instance or Person()
        
        # Update instance with validated data
        for attr, value in data.items():
            setattr(instance, attr, value)
        
        try:
            # Run model's clean method for additional validation
            instance.clean()
        except DjangoValidationError as e:
            # Convert Django validation errors to DRF validation errors
            if hasattr(e, 'error_dict'):
                raise serializers.ValidationError(e.error_dict)
            else:
                raise serializers.ValidationError(e.messages)
        
        return data


class PersonDetailSerializer(PersonSerializer):
    """
    Detailed serializer for Person model with related initiatives.
    
    Extends PersonSerializer to include related initiative information
    for detailed views.
    """
    
    # Related initiatives (will be populated when Initiative serializer is available)
    coordinated_initiatives = serializers.SerializerMethodField(
        help_text="List of initiatives this person coordinates (limited to 10 most recent)"
    )
    team_initiatives = serializers.SerializerMethodField(
        help_text="List of initiatives this person is a team member of (limited to 10 most recent)"
    )
    student_initiatives = serializers.SerializerMethodField(
        help_text="List of initiatives this person is a student in (limited to 10 most recent)"
    )
    
    class Meta(PersonSerializer.Meta):
        fields = PersonSerializer.Meta.fields + [
            'coordinated_initiatives',
            'team_initiatives',
            'student_initiatives'
        ]
    
    def get_coordinated_initiatives(self, obj):
        """
        Get basic information about coordinated initiatives.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            list: List of coordinated initiative basic info
        """
        if hasattr(obj, 'coordinated_initiatives'):
            return [
                {
                    'id': initiative.id,
                    'name': initiative.name,
                    'type': initiative.type.code if hasattr(initiative, 'type') and initiative.type else None,
                    'type_name': initiative.type.name if hasattr(initiative, 'type') and initiative.type else None
                }
                for initiative in obj.coordinated_initiatives.all()[:10]  # Limit to 10 for performance
            ]
        return []
    
    def get_team_initiatives(self, obj):
        """
        Get basic information about team initiatives.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            list: List of team initiative basic info
        """
        if hasattr(obj, 'team_initiatives'):
            return [
                {
                    'id': initiative.id,
                    'name': initiative.name,
                    'type': initiative.type.code if hasattr(initiative, 'type') and initiative.type else None,
                    'type_name': initiative.type.name if hasattr(initiative, 'type') and initiative.type else None
                }
                for initiative in obj.team_initiatives.all()[:10]  # Limit to 10 for performance
            ]
        return []
    
    def get_student_initiatives(self, obj):
        """
        Get basic information about student initiatives.
        
        Args:
            obj (Person): Person instance
            
        Returns:
            list: List of student initiative basic info
        """
        if hasattr(obj, 'student_initiatives'):
            return [
                {
                    'id': initiative.id,
                    'name': initiative.name,
                    'type': initiative.type.code if hasattr(initiative, 'type') and initiative.type else None,
                    'type_name': initiative.type.name if hasattr(initiative, 'type') and initiative.type else None
                }
                for initiative in obj.student_initiatives.all()[:10]  # Limit to 10 for performance
            ]
        return []