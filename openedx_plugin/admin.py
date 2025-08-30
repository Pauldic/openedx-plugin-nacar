# coding=utf-8
"""
written by:     Paul Okeke
                https://pauldiconline.com

date:           dec-2022

usage:          register the custom Django models in LMS Django Admin
"""

from django.urls import path
from django.shortcuts import redirect
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from common.djangoapps.student.admin import UserAdmin as OpenEdxUserAdmin
from common.djangoapps.student.views import compose_and_send_activation_email

from .models import Configuration, Locale, MarketingSites


User = get_user_model()  # pylint:disable=invalid-name


class MarketingSitesAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MarketingSites._meta.get_fields()]


class LocaleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Locale._meta.get_fields()]


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Configuration._meta.get_fields()]


class CustomUserAdmin(OpenEdxUserAdmin):
    actions = ['bulk_resend_activation']
    # list_display = OpenEdxUserAdmin.list_display + ('resend_activation_button',)
    
    # Add a row-level button
    # def resend_activation_button(self, obj):
    #     return "Activated" if obj.is_active else mark_safe(f'<a class="button" href="/admin/resend-activation/{obj.pk}/">Resend Activation</a>')
    # resend_activation_button.short_description = 'Activation'
    # resend_activation_button.allow_tags = True  # required for raw HTML links

    # Register custom admin view
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('resend-activation/<int:user_id>/', self.admin_site.admin_view(self.resend_activation)),
        ]
        return custom_urls + urls

    # Action to perform when button clicked
    def resend_activation(self, request, user_id):
        user = User.objects.get(pk=user_id)
        try:
            if not user.is_active:
                compose_and_send_activation_email(user, user.profile)
                self.message_user(request, f"Activation email sent to {user.email}", messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Failed to send activation email: {e}", messages.ERROR)
        return redirect(request.META.get('HTTP_REFERER'))

    def bulk_resend_activation(self, request, queryset):
        """
            Bulk action to resend activation emails to selected users.
        """
        sent_count = 0
        skipped_count = 0
        failed_count = 0

        for user in queryset:
            try:
                if not user.is_active:
                    compose_and_send_activation_email(user, user.profile)
                    sent_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                failed_count += 1
                self.message_user(
                    request,
                    f"Failed to send to {user.email}: {e}",
                    level=messages.ERROR,
                )

        self.message_user(
            request,
            f"Activation emails sent: {sent_count}, skipped: {skipped_count}, failed: {failed_count}",
            level=messages.INFO,
        )

    bulk_resend_activation.short_description = "Resend activation email to Users"
    

admin.site.register(MarketingSites, MarketingSitesAdmin)
admin.site.register(Locale, LocaleAdmin)
admin.site.register(Configuration, ConfigurationAdmin)

try:
    admin.site.unregister(User)
except NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
