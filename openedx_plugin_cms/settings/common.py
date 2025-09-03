# coding=utf-8
"""
Paul Okeke - https://pauldiconline.com
Oct-2021

Common Pluggable Django App settings
"""
from path import Path as path

APP_ROOT = path(__file__).abspath().dirname().dirname()  # /openedx_plugin_cms
REPO_ROOT = APP_ROOT.dirname()  # openedx-plugin-nacar
TEMPLATES_DIR = APP_ROOT / "templates"


# -------------------------------
# Plugin Settings Injection
# -------------------------------
def plugin_settings(settings):
    """
        Injects local settings into django settings

        see: https://stackoverflow.com/questions/56129708/how-to-force-redirect-uri-to-use-https-with-python-social-app
    """

    # settings.MAKO_TEMPLATE_DIRS_BASE.extend([TEMPLATES_DIR])  
    # 1. Mako templates (keep this if you have any Mako-based templates)
    if hasattr(settings, "MAKO_TEMPLATE_DIRS_BASE"):
        settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
        settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority

    # 2. Django templates (for render_to_string / email templates)
    if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
        dirs = list(settings.TEMPLATES[0]["DIRS"])
        dirs.insert(0, str(TEMPLATES_DIR))
        settings.TEMPLATES[0]["DIRS"] = dirs

    # 3. Optional: static files directory if your plugin has static assets
    if hasattr(settings, "STATICFILES_DIRS"):
        settings.STATICFILES_DIRS = list(settings.STATICFILES_DIRS)
        settings.STATICFILES_DIRS.insert(0, str(STATIC_DIR))
