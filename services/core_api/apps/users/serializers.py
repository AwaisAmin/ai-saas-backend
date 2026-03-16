from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta: 
        model = User
        fields = ('email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs: dict) -> dict:
        if attrs['password'] != attrs['password2']:
            raise serializers.Validation({'password': 'Passwords do no match'})
        return attrs
    
    def create(self, validated_data: dict) -> User:
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
    
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'is_verified', 'created_at')
        read_only_fields = ('id', 'email', 'is_verified', 'created_at')