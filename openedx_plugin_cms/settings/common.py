# coding=utf-8
"""
Lawrence McDaniel - https://lawrencemcdaniel.com
Oct-2021

Common Pluggable Django App settings
"""

from path import Path as path
from openedx.core.lib.derived import Derived

APP_ROOT = (path(__file__).abspath().dirname().dirname())  # /blah/blah/blah/.../nacar-digital-learning-openedx/openedx_plugin
TEMPLATES_DIR = APP_ROOT / "templates"
STATIC_DIR = APP_ROOT / "static"

# COURSE_TEMPLATE_DIR = APP_ROOT / "templates"
COURSE_TEMPLATE_DIR = APP_ROOT / "templates" / "course_template"

from datetime import datetime
print(f" >>>>>> >> >>>>>>> openedx_plugin_cms.settings.common loaded {datetime.now().isoformat()}")
    
# -------------------------------
# Plugin Settings Injection
# -------------------------------
def plugin_settings(settings):
    """
        Injects local settings into django settings

        see: https://stackoverflow.com/questions/56129708/how-to-force-redirect-uri-to-use-https-with-python-social-app
    """

    settings.NACAR_FEATURES = getattr(settings, 'NACAR_FEATURES', {})
    settings.NACAR_FEATURES['BULK_ENROLLMENT'] = True
    
    # settings.SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    # settings.MAKO_TEMPLATE_DIRS_BASE.extend([TEMPLATES_DIR])    
    # 1. Mako templates (keep this if you have any Mako-based templates)
    if hasattr(settings, "MAKO_TEMPLATE_DIRS_BASE"):
        settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
        # print(f"\n\n>>>>>>>>>>>>>>>>>>>>>>>>>> Found: {list(settings.MAKO_TEMPLATE_DIRS_BASE)}")
        settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority
        # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding {TEMPLATES_DIR} to {settings.MAKO_TEMPLATE_DIRS_BASE}")
