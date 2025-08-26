# coding=utf-8
"""
Common Pluggable Django App settings

Handling of environment variables, see: https://django-environ.readthedocs.io/en/latest/
to convert .env to yml see: https://django-environ.readthedocs.io/en/latest/tips.html#docker-style-file-based-variables
"""
import os
import environ
from path import Path as path

# -------------------------------
# Paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# -------------------------------
# Paths
# -------------------------------
APP_ROOT = (path(__file__).abspath().dirname().dirname())  # /blah/blah/blah/.../nacar-digital-learning-openedx/openedx_plugin
REPO_ROOT = APP_ROOT.dirname()  # /blah/blah/blah/.../nacar-digital-learning-openedx
TEMPLATES_DIR = APP_ROOT / "templates"
STATIC_DIR = APP_ROOT / "static"

# -------------------------------
# Plugin Settings Injection
# -------------------------------
def plugin_settings(settings):
    """
    Injects local settings into django settings

    see: https://stackoverflow.com/questions/56129708/how-to-force-redirect-uri-to-use-https-with-python-social-app
    """

    # settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # settings.MAKO_TEMPLATE_DIRS_BASE.extend([TEMPLATES_DIR])    
    # 1. Mako templates (keep this if you have any Mako-based templates)
    if hasattr(settings, "MAKO_TEMPLATE_DIRS_BASE"):
        settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
        settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority

    # 2. Django templates (for render_to_string / email templates)
    if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
        settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
        # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])

    # 3. Optional: static files directory if your plugin has static assets
    if hasattr(settings, "STATICFILES_DIRS"):
        settings.STATICFILES_DIRS = list(settings.STATICFILES_DIRS)
        settings.STATICFILES_DIRS.insert(0, str(STATIC_DIR))

    # 4. Dummy request & user for Celery tasks
    # This avoids 'VariableDoesNotExist' errors when rendering templates in background
    if not hasattr(settings, "PLUGIN_DUMMY_CONTEXT_FACTORY"):
        def dummy_context():
            from types import SimpleNamespace
            from django.contrib.sites.models import Site
            from django.contrib.auth.models import AnonymousUser

            dummy_site = Site(domain="example.com", name="Example")
            dummy_request = SimpleNamespace(user=AnonymousUser(), site=dummy_site)
            dummy_message = SimpleNamespace(app_label="openedx_plugin")

            return {
                "request": dummy_request,
                "user": dummy_request.user,
                "site": dummy_site,
                "message": dummy_message,
            }

        settings.PLUGIN_DUMMY_CONTEXT_FACTORY = dummy_context