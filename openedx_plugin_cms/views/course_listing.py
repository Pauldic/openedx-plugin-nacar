
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from cms.djangoapps.contentstore.utils import get_home_context
from common.djangoapps.edxmako.shortcuts import render_to_response


@login_required
@ensure_csrf_cookie
def course_listing(request):
    """
    List all courses available to the logged in user
    """
    
    home_context = get_home_context(request)
    return render_to_response('index.html', home_context)
    