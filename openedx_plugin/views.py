# openedx-plugin-nacac/openedx_plugin/views.py
# from django.shortcuts import render
from common.djangoapps.edxmako.shortcuts import render_to_response

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from opaque_keys.edx.keys import CourseKey
from openedx_filters.learning.filters import InstructorDashboardRenderStarted
from common.djangoapps.student.models import CourseEnrollment
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole

from xmodule.modulestore.django import modulestore
from lms.djangoapps.courseware.courses import get_studio_url
from lms.djangoapps.grades.api import CourseGradeFactory
from lms.djangoapps.course_blocks.api import get_course_blocks
from lms.djangoapps.courseware.courses import get_course_by_id
from lms.djangoapps.grades.api import CourseGradeFactory

from lms.djangoapps.grades.course_grade_factory import CourseGradeFactory as LMSCourseGradeFactory
from lms.djangoapps.grades.subsection_grade_factory import SubsectionGradeFactory
from lms.djangoapps.grades.config import GRADING_POLICY_CHANGED
from lms.djangoapps.grades.models import PersistentSubsectionGrade, PersistentCourseGrade
from lms.djangoapps.grades.constants import ScoreScope
from openedx.core.lib.cache_utils import request_cached

from django.contrib.auth.models import User
from common.djangoapps.student.models import UserProfile


def getNewVerbiage (name):
    if name == "honor":
      return "Learner"
    elif name == "audit":
      return "Auditor"
    
    return name.title()
  


@login_required
@xframe_options_exempt
def enrollment_list_view(request, course_id):
    print(f" >>>>>> >> >>>>>>> Enrollment List for: {course_id}")
    
    course_key = CourseKey.from_string(course_id)

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
        
        full_name = user.profile.name.strip() if hasattr(user, 'profile') else ""
            
        # Fallback to first/last name if profile name is empty
        if not full_name:
            full_name = f"{user.first_name} {user.last_name}".strip()

        # Final fallback to username
        if not full_name:
            full_name = user.username

        # Get grade
        try:
            grade = CourseGradeFactory().read(user, course)
            grade_percent = round(grade.percent * 100, 1)
        except Exception:
            grade_percent = None

        # --- CALCULATE PROGRESS PERCENTAGE (Based on Graded Blocks) ---
        progress_percent = None
        try:
            # Get the course grade object which contains subsection grades
            course_grade = LMSCourseGradeFactory().read(user, course)
            if course_grade:
                # The overall course grade percentage often reflects the weighted sum of graded subsections
                # This is effectively the progress based on graded assignments.
                # The 'percent' attribute of the course grade is usually the best indicator.
                # However, if you need a calculation based *only* on specific subsection types (like homework/exam),
                # you'd need to iterate through subsections manually.
                # For simplicity, using the overall grade percent is often equivalent.
                # If the course grade calculation explicitly excludes non-graded items from the percentage,
                # then grade.percent *is* the progress percentage.
                # If not, a more detailed calculation might be needed based on subsection grades.
                # The default Open edX grade calculation *should* be based on *graded* subsections.
                progress_percent = grade_percent # Often the same as grade_percent for the overall progress
                # Alternatively, if grade.percent includes non-graded items, calculate manually:
                # total_weighted_score = 0
                # total_possible_weighted_score = 0
                # for subsection_grade in course_grade.graded_subsections.values():
                #     # Calculate weighted score for this subsection
                #     subsection_weight = subsection_grade.subsection.format_weight or 0
                #     subsection_earned = subsection_grade.all_total.earned
                #     subsection_possible = subsection_grade.all_total.possible
                #     if subsection_possible > 0:
                #         subsection_percent = (subsection_earned / subsection_possible) * 100
                #         total_weighted_score += subsection_percent * subsection_weight
                #         total_possible_weighted_score += 100 * subsection_weight # Max possible for this subsection part
                # if total_possible_weighted_score > 0:
                #     progress_percent = (total_weighted_score / total_possible_weighted_score) * 100
                # else:
                #     progress_percent = 0.0 # Or None if no graded items found

        except Exception as e:
            print(f"Error calculating progress for {user.email} in {course_id}: {e}")
            # Fallback to grade_percent if progress calculation fails
            progress_percent = grade_percent # Or set to None if you prefer no value on failure

        students.append({
            'user_id': user.id,
            'username': user.username.lower(),
            'full_name': full_name.title(),
            'email': user.email.lower(),
            'mode': getNewVerbiage(enrollment.mode),
            'grade': grade_percent,
            'progress': progress_percent, # Add the calculated progress,
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
        # .. filter_implemented_name: InstructorDashboardRenderStarted
        # .. filter_type: org.openedx.learning.instructor.dashboard.render.started.v1
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

    # return render(request, instructor_template, context)