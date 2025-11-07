# openedx_plugin_cms/views/bulk_enrollment.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseEnrollment
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token

from ..forms import BulkEnrollmentForm

User = get_user_model()

@login_required
def bulk_enrollment_view(request):
    if request.method == "POST":
        form = BulkEnrollmentForm(request, request.POST)
        if form.is_valid():
            course_id_strings = form.cleaned_data["course_ids"]
            emails = [e.strip() for e in form.cleaned_data["emails"].splitlines() if e.strip()]

            course_keys = []
            for cid in course_id_strings:
                try:
                    course_keys.append(CourseKey.from_string(cid))
                except Exception:
                    messages.error(request, f"Invalid course ID: {cid}")
                    return HttpResponseRedirect(reverse("openedx_plugin_cms:bulk-enrollment"))

            enrolled_count = 0
            errors = []

            for email in emails:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    errors.append(f"User with email `{email}` not found.")
                    continue

                for course_key in course_keys:
                    try:
                        CourseEnrollment.enroll(user, course_key, mode="honor", check_access=False)
                        enrolled_count += 1
                    except Exception as exc:
                        errors.append(f"Failed to enroll {email} in {course_key}: {str(exc)}")

            if enrolled_count:
                messages.success(request, f"Successfully created {enrolled_count} enrollment(s).")
            for err in errors:
                messages.error(request, err)

            return HttpResponseRedirect(reverse("openedx_plugin_cms:bulk_enrollment"))
    else:
        form = BulkEnrollmentForm(request)

    return render(request, "openedx_plugin_cms/bulk_enrollment.html", {"form": form, "csrf_token": get_token(request)})