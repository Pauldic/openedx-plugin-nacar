# coding=utf-8
"""
written by:     Paul Okeke
                https://pauldiconline.com

date:           dec-2022

usage:          register the custom Django models in LMS Django Admin
"""

from django import forms
from django.urls import path
from django.shortcuts import redirect, render
from django.contrib import admin, messages
from django.utils.safestring import mark_safe
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import NotRegistered
from common.djangoapps.student.admin import UserAdmin as OpenEdxUserAdmin
from common.djangoapps.student.views import compose_and_send_activation_email

# Course & enrollment imports
from openedx.core.djangoapps.enrollments.data import create_course_enrollment
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.content.course_overviews.admin import CourseOverviewAdmin as OpenEdxCourseOverviewAdmin

from .models import Configuration, Locale, MarketingSites


User = get_user_model()  # pylint:disable=invalid-name


class MarketingSitesAdmin(admin.ModelAdmin):
    list_display = [f.name for f in MarketingSites._meta.get_fields()]


class LocaleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Locale._meta.get_fields()]


class ConfigurationAdmin(admin.ModelAdmin):
    list_display = [f.name for f in Configuration._meta.get_fields()]


class CustomUserAdmin(OpenEdxUserAdmin):
    actions = ['bulk_manual_activation']
    # actions = ['bulk_resend_activation']
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
    

    def bulk_manual_activation(self, request, queryset):
        """
            Bulk action to manually activate emails of selected users.
        """
        
        activated_count = queryset.filter(is_active=False).update(is_active=True)
        
        self.message_user(
            request,
            f"{activated_count} users activated successfully",
            level=messages.INFO,
        )

    bulk_manual_activation.short_description = "Manually activate Users' emails"
    
# ---------------------------------------------------------------------
# Course-side bulk enroll (select courses -> enroll user(s) by email)
# ---------------------------------------------------------------------

class EnrollUsersForm(forms.Form):
    emails = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "placeholder": "user1@example.com\nuser2@example.com\n(one email per line)",
            }
        ),
        help_text="Enter one email per line (users must already exist).",
    )


class CustomCourseOverviewAdmin(OpenEdxCourseOverviewAdmin):
    """
        Adds an action to CourseOverview admin: "Enroll users into selected courses".
        When chosen, you are redirected to a simple form to paste emails (one per line).
        Those users will be enrolled into the selected courses.
    """
    list_display = [
        'id',
        'display_name',
        'org',
        'version',
        'enrollment_start',
        'enrollment_end',
        'created',
        'modified',
    ]
    # search_fields = ['id', 'display_name']
    actions = ["enroll_selected_courses"]

    # Add the custom admin view URL (this will be under the CourseOverview admin path)
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("bulk-enroll/", self.admin_site.admin_view(self.bulk_enroll_view), name="course_bulk_enroll"),
        ]
        return custom_urls + urls

    def enroll_selected_courses(self, request, queryset):
        """
            Action: redirect to the bulk-enroll admin view with selected course ids in querystring.
            NOTE: the redirect path assumes the admin URL layout /admin/content/course_overviews/courseoverview/bulk-enroll/
            which is standard for CourseOverview in Open edX.
        """
        ids = list(queryset.values_list("id", flat=True))
        if not ids:
            self.message_user(request, "No courses selected.", level=messages.WARNING)
            return
        # Join ids into querystring param "ids=..."
        qs = "&".join([f"ids={i}" for i in ids])
        return redirect(f"/admin/content/course_overviews/courseoverview/bulk-enroll/?{qs}")

    enroll_selected_courses.short_description = "Enroll users into selected courses"

    def bulk_enroll_view(self, request):
        """
            The admin view that shows the form. Expects query param ids=<course_id>&ids=<course_id>...
        """
        course_ids = request.GET.getlist("ids")
        courses = CourseOverview.objects.filter(id__in=course_ids)

        if request.method == "POST":
            form = EnrollUsersForm(request.POST)
            if form.is_valid():
                emails = [e.strip() for e in form.cleaned_data["emails"].splitlines() if e.strip()]
                enrolled_count = 0
                email_count = 0
                errors = []

                for email in emails:
                    try:
                        user = User.objects.get(email=email)
                    except User.DoesNotExist:
                        errors.append(f"User with email `{email}` not found; skipping.")
                        continue

                    email_count += 1
                    for course in courses:
                        cid = course.id  # course-v1:Org+Code+Run
                        try:
                            # create_course_enrollment accepts username (or user id in some setups),
                            # here we use username which is safe for typical Open edX installs.
                            create_course_enrollment(
                                user.username,
                                cid,
                                mode="honor",
                                is_active=True,
                                force_enrollment=True,
                            )
                            enrolled_count += 1
                        except Exception as exc:
                            errors.append(f"Failed to enroll {email} in {cid}: {exc}")

                if enrolled_count:
                    self.message_user(
                        request,
                        f"Successfully created {enrolled_count} enrollment(s) for {email_count} users.",
                        level=messages.SUCCESS,
                    )
                for err in errors:
                    self.message_user(request, err, level=messages.ERROR)

                # go back to CourseOverview changelist
                return redirect("/admin/content/course_overviews/courseoverview/")
        else:
            form = EnrollUsersForm()

        context = dict(
            self.admin_site.each_context(request),
            title="Enroll users into selected courses",
            form=form,
            courses=courses,
        )
        return render(request, "openedx_plugin/course_bulk_enroll.html", context)


# ---------------------------------------------------------------------
# Register other models & user admin (keep your existing registrations)
# ---------------------------------------------------------------------

admin.site.register(MarketingSites, MarketingSitesAdmin)
admin.site.register(Locale, LocaleAdmin)
admin.site.register(Configuration, ConfigurationAdmin)

try:
    admin.site.unregister(User)
    admin.site.unregister(CourseOverview)
except NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)
admin.site.register(CourseOverview, CustomCourseOverviewAdmin)
