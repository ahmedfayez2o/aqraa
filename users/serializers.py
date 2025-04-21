from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    current_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                 'profile_picture', 'bio', 'phone_number', 'birth_date', 
                 'favorite_genres', 'notification_preferences', 'last_active', 
                 'is_verified', 'password', 'confirm_password', 'current_password',
                 'date_joined']
        read_only_fields = ['date_joined', 'last_active', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def validate(self, data):
        # Validate password for new users
        if self.instance is None and 'password' in data:
            if 'confirm_password' not in data:
                raise serializers.ValidationError({"confirm_password": "Please confirm your password"})
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"password": "Passwords do not match"})
            validate_password(data['password'])

        # Validate password change for existing users
        elif self.instance and 'password' in data:
            if 'current_password' not in data:
                raise serializers.ValidationError({"current_password": "Current password is required"})
            if 'confirm_password' not in data:
                raise serializers.ValidationError({"confirm_password": "Please confirm your new password"})
            if not self.instance.check_password(data['current_password']):
                raise serializers.ValidationError({"current_password": "Current password is incorrect"})
            if data['password'] != data['confirm_password']:
                raise serializers.ValidationError({"password": "Passwords do not match"})
            validate_password(data['password'])

        # Validate phone number format
        if 'phone_number' in data:
            phone = ''.join(filter(str.isdigit, data['phone_number']))
            if len(phone) < 10:
                raise serializers.ValidationError({"phone_number": "Phone number must have at least 10 digits"})

        # Validate notification preferences structure
        if 'notification_preferences' in data:
            valid_keys = {'email', 'push', 'sms'}
            prefs = data['notification_preferences']
            if not isinstance(prefs, dict):
                raise serializers.ValidationError({"notification_preferences": "Must be a dictionary"})
            if not all(k in valid_keys for k in prefs.keys()):
                raise serializers.ValidationError({"notification_preferences": f"Valid keys are: {valid_keys}"})

        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data.pop('current_password', None)
        password = validated_data.pop('password', None)
        
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        validated_data.pop('current_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance