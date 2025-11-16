# openedx_plugin_cms/views/bulk_enrollment.py (Assuming this is the correct file path based on your context)
# from django.shortcuts import render
from common.djangoapps.edxmako.shortcuts import render_to_response
from django.http import HttpResponseRedirect # Import for redirect handling

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.clickjacking import xframe_options_exempt # Correct import
from opaque_keys.edx.keys import CourseKey
from openedx_filters.learning.filters import InstructorDashboardRenderStarted # Correct filter import
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole

# Use the standard courseware imports
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.courseware.courses import get_studio_url # Use this for Studio URL

# Use the standard grades API
from lms.djangoapps.grades.api import CourseGradeFactory as LMSCourseGradeFactory # Standard factory

# Modulestore might be needed for low-level access if get_course_by_id isn't sufficient, but usually not needed here.
# from xmodule.modulestore.django import modulestore

# Avoid importing ScoreScope as it doesn't exist in grades.constants in Teak
# from lms.djangoapps.grades.constants import ScoreScope # <- This line was causing the import error

from django.contrib.auth.models import User
from common.djangoapps.student.models import UserProfile


def getNewVerbiage(mode_name):
    """Converts enrollment mode to a more readable format."""
    if mode_name == "honor":
        return "Learner"
    elif mode_name == "audit":
        return "Auditor"
    # Return the title-cased name for other modes (e.g., 'verified' -> 'Verified')
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
    except (ValueError, InvalidKeyError):
        # Handle invalid course ID string gracefully, e.g., return 404 or redirect
        # For now, let it raise if key is invalid
        raise Http404("Invalid course ID") # Requires: from django.http import Http404

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
        user = enrollment.user # Get the user from the enrollment object

        # Get full name from profile, fallback to first/last, then username
        full_name = ""
        if hasattr(user, 'profile') and user.profile.name:
            full_name = user.profile.name.strip()
        if not full_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
        if not full_name:
            full_name = user.username

        # --- GET OVERALL COURSE GRADE PERCENTAGE (Often reflects progress on graded items) ---
        grade_percent = None
        try:
            grade_record = LMSCourseGradeFactory().read(user, course_key) # Pass course_key, not course object
            if grade_record:
                grade_percent = round(grade_record.percent * 100, 1) # Percent is a float between 0 and 1
        except Exception as e:
            print(f"Error fetching grade for {user.email} in {course_id}: {e}")
            # Optionally log the error using Django's logging
            # import logging
            # log = logging.getLogger(__name__)
            # log.error(f"Error fetching grade for {user.email} in {course_id}: {e}")

        # --- CALCULATE PROGRESS PERCENTAGE (Based on Graded Subsections) ---
        # In most standard configurations, grade_record.percent *is* the progress on graded items.
        # However, to be explicit and ensure it matches the LMS Progress page logic:
        progress_percent = grade_percent # Often the same as grade_percent

        # If you needed a more granular calculation based on subsections (though likely unnecessary):
        # if grade_record:
        #     total_weighted_earned = 0
        #     total_weighted_possible = 0
        #     for subsection_grade in grade_record.graded_subsections.values():
        #         weight = subsection_grade.subsection.format_weight or 0
        #         earned = subsection_grade.graded_total.earned # Use 'graded_total' to exclude ungraded problems
        #         possible = subsection_grade.graded_total.possible
        #         total_weighted_earned += (earned / possible) * weight if possible > 0 else 0
        #         total_weighted_possible += weight
        #     if total_weighted_possible > 0:
        #         progress_percent = round((total_weighted_earned / total_weighted_possible) * 100, 1)
        #     else:
        #         progress_percent = 0.0 # Or None if no graded items


        students.append({
            'user_id': user.id,
            'username': user.username.lower(),
            'full_name': full_name.title(),
            'email': user.email.lower(),
            'mode': getNewVerbiage(enrollment.mode), # Call the helper function
            'grade': grade_percent,
            'progress': progress_percent, # Add the calculated progress
            'enrollment_date': enrollment.created,
        })

    context = {
        'course': course,
        'students': students,
        'course_id': str(course_key), # Pass the string representation of the key
        'studio_url': get_studio_url(course, 'course'), # Get Studio editing URL
    }
    instructor_template = 'openedx_plugin/enrollment_list.html' # Default template

    try:
        # Apply the filter to allow plugins to modify the context or template
        context, instructor_template = InstructorDashboardRenderStarted.run_filter(
            context=context, template_name=instructor_template)
    except InstructorDashboardRenderStarted.RenderInvalidDashboard as exc:
        # Handle the case where a plugin renders a custom response
        response = render_to_response(exc.instructor_template, exc.template_context)
    except InstructorDashboardRenderStarted.RedirectToPage as exc:
        # Handle the case where a plugin redirects
        response = HttpResponseRedirect(exc.redirect_to)
    except InstructorDashboardRenderStarted.RenderCustomResponse as exc:
        # Handle the case where a plugin returns a custom HttpResponse
        response = exc.response
    else:
        # Render the standard template with the context
        response = render_to_response(instructor_template, context)

    return response
