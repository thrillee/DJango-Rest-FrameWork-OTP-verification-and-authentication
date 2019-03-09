from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import UserChangeForm, UserCreationForm
from .models import User, PhoneOTP

from django.utils.translation import gettext_lazy as _

admin.site.site_header = 'WORKHUNT Administration'
admin.site.site_title = 'WORKHUNT'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        (_('Personal info'), {
         'fields': ('display_name', 'first_name', 'last_name', 'email')}),

        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )

    list_display = ('phone_number', 'display_name', 'email', 'first_name',
                    'last_name', 'is_active')
    list_filter = ('is_active',)
    list_display_link = ('phone_number', 'display_name',
                         'first_name', 'last_name', 'email')
    search_fields = ('display_name', 'first_name',
                     'last_name', 'email', 'phone_number')
    ordering = ('phone_number', 'display_name',
                'first_name', 'last_name', 'email')

    filter_horizontal = ()

    class Meta:
        model = User

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    class Meta:
        model = PhoneOTP

    list_display = ('phone_number', 'otp', 'initial', 'elapse', 'validated')
    list_filter = ('phone_number', 'validated')
    list_display_link = ('phone_number', 'validated')
    search_fields = ('otp', 'phone_number')
    ordering = ('phone_number', 'otp', 'initial', 'elapse', 'validated')
