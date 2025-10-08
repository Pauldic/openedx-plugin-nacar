# openedx-plugin-nacac/openedx_plugin/views.py
# from django.shortcuts import render
from common.djangoapps.edxmako.shortcuts import render_to_response as render

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from opaque_keys.edx.keys import CourseKey
from common.djangoapps.student.models import CourseEnrollment
from lms.djangoapps.courseware.courses import get_studio_url
from lms.djangoapps.courseware.courses import get_course_by_id
from common.djangoapps.student.roles import CourseInstructorRole, CourseStaffRole


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
    ).select_related('user').order_by('user__username')

    students = []
    for enrollment in enrollments:
        user = enrollment.user
        students.append({
            'username': user.username,
            'email': user.email,
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'mode': enrollment.mode,
            'enrollment_date': enrollment.created,
        })

    context = {
        'course': course,
        'students': students,
        'course_id': str(course_key),
        'studio_url': get_studio_url(course, 'course'),
    }

    return render(request, 'openedx_plugin/enrollment_list.html', context)