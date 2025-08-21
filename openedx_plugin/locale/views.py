# coding=utf-8
"""
Paul Okeke - https://pauldiconline.com
Feb-2022

nacar theming utility functions
"""
import logging
from urllib.parse import urljoin

from django.shortcuts import redirect

from .utils import get_marketing_site

log = logging.getLogger(__name__)


def marketing_redirector(request):
    """
    Receives urls from MKTG_URL_OVERRIDES such as

    MKTG_URL_OVERRIDES: {
        "COURSES": "https://lms.nacarlearning.org/marketing-redirector?nacar_page=learning-content",
    }

    analyzes the request object to determine the best marketing site to redirect to.
    nacar: nacarlearning.org/learning-content

    """
    url = get_marketing_site(request)
    nacar_page = request.GET.get("nacar_page") or ""
    redirect_to = urljoin(url, nacar_page)

    return redirect(redirect_to)
