from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Initiative, InitiativeType
from apps.people.serializers import PersonSerializer


class InitiativeTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for InitiativeType model.
    
    Provides serialization for InitiativeType with basic information.
    """
    
    class Meta:
        model = InitiativeType
        fields = [
            'id',
            'name',
            'code',
            'description',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InitiativeSerializer(serializers.ModelSerializer):
    """
    Serializer for Initiative model with validation and computed fields.
    
    Provides serialization for Initiative CRUD operations with proper validation
    and additional computed fields for API responses.
    """
    
    # Read-only computed fields
    coordinator_name = serializers.CharField(
        source='coordinator.full_name',
        read_only=True,
        help_text="Full name of the person coordinating this initiative"
    )
    type_name = serializers.CharField(
        source='type.name',
        read_only=True,
        help_text="Display name of the initiative type (e.g., Program, Project, Event)"
    )
    type_code = serializers.CharField(
        source='type.code',
        read_only=True,
        help_text="Code identifier for the initiative type (e.g., program, project, event)"
    )
    team_count = serializers.SerializerMethodField(
        help_text="Number of team members assigned to this initiative"
    )
    student_count = serializers.SerializerMethodField(
        help_text="Number of students participating in this initiative"
    )
    partnerships_count = serializers.SerializerMethodField(
        help_text="Number of partnership organizational units"
    )
    children_count = serializers.SerializerMethodField(
        help_text="Number of child initiatives under this initiative"
    )
    hierarchy_level = serializers.SerializerMethodField(
        help_text="Depth level in the initiative hierarchy (0 = root level)"
    )
    
    # Nested serialization for parent (basic info only to avoid deep nesting)
    parent_info = serializers.SerializerMethodField(
        help_text="Basic information about the parent initiative (id, name, type)"
    )
    
    # Demanding partner information
    demanding_partner_name = serializers.CharField(
        source='demanding_partner.name',
        read_only=True,
        help_text="Name of the organization that demands this initiative"
    )
    
    class Meta:
        model = Initiative
        fields = [
            'id',
            'name',
            'description',
            'type',
            'type_name',
            'type_code',
            'start_date',
            'end_date',
            'parent',
            'parent_info',
            'coordinator',
            'coordinator_name',
            'team_members',
            'students',
            'demanding_partner',
            'demanding_partner_name',
            'partnerships',
            'partnerships_count',
            'team_count',
            'student_count',
            'children_count',
            'hierarchy_level',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id', 
            'created_at', 
            'updated_at', 
            'coordinator_name',
            'type_name',
            'type_code',
            'demanding_partner_name',
            'partnerships_count',
            'team_count',
            'student_count',
            'children_count',
            'hierarchy_level',
            'parent_info'
        ]
    
    def get_team_count(self, obj):
        """
        Get the count of team members for this initiative.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            int: Number of team members
        """
        return obj.team_members.count()
    
    def get_student_count(self, obj):
        """
        Get the count of students for this initiative.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            int: Number of students
        """
        return obj.students.count()
    
    def get_partnerships_count(self, obj):
        """
        Get the count of partnerships for this initiative.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            int: Number of partnerships
        """
        return obj.partnerships_count
    
    def get_children_count(self, obj):
        """
        Get the count of child initiatives.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            int: Number of child initiatives
        """
        return obj.children.count()
    
    def get_hierarchy_level(self, obj):
        """
        Get the hierarchy level of this initiative.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            int: Hierarchy level (0 = root)
        """
        return obj.get_hierarchy_level()
    
    def get_parent_info(self, obj):
        """
        Get basic information about the parent initiative.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            dict or None: Parent initiative basic info
        """
        if obj.parent:
            return {
                'id': obj.parent.id,
                'name': obj.parent.name,
                'type_name': obj.parent.type.name,
                'type_code': obj.parent.type.code
            }
        return None
    
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
            raise serializers.ValidationError("Initiative name cannot be empty.")
        return value.strip()
    
    def validate_type(self, value):
        """
        Validate type field.
        
        Args:
            value (InitiativeType): Type instance to validate
            
        Returns:
            InitiativeType: Validated type
            
        Raises:
            serializers.ValidationError: If type is not valid or inactive
        """
        if not value.is_active:
            raise serializers.ValidationError("Selected initiative type is not active.")
        return value
    
    def validate_parent(self, value):
        """
        Validate parent field to prevent circular references.
        
        Args:
            value (Initiative): Parent initiative instance
            
        Returns:
            Initiative: Validated parent
            
        Raises:
            serializers.ValidationError: If circular reference detected
        """
        if value and self.instance:
            # Prevent self-reference
            if value.pk == self.instance.pk:
                raise serializers.ValidationError("An initiative cannot be its own parent.")
            
            # Check for circular reference
            current_parent = value
            while current_parent:
                if current_parent.pk == self.instance.pk:
                    raise serializers.ValidationError("Circular parent relationship detected.")
                current_parent = current_parent.parent
        
        return value
    
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
        # Validate date logic
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if end_date and start_date:
            if end_date < start_date:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after or equal to start date.'
                })
        
        # Create a temporary instance for model validation
        instance = self.instance or Initiative()
        
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


class InitiativeDetailSerializer(InitiativeSerializer):
    """
    Detailed serializer for Initiative model with nested related data.
    
    Extends InitiativeSerializer to include full related object information
    for detailed views.
    """
    
    # Full nested serialization for related objects
    type = InitiativeTypeSerializer(
        read_only=True,
        help_text="Complete initiative type information including name, code, and description"
    )
    coordinator = PersonSerializer(
        read_only=True,
        help_text="Complete information about the person coordinating this initiative"
    )
    team_members = PersonSerializer(
        many=True,
        read_only=True,
        help_text="List of all team members with their complete information"
    )
    students = PersonSerializer(
        many=True,
        read_only=True,
        help_text="List of all students with their complete information"
    )
    demanding_partner = serializers.SerializerMethodField(
        help_text="Complete information about the organization that demands this initiative"
    )
    children = serializers.SerializerMethodField(
        help_text="List of child initiatives with their basic information"
    )
    parent = serializers.SerializerMethodField(
        help_text="Complete information about the parent initiative"
    )
    
    class Meta(InitiativeSerializer.Meta):
        fields = InitiativeSerializer.Meta.fields + [
            'children'
        ]
    
    def get_children(self, obj):
        """
        Get child initiatives with basic information.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            list: List of child initiatives with basic info
        """
        # Use prefetched data if available to avoid additional queries
        if hasattr(obj, '_prefetched_objects_cache') and 'children' in obj._prefetched_objects_cache:
            children = obj._prefetched_objects_cache['children']
        else:
            children = obj.children.select_related('type', 'coordinator', 'parent').all()
        return InitiativeSerializer(children, many=True, context=self.context).data
    
    def get_parent(self, obj):
        """
        Get parent initiative with basic information.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            dict or None: Parent initiative with basic info
        """
        if obj.parent:
            return InitiativeSerializer(obj.parent, context=self.context).data
        return None
    
    def get_demanding_partner(self, obj):
        """
        Get demanding partner organization with complete information.
        
        Args:
            obj (Initiative): Initiative instance
            
        Returns:
            dict or None: Demanding partner organization data
        """
        if obj.demanding_partner:
            # Import here to avoid circular import
            from apps.organizational_group.serializers import OrganizationSerializer
            return OrganizationSerializer(obj.demanding_partner, context=self.context).data
        return None


class InitiativeCreateUpdateSerializer(InitiativeSerializer):
    """
    Serializer for Initiative creation and updates with write operations.
    
    Handles team member assignments and other write operations that require
    special handling.
    """
    
    # Allow writing to team_members and students fields
    team_member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of person IDs to assign as team members"
    )
    student_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of person IDs to assign as students"
    )
    demanding_partner_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True,
        help_text="ID of the organization that demands this initiative"
    )
    partnership_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of organizational unit IDs to assign as partnerships"
    )
    
    class Meta(InitiativeSerializer.Meta):
        fields = InitiativeSerializer.Meta.fields + ['team_member_ids', 'student_ids', 'demanding_partner_id', 'partnership_ids']
    
    def validate_demanding_partner_id(self, value):
        """
        Validate demanding_partner_id field.
        
        Args:
            value: Organization ID
            
        Returns:
            Organization instance or None
            
        Raises:
            serializers.ValidationError: If organization doesn't exist
        """
        if value is None:
            return None
        
        # Import here to avoid circular import
        from apps.organizational_group.models import Organization
        
        try:
            return Organization.objects.get(pk=value)
        except Organization.DoesNotExist:
            raise serializers.ValidationError(f"Organization with ID {value} does not exist.")
    
    def create(self, validated_data):
        """
        Create a new Initiative instance with team members, students, and partnerships.
        
        Args:
            validated_data (dict): Validated data
            
        Returns:
            Initiative: Created initiative instance
        """
        team_member_ids = validated_data.pop('team_member_ids', [])
        student_ids = validated_data.pop('student_ids', [])
        partnership_ids = validated_data.pop('partnership_ids', [])
        demanding_partner_id = validated_data.pop('demanding_partner_id', None)
        
        # Set demanding_partner if provided
        if demanding_partner_id is not None:
            validated_data['demanding_partner'] = demanding_partner_id
        
        initiative = Initiative.objects.create(**validated_data)
        
        if team_member_ids:
            initiative.team_members.set(team_member_ids)
        
        if student_ids:
            initiative.students.set(student_ids)
        
        if partnership_ids:
            initiative.partnerships.set(partnership_ids)
        
        return initiative
    
    def update(self, instance, validated_data):
        """
        Update an existing Initiative instance with team members, students, and partnerships.
        
        Args:
            instance (Initiative): Initiative instance to update
            validated_data (dict): Validated data
            
        Returns:
            Initiative: Updated initiative instance
        """
        team_member_ids = validated_data.pop('team_member_ids', None)
        student_ids = validated_data.pop('student_ids', None)
        partnership_ids = validated_data.pop('partnership_ids', None)
        demanding_partner_id = validated_data.pop('demanding_partner_id', None)
        
        # Update demanding_partner if provided
        if 'demanding_partner_id' in self.initial_data:
            instance.demanding_partner = demanding_partner_id
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update team members if provided
        if team_member_ids is not None:
            instance.team_members.set(team_member_ids)
        
        # Update students if provided
        if student_ids is not None:
            instance.students.set(student_ids)
        
        # Update partnerships if provided
        if partnership_ids is not None:
            instance.partnerships.set(partnership_ids)
        
        return instance