from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

from .models import  PhoneOTP
import time

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','phone_number', 'password', 'display_name')
        extra_kwargs = {'password':{'write_only':True}}

    def validate(self, validated_data):
        user = User.objects.create_user(**validated_data)
        print(user)
        return user

    # def create(self, validated_data):
    #     user = User.objects.create_user(validated_data
    #     ['phone_number'], validated_data['password'])
        
    #     return user

class CreateUserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()
    class Meta:
        model = User
        fields = 'phone_number', 'password'
        extra_kwargs = {'password':{'write_only':True}}

    def create(self, validated_data):
        print(validated_data)
        user = User.object.create_user(**validated_data)
        print(user)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['groups', 'password', 'user_permissions']


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(
        style={'input-type':'password'}, trim_whitespace=False
    )

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            if User.objects.filter(phone_number=phone_number).exists():
                user = authenticate(request=self.context['request'], phone_number=phone_number, password=password)
            else:
                msg = {
                    'status': False,
                    'detail': 'Phone number and password not match',
                }

                raise serializers.ValidationError(msg, code='authorization')

            if not user:
                msg = {
                    'status': False,
                    'detail': 'Phone number and password not match',
                }
                raise serializers.ValidationError(msg, code='authorization')

        else:
            msg = {
                'status': False,
                'detail': 'Phone number and password not found',
            }
            raise serializers.ValidationError(msg, code='authorization')

        data['user'] = user
        return data
        

class ValidateOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    otp = serializers.CharField()

    def validate(self, attrs):
        pass
