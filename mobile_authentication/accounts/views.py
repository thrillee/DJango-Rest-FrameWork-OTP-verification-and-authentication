import random
import time

from django_otp.oath import totp
from django.contrib.auth import login
from django.shortcuts import get_object_or_404
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
from rest_framework.generics import GenericAPIView 
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from accounts.serializers import LoginSerializer

from .models import PhoneOTP, User
from .serializers import CreateUserSerializer, UserSerializer, RegisterSerializer


class ValidatePhone(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if phone_number:
            phone_number = str(phone_number)
            user = User.objects.filter(phone_number__iexact=phone_number)
            if user.exists():
                return Response({
                    'status': False,
                    'detail': 'Phone number Exist'
                })
            else:
                key = send_otp(phone_number)
                print(key)
                if key:
                    old = PhoneOTP.objects.filter(phone_number__iexact=phone_number)
                    if old.exists():
                        old = old.first()
                        now = int(time.time())
                        elapse = old.elapse
                        if now > elapse:
                            return Response({
                                'status': False,
                                'detail': 'OTP has expired'
                            })

                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully'
                        })
                    else:
                        PhoneOTP.objects.create(
                            phone_number=phone_number,
                            otp=key,
                        )
                        return Response({
                            'status': True,
                            'detail': 'OTP sent successfully!'
                        })
                else:
                    return Response({
                        'status': False,
                        'detail': 'Error in sending OTP'
                    })
        else:
            return Response({
                'status': False,
                'detail': 'Provide phone number'
            })


secret_key = b'12345678901234567890'

def send_otp(phone):
    
    if phone:
        return totp(key=secret_key, step=1, digits=6, t0=random.randint(999, 999))
    return False


class ValidateOTP(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', False)
        otp_sent = request.data.get('otp', False)

        if phone_number and otp_sent:
            old = PhoneOTP .objects.filter(phone_number__iexact=phone_number)
            if old.exists():
                old = old.first()
                otp = old.otp
                now = int(time.time())
                elapse = old.elapse
                if now > elapse:
                    if str(otp_sent) == str(otp):
                        old.validated = True
                        old.save()
                        return Response({
                            'status': True,
                            'detail': 'OTP Confirmed'
                        })

                    else:
                        return Response({
                            'status': False,
                            'detail': 'Incorrect OTP'
                        })
                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP has expired'
                    })
        else:
            return Response({
                'status': False,
                'detail': 'Missing phone or otp'
            })
                    

# {"phone_number": 1234567890, "otp": 755224	}

class Register(GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number', False)
        password = request.data.get('password', False)
        
        if phone_number and password:
            old = PhoneOTP.objects.filter(phone_number__iexact=phone_number)
            if old.exists():
                old = old.first()
                validated = old.validated
                if validated:
                    temp_data = {
                        'phone_number': phone_number,
                        'password': password
                    }
                    serializer = self.get_serializer(data=temp_data)
                    serializer.is_valid(raise_exception=True)
                    user = serializer.validated_data
                    return Response({
                        'user': UserSerializer(user, context=self.get_serializer_context()).data,
                        'token': AuthToken.objects.create(user)
                    })

                else:
                    return Response({
                        'status': False,
                        'detail': 'OTP is not verified '
                    })
            else:
                return Response({
                    'status': False,
                    'detail': 'Verify phone number'
                })
        else:
            return Response({
                'status':'False',
                'detail': 'Both phone and password are not sent'
            })


class LoginAPI(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            'user': UserSerializer(user, context=self.get_serializer_context()).data,
            'token': AuthToken.objects.create(user)
        })
