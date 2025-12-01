from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer class that includes common fields and functionality.
    """
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        abstract = True


from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'permissions']
        read_only_fields = fields

    def get_permissions(self, obj):
        if obj.is_superuser:
            return ['*']
        return list(obj.get_all_permissions())