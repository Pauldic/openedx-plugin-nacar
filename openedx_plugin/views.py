# openedx_plugin_cms/views/bulk_enrollment.py
from common.djangoapps.edxmako.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.clickjacking import xframe_options_exempt
from opaque_keys.edx.keys import CourseKey
from openedx_filters.learning.filters import InstructorDashboardRenderStarted
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole
from lms.djangoapps.courseware.courses import get_course_by_id, get_studio_url
from lms.djangoapps.grades.api import CourseGradeFactory as LMSCourseGradeFactory
from django.contrib.auth.models import User
from common.djangoapps.student.models import UserProfile

# Import for completion summary calculation
from lms.djangoapps.courseware.courses import get_course_blocks_completion_summary

def getNewVerbiage(mode_name):
    """Converts enrollment mode to a more readable format."""
    if mode_name == "honor":
        return "Learner"
    elif mode_name == "audit":
        return "Auditor"
    return mode_name.title()


@login_required
@xframe_options_exempt
def enrollment_list_view(request, course_id):
    """
    Renders a list of enrolled students for a given course, including grades and progress.
    """
    print(f" >>>>>> >> >>>>>>> Enrollment List for: {course_id}")

    try:
        course_key = CourseKey.from_string(course_id)
    except (ValueError, NameError):  # NameError for cases where InvalidKeyError isn't defined
        raise Http404("Invalid course ID")

    # Check permissions: only instructors/staff
    if not (
        CourseInstructorRole(course_key).has_user(request.user) or
        CourseStaffRole(course_key).has_user(request.user)
    ):
        raise PermissionDenied

    course = get_course_by_id(course_key)

    enrollments = CourseEnrollment.objects.filter(
        course_id=course_key,
        is_active=True
    ).select_related('user__profile').order_by('user__username')

    students = []
    for enrollment in enrollments:
        user = enrollment.user

        # Get full name from profile, fallback to first/last, then username
        full_name = ""
        if hasattr(user, 'profile') and user.profile.name:
            full_name = user.profile.name.strip()
        if not full_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
        if not full_name:
            full_name = user.username

        # --- GET OVERALL COURSE GRADE PERCENTAGE (graded assignments only) ---
        grade_percent = None
        try:
            grade_record = LMSCourseGradeFactory().read(user, course_key)
            if grade_record:
                grade_percent = round(grade_record.percent * 100, 1)
        except Exception as e:
            print(f"Error fetching grade for {user.email} in {course_id}: {e}")

        # --- CALCULATE PROGRESS PERCENTAGE (all completed units) ---
        # This matches the calculation used in the Progress tab
        progress_percent = 0.0
        try:
            # Get the completion summary which contains counts of complete/incomplete/locked units
            completion_summary = get_course_blocks_completion_summary(course_key, user)
            
            if completion_summary:
                total_units = (
                    completion_summary.get('complete_count', 0) +
                    completion_summary.get('incomplete_count', 0) +
                    completion_summary.get('locked_count', 0)
                )
                
                # Avoid division by zero
                if total_units > 0:
                    progress_percent = round(
                        (completion_summary.get('complete_count', 0) / total_units) * 100,
                        1
                    )
                else:
                    progress_percent = 0.0
        except Exception as e:
            print(f"Error calculating progress for {user.email} in {course_id}: {e}")
            # Fall back to grade_percent if progress calculation fails
            progress_percent = grade_percent if grade_percent is not None else 0.0

        students.append({
            'user_id': user.id,
            'username': user.username.lower(),
            'full_name': full_name.title(),
            'email': user.email.lower(),
            'mode': getNewVerbiage(enrollment.mode),
            'grade': grade_percent,
            'progress': int(round(progress_percent, 0)),  # Now calculated properly based on unit completion
            'enrollment_date': enrollment.created,
        })

    context = {
        'course': course,
        'students': students,
        'course_id': str(course_key),
        'studio_url': get_studio_url(course, 'course'),
    }
    instructor_template = 'openedx_plugin/enrollment_list.html'

    try:
        context, instructor_template = InstructorDashboardRenderStarted.run_filter(
            context=context, template_name=instructor_template)
    except InstructorDashboardRenderStarted.RenderInvalidDashboard as exc:
        response = render_to_response(exc.instructor_template, exc.template_context)
    except InstructorDashboardRenderStarted.RedirectToPage as exc:
        response = HttpResponseRedirect(exc.redirect_to)
    except InstructorDashboardRenderStarted.RenderCustomResponse as exc:
        response = exc.response
    else:
        response = render_to_response(instructor_template, context)

    return response