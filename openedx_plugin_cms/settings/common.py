# coding=utf-8
"""
Lawrence McDaniel - https://lawrencemcdaniel.com
Oct-2021

Common Pluggable Django App settings
"""
from path import Path as path

APP_ROOT = (path(__file__).abspath().dirname().dirname())  # /blah/blah/blah/.../nacar-digital-learning-openedx/openedx_plugin
TEMPLATES_DIR = APP_ROOT / "templates"

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
        print(f">>>>>>>>>>>>>>>  settings.MAKO_TEMPLATE_DIRS_BASE ", settings.MAKO_TEMPLATE_DIRS_BASE)
        settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
        # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding AA {TEMPLATES_DIR} to {settings.MAKO_TEMPLATE_DIRS_BASE}")
        settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority
        # settings.MAKO_TEMPLATE_DIRS_BASE.append(TEMPLATES_DIR)  # postpend to have priority

    # 2. Django templates (for render_to_string / email templates)t 
    if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
        print(f">>>>>>>>>>>>>>>  settings.TEMPLATES ", settings.TEMPLATES)
        # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding BB {TEMPLATES_DIR} to {settings.TEMPLATES[0]['DIRS']}")
        settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
        # settings.TEMPLATES[0]["DIRS"].append(str(TEMPLATES_DIR))
        # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])


