from django.urls import path, re_path
from .views import ValidatePhone, ValidateOTP, LoginAPI, Register
from knox import views as knox_views


app_name = 'accounts'
urlpatterns = [
    path('validate-phone/', ValidatePhone.as_view(), name='validate-phone'),
    path('validate-otp/', ValidateOTP.as_view(), name='validate-otp'),
    path('register/', Register.as_view(), name='register'),
    path('login/', LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout')
]
