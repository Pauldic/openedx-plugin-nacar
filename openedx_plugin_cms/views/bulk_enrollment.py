# openedx_plugin_cms/views/bulk_enrollment.py
# from django.contrib import messages
from openedx.core.djangoapps.util.user_messages import PageLevelMessages
from openedx.core.djangolib.markup import HTML, Text
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.shortcuts import render, redirect
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.management import call_command
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.edxmako.shortcuts import render_to_response
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from cms.djangoapps.contentstore.views.course import get_courses_accessible_to_user
from django.contrib.auth import get_user_model
from django.middleware.csrf import get_token
from django.db import transaction # Optional: for atomicity if needed



import logging



log = logging.getLogger(__name__)

def get_course_name(cid):
    try:
        course = CourseOverview.get_from_id(CourseKey.from_string(cid))
        return course.display_name_with_default
    except Exception:
        return cid  # fallback to ID if name lookup fails


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
        users_processed = {}
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

        newly_enrolled_user_ids = []
        for email in set(emails):
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                errors.append(f"User with email `{email}` not found.")
                log.error(f">>> User with email `{email}` not found.")
                continue

            users_processed[email] = {"skipped": [], "enrolled": []}
            for cid in selected_course_ids:
                try:
                    course_key = CourseKey.from_string(cid)
                    
                    # --- CHECK IF ALREADY ENROLLED ---
                    if CourseEnrollment.is_enrolled(user, course_key):
                        log.info(f">>> User {email} is already enrolled in {cid}")
                        users_processed[email]["skipped"].append(cid)
                        continue # Skip enrollment attempt
                    
                    # --- ATTEMPT NEW ENROLLMENT ---
                    CourseEnrollment.enroll(user, course_key, mode="honor", check_access=False)
                    users_processed[email]["enrolled"].append(cid)
                    newly_enrolled_user_ids.append(user.id)
                    log.info(f">>> Successfully enrolled {email} in {cid}")
                    
                except Exception as exc:
                    log.error(f">>> Failed to enroll {email} in {cid}: {exc}")
                    errors.append(f"Failed to enroll {email} in {cid}")

        # ✅ Send enrollment emails to all newly enrolled users
        if newly_enrolled_user_ids:
            try:
                # Deduplicate user IDs
                unique_user_ids = list(set(newly_enrolled_user_ids))
                
                # Call the built-in Open edX command
                call_command(
                    'update_course_enrollment_email',
                    '--course-id', ','.join(selected_course_ids),  # Support multiple courses
                    '--subject-line', 'Welcome to Your New Course!',
                    '--message-type', 'welcome',
                    '--from-email-name', 'NACAR Learning Team',
                    *unique_user_ids  # Pass each user ID as a separate argument
                )
                log.info(f">>> Sent welcome emails to {len(unique_user_ids)} users for {len(selected_course_ids)} courses.")
            except Exception as e:
                log.error(f">>> Failed to send emails: {e}")
                PageLevelMessages.register_error_message(
                    request,
                    Text("Course enrollments were successful, but failed to send some welcome emails.")
                )

        # --- REPORT RESULTS ---
        if users_processed:
            msg = ""
            for email, v in users_processed.items():
                msg += f"<b>{email}</b>:<ul>"
                if len(v["skipped"]) > 0:
                    msg += " ".join([f'<li>Skipped: <a href="{settings.LMS_ROOT_URL}/courses/{cid}/about" target="_blank">{get_course_name(cid)}</a> <i>(user is already enrolled)</i></li>' for cid in v['skipped']])
                if len(v["enrolled"]) > 0:
                    msg += " ".join([f'<li>Enrolled: <a href="{settings.LMS_ROOT_URL}/courses/{cid}/about" target="_blank">{get_course_name(cid)}</a></li>' for cid in v['enrolled']])
                msg += "</ul>"
            PageLevelMessages.register_success_message(request, HTML(msg))
        for err in errors:
            PageLevelMessages.register_error_message(request, Text(err))

        return redirect("openedx_plugin_cms:bulk-enrollment")
    # For GET: just pass courses
    context = {"courses": courses, "csrf_token": get_token(request)}
    return render_to_response("openedx_plugin_cms/bulk_enrollment.html", context, request)

