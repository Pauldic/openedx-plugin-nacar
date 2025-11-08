# openedx_plugin_cms/views/bulk_enrollment.py
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
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
def bulk_enrollment_view(request):
    # Get the same course data as Studio home
    courses, _ = get_courses_accessible_to_user(request)
    
    if request.method == "POST":
        # Parse selected course IDs and emails from request.POST
        selected_course_ids = request.POST.getlist("course_ids")
        emails_raw = request.POST.get("emails", "")
        emails = [e.strip() for e in emails_raw.splitlines() if e.strip()]

        User = get_user_model()
        enrolled_count = 0
        errors = []

        log.info(f"Emails: {emails}")
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
                except Exception as exc:
                    log.error(f">>> Failed to enroll {email} in {cid}: {exc}")
                    errors.append(f"Failed to enroll {email} in {cid}")

        if enrolled_count:
            messages.success(request, f"Successfully enrolled {enrolled_count} user(s).")
        for err in errors:
            messages.error(request, err)

        return redirect("openedx_plugin_cms:bulk-enrollment")

    # For GET: just pass courses
    context = {
        "courses": courses,
        "csrf_token": get_token(request),
        "messages": get_messages(request)
    }
    return render_to_response("openedx_plugin_cms/bulk_enrollment.html", context, request)


    # return render(request, "openedx_plugin_cms/bulk_enrollment.html", {"form": form, "csrf_token": get_token(request)})


    # home_context = get_home_context(request)
    # return render_to_response('openedx_plugin_cms/bulk_enrollment.html', home_context)
    
    # return render_to_response('openedx_plugin_cms/bulk_enrollment.html', {"form": form, "csrf_token": get_token(request)})


