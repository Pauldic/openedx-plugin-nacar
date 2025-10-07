# coding=utf-8
"""
Paul Okeke - https://pauldiconline.com
Feb-2022

https://lms.yourdomain.edu/openedx_plugin/api/v1/configuration
https://lms.yourdomain.edu/openedx_plugin/dashboard
https://lms.yourdomain.edu/openedx_plugin/dashboard?language=es-419
"""
# Django
from django.urls import path
from django.urls import re_path
# this repo
from openedx_plugin.dashboard.views import student_dashboard
from openedx_plugin.locale.views import marketing_redirector
from openedx_plugin.api.urls import urlpatterns as api_urlpatterns
from .waffle import waffle_switches, AUTOMATED_ENROLLMENT, MARKETING_REDIRECTOR

app_name = "openedx_plugin"

urlpatterns = [    
    path("courses/<str:course_id>/instructor/enrollment_list/", views.enrollment_list_view, name="nacar_enrollment_list"),
]

if waffle_switches[AUTOMATED_ENROLLMENT]:
    urlpatterns += [re_path(r"^dashboard/?$", student_dashboard, name="nacar_dashboard"),]

if waffle_switches[MARKETING_REDIRECTOR]:
    urlpatterns += [
        re_path(
            r"^marketing-redirector/?$",
            marketing_redirector,
            name="nacar_marketing_redirector",
        ),
    ]

urlpatterns += api_urlpatterns
