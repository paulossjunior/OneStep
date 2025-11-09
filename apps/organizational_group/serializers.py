from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Campus, OrganizationalGroup, OrganizationalGroupLeadership, KnowledgeArea
from apps.people.serializers import PersonSerializer
from apps.initiatives.serializers import InitiativeSerializer


class KnowledgeAreaSerializer(serializers.ModelSerializer):
    """
    Serializer for KnowledgeArea model.
    
    Provides serialization for KnowledgeArea CRUD operations with proper validation
    and additional computed fields for API responses.
    """
    
    group_count = serializers.SerializerMethodField(
        help_text="Number of organizational groups in this knowledge area"
    )
    
    class Meta:
        model = KnowledgeArea
        fields = [
            'id',
            'name',
            'description',
            'group_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'group_count'
        ]
    
    def get_group_count(self, obj):
        """
        Get the count of organizational groups in this knowledge area.
        
        Args:
            obj (KnowledgeArea): KnowledgeArea instance
            
        Returns:
            int: Number of organizational groups in this knowledge area
        """
        # Use annotated count if available, otherwise call method
        if hasattr(obj, 'annotated_group_count'):
            return obj.annotated_group_count
        return obj.group_count()
    
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
            raise serializers.ValidationError("Knowledge area name cannot be empty.")
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
        instance = self.instance or KnowledgeArea()
        
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


class CampusSerializer(serializers.ModelSerializer):
    """
    Serializer for Campus model.
    
    Provides serialization for Campus CRUD operations with proper validation
    and additional computed fields for API responses.
    """
    
    group_count = serializers.SerializerMethodField(
        help_text="Number of organizational groups on this campus"
    )
    
    class Meta:
        model = Campus
        fields = [
            'id',
            'name',
            'code',
            'location',
            'group_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'group_count'
        ]
    
    def get_group_count(self, obj):
        """
        Get the count of organizational groups on this campus.
        
        Args:
            obj (Campus): Campus instance
            
        Returns:
            int: Number of organizational groups on this campus
        """
        return obj.group_count()
    
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
            raise serializers.ValidationError("Campus name cannot be empty.")
        return value.strip()
    
    def validate_code(self, value):
        """
        Validate code field and auto-uppercase.
        
        Args:
            value (str): Code value to validate
            
        Returns:
            str: Validated, cleaned, and uppercased code
            
        Raises:
            serializers.ValidationError: If code is empty after stripping
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Campus code cannot be empty.")
        return value.strip().upper()


class OrganizationalGroupLeadershipSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationalGroupLeadership model with person details.
    
    Provides serialization for leadership relationships including
    historical tracking and person information.
    """
    
    # Read-only fields for person details
    person_name = serializers.CharField(
        source='person.name',
        read_only=True,
        help_text="Full name of the person who is a leader"
    )
    person_email = serializers.EmailField(
        source='person.email',
        read_only=True,
        help_text="Email address of the person who is a leader"
    )
    
    # Nested person serialization for detailed views
    person_details = PersonSerializer(
        source='person',
        read_only=True,
        help_text="Complete information about the person who is a leader"
    )
    
    class Meta:
        model = OrganizationalGroupLeadership
        fields = [
            'id',
            'group',
            'person',
            'person_name',
            'person_email',
            'person_details',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'person_name',
            'person_email',
            'person_details'
        ]
    
    def validate_end_date(self, value):
        """
        Validate end_date field.
        
        Args:
            value (date): End date value to validate
            
        Returns:
            date: Validated end date
            
        Raises:
            serializers.ValidationError: If end_date is before start_date
        """
        start_date = self.initial_data.get('start_date')
        if self.instance:
            start_date = start_date or self.instance.start_date
        
        if value and start_date:
            if value < start_date:
                raise serializers.ValidationError(
                    "End date must be after or equal to start date."
                )
        
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
        # Validate that if end_date is set, is_active should be False
        end_date = data.get('end_date')
        is_active = data.get('is_active', True)
        
        if end_date and is_active:
            raise serializers.ValidationError({
                'is_active': 'Leadership with an end date should not be marked as active.'
            })
        
        # Create a temporary instance for model validation
        instance = self.instance or OrganizationalGroupLeadership()
        
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


class OrganizationalGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationalGroup model with nested relationships.
    
    Provides serialization for OrganizationalGroup CRUD operations with proper validation
    and additional computed fields for API responses.
    """
    
    # Read-only computed fields
    type_display = serializers.CharField(
        source='get_type_display',
        read_only=True,
        help_text="Human-readable display name for group type"
    )
    leader_count = serializers.SerializerMethodField(
        help_text="Number of current leaders"
    )
    member_count = serializers.SerializerMethodField(
        help_text="Number of members"
    )
    initiative_count = serializers.SerializerMethodField(
        help_text="Number of associated initiatives"
    )
    
    # Nested campus data for read operations
    campus = CampusSerializer(
        read_only=True,
        help_text="Campus information with complete details"
    )
    
    # Nested knowledge area data for read operations
    knowledge_area = KnowledgeAreaSerializer(
        read_only=True,
        help_text="Knowledge area information with complete details"
    )
    
    # Nested serialization for related objects (read-only)
    current_leaders = serializers.SerializerMethodField(
        help_text="List of current leaders with their details"
    )
    members = PersonSerializer(
        many=True,
        read_only=True,
        help_text="List of all members with their complete information"
    )
    initiatives = InitiativeSerializer(
        many=True,
        read_only=True,
        help_text="List of associated initiatives with their complete information"
    )
    
    class Meta:
        model = OrganizationalGroup
        fields = [
            'id',
            'name',
            'short_name',
            'url',
            'type',
            'type_display',
            'knowledge_area',
            'campus',
            'current_leaders',
            'members',
            'initiatives',
            'leader_count',
            'member_count',
            'initiative_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'type_display',
            'campus',
            'knowledge_area',
            'current_leaders',
            'members',
            'initiatives',
            'leader_count',
            'member_count',
            'initiative_count'
        ]
    
    def get_leader_count(self, obj):
        """
        Get the count of current leaders.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            int: Number of current leaders
        """
        return obj.leader_count()
    
    def get_member_count(self, obj):
        """
        Get the count of members.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            int: Number of members
        """
        return obj.member_count()
    
    def get_initiative_count(self, obj):
        """
        Get the count of associated initiatives.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            int: Number of associated initiatives
        """
        return obj.initiative_count()
    
    def get_current_leaders(self, obj):
        """
        Get current leaders with their leadership details.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            list: List of current leaders with leadership information
        """
        # Get active leadership relationships
        active_leaderships = OrganizationalGroupLeadership.objects.filter(
            group=obj,
            is_active=True
        ).select_related('person')
        
        return OrganizationalGroupLeadershipSerializer(
            active_leaderships,
            many=True,
            context=self.context
        ).data
    
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
            raise serializers.ValidationError("Group name cannot be empty.")
        return value.strip()
    
    def validate_short_name(self, value):
        """
        Validate short_name field.
        
        Args:
            value (str): Short name value to validate
            
        Returns:
            str: Validated and cleaned short name
            
        Raises:
            serializers.ValidationError: If short_name is empty after stripping
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Short name cannot be empty.")
        return value.strip()
    
    def validate_url(self, value):
        """
        Validate URL field.
        
        Args:
            value (str): URL value to validate
            
        Returns:
            str: Validated URL
            
        Raises:
            serializers.ValidationError: If URL format is invalid
        """
        if value and value.strip():
            # DRF's URLField already validates format, but we can add custom logic here
            return value.strip()
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
        # Note: Unique constraint validation for short_name + campus_id
        # is handled by the database and model's clean method
        
        # Create a temporary instance for model validation
        instance = self.instance or OrganizationalGroup()
        
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


class OrganizationalGroupDetailSerializer(OrganizationalGroupSerializer):
    """
    Detailed serializer for OrganizationalGroup model with full nested related data.
    
    Extends OrganizationalGroupSerializer to include complete related object information
    for detailed views, including leadership history.
    """
    
    # Leadership history (all leaders, not just current)
    leadership_history = serializers.SerializerMethodField(
        help_text="Complete leadership history including past leaders"
    )
    
    class Meta(OrganizationalGroupSerializer.Meta):
        fields = OrganizationalGroupSerializer.Meta.fields + [
            'leadership_history'
        ]
    
    def get_leadership_history(self, obj):
        """
        Get complete leadership history.
        
        Args:
            obj (OrganizationalGroup): OrganizationalGroup instance
            
        Returns:
            list: List of all leadership relationships (current and historical)
        """
        # Get all leadership relationships ordered by start_date
        all_leaderships = OrganizationalGroupLeadership.objects.filter(
            group=obj
        ).select_related('person').order_by('-start_date')
        
        return OrganizationalGroupLeadershipSerializer(
            all_leaderships,
            many=True,
            context=self.context
        ).data


class OrganizationalGroupCreateUpdateSerializer(OrganizationalGroupSerializer):
    """
    Serializer for OrganizationalGroup creation and updates with write operations.
    
    Handles member and initiative assignments that require special handling,
    and campus_id for write operations.
    """
    
    # Write-only field for campus foreign key
    campus_id = serializers.IntegerField(
        write_only=True,
        required=True,
        help_text="ID of the campus where this group is located"
    )
    
    # Write-only field for knowledge area foreign key
    knowledge_area_id = serializers.IntegerField(
        write_only=True,
        required=True,
        help_text="ID of the knowledge area for this group"
    )
    
    # Allow writing to members and initiatives fields
    member_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of person IDs to assign as members"
    )
    initiative_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of initiative IDs to associate with the group"
    )
    
    class Meta(OrganizationalGroupSerializer.Meta):
        fields = OrganizationalGroupSerializer.Meta.fields + ['campus_id', 'knowledge_area_id', 'member_ids', 'initiative_ids']
    
    def validate_campus_id(self, value):
        """
        Validate campus_id field.
        
        Args:
            value (int): Campus ID to validate
            
        Returns:
            int: Validated campus ID
            
        Raises:
            serializers.ValidationError: If campus does not exist
        """
        try:
            Campus.objects.get(pk=value)
        except Campus.DoesNotExist:
            raise serializers.ValidationError(f"Campus with ID {value} does not exist.")
        return value
    
    def validate_knowledge_area_id(self, value):
        """
        Validate knowledge_area_id field.
        
        Args:
            value (int): Knowledge area ID to validate
            
        Returns:
            int: Validated knowledge area ID
            
        Raises:
            serializers.ValidationError: If knowledge area does not exist
        """
        try:
            KnowledgeArea.objects.get(pk=value)
        except KnowledgeArea.DoesNotExist:
            raise serializers.ValidationError(f"Knowledge area with ID {value} does not exist.")
        return value
    
    def validate(self, data):
        """
        Object-level validation including unique constraint for short_name + campus_id.
        
        Args:
            data (dict): Validated data dictionary
            
        Returns:
            dict: Validated data
            
        Raises:
            serializers.ValidationError: If validation fails
        """
        # Validate unique constraint for short_name + campus_id
        short_name = data.get('short_name')
        campus_id = data.get('campus_id')
        
        if short_name and campus_id:
            existing_group = OrganizationalGroup.objects.filter(
                short_name__iexact=short_name,
                campus_id=campus_id
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_group = existing_group.exclude(pk=self.instance.pk)
            
            if existing_group.exists():
                raise serializers.ValidationError({
                    'short_name': f'A group with short name "{short_name}" already exists on this campus.'
                })
        
        # Call parent validation
        return super().validate(data)
    
    def create(self, validated_data):
        """
        Create a new OrganizationalGroup instance with members and initiatives.
        
        Args:
            validated_data (dict): Validated data
            
        Returns:
            OrganizationalGroup: Created group instance
        """
        member_ids = validated_data.pop('member_ids', [])
        initiative_ids = validated_data.pop('initiative_ids', [])
        
        group = OrganizationalGroup.objects.create(**validated_data)
        
        if member_ids:
            group.members.set(member_ids)
        
        if initiative_ids:
            group.initiatives.set(initiative_ids)
        
        return group
    
    def update(self, instance, validated_data):
        """
        Update an existing OrganizationalGroup instance with members and initiatives.
        
        Args:
            instance (OrganizationalGroup): OrganizationalGroup instance to update
            validated_data (dict): Validated data
            
        Returns:
            OrganizationalGroup: Updated group instance
        """
        member_ids = validated_data.pop('member_ids', None)
        initiative_ids = validated_data.pop('initiative_ids', None)
        
        # Update regular fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update members if provided
        if member_ids is not None:
            instance.members.set(member_ids)
        
        # Update initiatives if provided
        if initiative_ids is not None:
            instance.initiatives.set(initiative_ids)
        
        return instance
