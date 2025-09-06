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
        print(f" MAKO: >>>>>>>>>>>>>>>  {type(settings.MAKO_TEMPLATE_DIRS_BASE)} settings.MAKO_TEMPLATE_DIRS_BASE ", settings.MAKO_TEMPLATE_DIRS_BASE)
        # settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
        # settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority
        # # settings.MAKO_TEMPLATE_DIRS_BASE.append(TEMPLATES_DIR)  # postpend to have priority
        mako_value = settings.MAKO_TEMPLATE_DIRS_BASE
        if hasattr(mako_value, "original"):
            mako_value = mako_value.original
        mako_dirs = list(mako_value)
        if str(TEMPLATES_DIR) not in mako_dirs:
            mako_dirs.insert(0, str(TEMPLATES_DIR))
        settings.MAKO_TEMPLATE_DIRS_BASE = mako_dirs

    # 2. Django templates (for render_to_string / email templates)t 
    if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
        # print(f"TEMPLATES 1: >>>>>>>>>>>>>>>  settings.TEMPLATES ", settings.TEMPLATES)  
        # if isinstance(settings.TEMPLATES[0]["DIRS"], Derived):      
        #     dirs = list(settings.TEMPLATES[0]["DIRS"])
        #     print(f"TEMPLATES 2: >>>>>>>>>>>>>>>  settings.TEMPLATES (List): ", dirs)
        #     dirs.insert(0, str(TEMPLATES_DIR))
        #     settings.TEMPLATES[0]["DIRS"] = dirs
        # else:            
        #     # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding BB {TEMPLATES_DIR} to {settings.TEMPLATES[0]['DIRS']}")
        #     settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
        #     # settings.TEMPLATES[0]["DIRS"].append(str(TEMPLATES_DIR))
        #     # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])
        if isinstance(settings.TEMPLATES[0]["DIRS"], Derived):
            # Pass a function that adds our plugin DIR to the final resolved list
            settings.TEMPLATES[0]["DIRS"] = Derived(add_plugin_template_dirs)
        else:
            # Plain list case
            if str(TEMPLATES_DIR) not in settings.TEMPLATES[0]["DIRS"]:
                settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))


def add_plugin_template_dirs(settings):
    # This function will be called by Derived after TEMPLATES[0]["DIRS"] is resolved
    dirs = list(settings.TEMPLATES[0]["DIRS"])  # safe now, it's a real list
    if str(TEMPLATES_DIR) not in dirs:
        dirs.insert(0, str(TEMPLATES_DIR))
    return dirs