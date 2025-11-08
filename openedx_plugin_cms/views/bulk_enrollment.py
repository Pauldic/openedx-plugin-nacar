# openedx_plugin_cms/views/bulk_enrollment.py
# from django.contrib import messages
from openedx.core.djangoapps.util.user_messages import PageLevelMessages
from openedx.core.djangolib.markup import HTML, Text
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.edxmako.shortcuts import render_to_response
from cms.djangoapps.contentstore.views.course import get_courses_accessible_to_user
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token

import logging

log = logging.getLogger(__name__)

@login_required
@ensure_csrf_cookie
def bulk_enrollment_view(request):
    courses, _ = get_courses_accessible_to_user(request)
    
    if request.method == "POST":
        # Parse selected course IDs and emails from request.POST
        selected_course_ids = request.POST.getlist("course_ids")
        emails_raw = request.POST.get("emails", "")
        emails = [e.strip() for e in emails_raw.splitlines() if e.strip()]

        User = get_user_model()
        users = set()
        enrolled_count = 0
        errors = []

        # Validation check first
        if len(emails) == 0 or len(selected_course_ids) == 0:
            PageLevelMessages.register_error_message(
                request,
                Text("At least 1 email and 1 course are required")
            )
            # Re-render the form with current data instead of redirecting
            context = {
                "courses": courses,
                "csrf_token": get_token(request),
                "pre_selected_course_ids": selected_course_ids,  # For repopulating checkboxes
                "pre_entered_emails": emails_raw,  # For repopulating textarea
            }
            return render_to_response("openedx_plugin_cms/bulk_enrollment.html", context, request)

        for email in emails:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                errors.append(f"User with email `{email}` not found.")
                log.info(f">>> User with email `{email}` not found.")
                continue

            for cid in selected_course_ids:
                try:
                    course_key = CourseKey.from_string(cid)
                    CourseEnrollment.enroll(user, course_key, mode="honor", check_access=False)
                    enrolled_count += 1
                    users.add(email)
                except Exception as exc:
                    log.error(f">>> Failed to enroll {email} in {cid}: {exc}")
                    errors.append(f"Failed to enroll {email} in {cid}")

        if enrolled_count:
            PageLevelMessages.register_success_message(
                request, 
                Text(f"Total of {enrolled_count} enrollments successful for {users} users")
            )
        for err in errors:
            PageLevelMessages.register_error_message(
                request,
                Text(err)
            )


        log.info(f">>> The Redirect link: {redirect('openedx_plugin_cms:bulk-enrollment')}")
        return redirect("openedx_plugin_cms:bulk-enrollment")

    # For GET: just pass courses
    context = {
        "courses": courses,
        "csrf_token": get_token(request)
    }
    return render_to_response("openedx_plugin_cms/bulk_enrollment.html", context, request)
