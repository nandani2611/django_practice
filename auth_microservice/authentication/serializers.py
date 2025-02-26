from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone_number', 'role']

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.generate_otp()
        return user

class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError('User not found')
        
        # Generate and send OTP
        user.generate_otp()
        return {'message': 'OTP sent to email'}

class OTPLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        user = User.objects.filter(email=data['email'], otp=data['otp']).first()
        if not user:
            raise serializers.ValidationError('Invalid OTP')

        # Clear OTP after successful login
        user.otp = None
        user.save()

        return {'tokens': user.get_tokens()}

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        user = User.objects.filter(email=data['email']).first()
        if not user:
            raise serializers.ValidationError('User not found')
        user.generate_otp()
        return data

class PasswordUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = User.objects.filter(email=data['email'], otp=data['otp']).first()
        if not user:
            raise serializers.ValidationError('Invalid OTP')
        user.set_password(data['new_password'])
        user.otp = None
        user.save()
        return data