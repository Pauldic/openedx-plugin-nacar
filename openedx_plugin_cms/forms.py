# openedx_plugin_cms/forms.py
from django import forms
from opaque_keys.edx.keys import CourseKey
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview

# class BulkEnrollmentForm(forms.Form):
#     course_ids = forms.MultipleChoiceField(
#         choices=[],  # populated dynamically in __init__
#         widget=forms.CheckboxSelectMultiple,
#         label="Select Courses"
#     )
#     emails = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": 6, "placeholder": "user1@example.com\nuser2@example.com"}),
#         help_text="Enter one email per line.",
#         label="User Emails"
#     )

#     def __init__(self, request, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Get courses the user can access in Studio
#         from cms.djangoapps.contentstore.views.course import get_courses_accessible_to_user
#         courses, _ = get_courses_accessible_to_user(request)
#         self.fields['course_ids'].choices = [
#             (str(course.id), course.display_name)
#             for course in courses
#         ]