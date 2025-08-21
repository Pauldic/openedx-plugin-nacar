# coding=utf-8
"""
written by:     Paul Okeke
                https://pauldiconline.com

date:           sep-2021

usage:          register the custom Django model in LMS Django Admin
"""
from django.contrib import admin
from .models import CoursePoints


class CoursePointsAdmin(admin.ModelAdmin):
    pass


admin.site.register(CoursePoints, CoursePointsAdmin)
