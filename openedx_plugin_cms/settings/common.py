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

    # # 2. Django templates (for render_to_string / email templates)t 
    # if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
    #     print(f"\n\n>>>>>>>>>>>>>>>>>>>>>>>>>> Adding BB {TEMPLATES_DIR} to {settings.TEMPLATES[0]['DIRS']}")
    #     settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
    #     # settings.TEMPLATES[0]["DIRS"].append(str(TEMPLATES_DIR))
    #     # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])


    # # 2. Django templates (for render_to_string / email templates)
    # if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
    #     # print(f"TEMPLATES 1: >>>>>>>>>>>>>>>  settings.TEMPLATES ", settings.TEMPLATES)  
    #     # if isinstance(settings.TEMPLATES[0]["DIRS"], Derived):      
    #     #     dirs = list(settings.TEMPLATES[0]["DIRS"])
    #     #     print(f"TEMPLATES 2: >>>>>>>>>>>>>>>  settings.TEMPLATES (List): ", dirs)
    #     #     dirs.insert(0, str(TEMPLATES_DIR))
    #     #     settings.TEMPLATES[0]["DIRS"] = dirs
    #     # else:            
    #     #     # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding BB {TEMPLATES_DIR} to {settings.TEMPLATES[0]['DIRS']}")
    #     #     settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
    #     #     # settings.TEMPLATES[0]["DIRS"].append(str(TEMPLATES_DIR))
    #     #     # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])
    #     def prepend_plugin_dir(settings):
    #         print(f">>>>>>>>>>>>>>>  settings.TEMPLATES: ", settings.TEMPLATES) 
    #         print(f"isDrived: {isinstance(settings.TEMPLATES[0]['DIRS'], Derived)}")
    #         # Ensure settings.TEMPLATES[0]["DIRS"] is a list
    #         dirs = list(settings.TEMPLATES[0]["DIRS"]) if isinstance(settings.TEMPLATES[0]["DIRS"], list) else []
    #         if str(TEMPLATES_DIR) not in dirs:
    #             dirs.insert(0, str(TEMPLATES_DIR))
    #         print(f"Dirs: {dirs}")
    #         return dirs

    #     settings.TEMPLATES[0]["DIRS"] = Derived(lambda settings: prepend_plugin_dir(settings))

    # 2. Django templates (for render_to_string / email templates)
    if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
        print(f"\n\n ------ Here {type(settings.TEMPLATES[0]['DIRS'])}\n{settings.TEMPLATES[0]['DIRS']}")
        # Create a new Derived instance that properly combines template directories
        settings.TEMPLATES[0]["DIRS"] = Derived(lambda settings: get_template_dirs(settings))
        
    def get_template_dirs(settings):
        # First, get the existing template directories from the Derived object
        try:
            if isinstance(settings.TEMPLATES[0]["DIRS"], Derived):
                print(f"Org A: {settings.TEMPLATES[0]['DIRS']}")
                # Handle the Derived object properly                
                original_dirs = list(settings.TEMPLATES[0]["DIRS"])
            else:
                print(f"Org B: {settings.TEMPLATES[0]['DIRS']}")
                # Fallback to standard list handling
                original_dirs = list(settings.TEMPLATES[0]["DIRS"])
        except Exception as e:
            print(f">>> {e}")
            # Default to empty list if there's an error
            original_dirs = []
        
        # Convert all paths to strings for comparison
        original_dirs_str = [str(d) for d in original_dirs]
        
        # Only add our template directory if it's not already present
        if TEMPLATES_DIR not in original_dirs_str:
            print(f"Adding: {TEMPLATES_DIR} to {original_dirs}")
            original_dirs = [TEMPLATES_DIR] + original_dirs
        
        print(f">>>>>>>>>>>>>>>  Dir 2: {original_dirs}")
        return original_dirs
    
    
    
    
    
#     # settings.MAKO_TEMPLATE_DIRS_BASE.extend([TEMPLATES_DIR])    
#     # 1. Mako templates (keep this if you have any Mako-based templates)
#     if hasattr(settings, "MAKO_TEMPLATE_DIRS_BASE"):
#         # print(f" MAKO: >>>>>>>>>>>>>>>  {type(settings.MAKO_TEMPLATE_DIRS_BASE)} settings.MAKO_TEMPLATE_DIRS_BASE ", settings.MAKO_TEMPLATE_DIRS_BASE)
#         # settings.MAKO_TEMPLATE_DIRS_BASE = list(settings.MAKO_TEMPLATE_DIRS_BASE)  # ensure mutable
#         # settings.MAKO_TEMPLATE_DIRS_BASE.insert(0, TEMPLATES_DIR)  # prepend to have priority
#         # # settings.MAKO_TEMPLATE_DIRS_BASE.append(TEMPLATES_DIR)  # postpend to have priority
#         mako_value = settings.MAKO_TEMPLATE_DIRS_BASE
#         if hasattr(mako_value, "original"):
#             mako_value = mako_value.original
#         mako_dirs = list(mako_value)
#         if str(TEMPLATES_DIR) not in mako_dirs:
#             mako_dirs.insert(0, str(TEMPLATES_DIR))
#         settings.MAKO_TEMPLATE_DIRS_BASE = mako_dirs

#     # 2. Django templates (for render_to_string / email templates)t 
#     if hasattr(settings, "TEMPLATES") and settings.TEMPLATES:
#         # print(f"TEMPLATES 1: >>>>>>>>>>>>>>>  settings.TEMPLATES ", settings.TEMPLATES)  
#         # if isinstance(settings.TEMPLATES[0]["DIRS"], Derived):      
#         #     dirs = list(settings.TEMPLATES[0]["DIRS"])
#         #     print(f"TEMPLATES 2: >>>>>>>>>>>>>>>  settings.TEMPLATES (List): ", dirs)
#         #     dirs.insert(0, str(TEMPLATES_DIR))
#         #     settings.TEMPLATES[0]["DIRS"] = dirs
#         # else:            
#         #     # print(f">>>>>>>>>>>>>>>>>>>>>>>>>> Adding BB {TEMPLATES_DIR} to {settings.TEMPLATES[0]['DIRS']}")
#         #     settings.TEMPLATES[0]["DIRS"].insert(0, str(TEMPLATES_DIR))
#         #     # settings.TEMPLATES[0]["DIRS"].append(str(TEMPLATES_DIR))
#         #     # settings.TEMPLATES[0]["DIRS"] = [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])
#         def prepend_plugin_dir(settings):
#             # Ensure settings.TEMPLATES[0]["DIRS"] is a list
#             dirs = list(settings.TEMPLATES[0]["DIRS"]) if isinstance(settings.TEMPLATES[0]["DIRS"], list) else []
#             if str(TEMPLATES_DIR) not in dirs:
#                 dirs.insert(0, str(TEMPLATES_DIR))
#             return dirs

#         settings.TEMPLATES[0]["DIRS"] = Derived(lambda settings: prepend_plugin_dir(settings))

#     # 3. Course templates (for Studio "Create Course" templates)
#     # if hasattr(settings, "COURSE_TEMPLATES_DIRS"):
#     #     if str(COURSE_TEMPLATE_DIR) not in settings.COURSE_TEMPLATES_DIRS:
#     #         settings.COURSE_TEMPLATES_DIRS.insert(0, str(COURSE_TEMPLATE_DIR))
#     # else:
#     #     settings.COURSE_TEMPLATES_DIRS = [str(COURSE_TEMPLATE_DIR)]
#     # # Optional: Make 'private' the default template (This avoids requiring authors to manually pick your template.)
#     # settings.COURSE_CREATION_SETTINGS = getattr(settings, 'COURSE_CREATION_SETTINGS', {})
#     # settings.COURSE_CREATION_SETTINGS['DEFAULT_COURSE_TEMPLATE'] = 'private'
    
#     # if hasattr(settings, "COURSE_TEMPLATES_DIRS"):
#     #     settings.COURSE_TEMPLATES_DIRS = []

#     # if hasattr(settings, "COURSE_CREATION_SETTINGS"):
#     #     if hasattr(settings.COURSE_CREATION_SETTINGS, "DEFAULT_COURSE_TEMPLATE"):
#     #         if settings.COURSE_CREATION_SETTINGS['DEFAULT_COURSE_TEMPLATE'] == 'private':
#     #             del settings.COURSE_CREATION_SETTINGS['DEFAULT_COURSE_TEMPLATE']
        
#     # 4. Allow your domain for course intro videos
#     settings.VIDEO_IMAGE_SETTINGS = getattr(settings, 'VIDEO_IMAGE_SETTINGS', {})
#     hosting_sites = settings.VIDEO_IMAGE_SETTINGS.get("VIDEO_HOSTING_SITES", [])
#     if settings.LMS_BASE not in hosting_sites:
#         hosting_sites.append(settings.LMS_BASE)
#     settings.VIDEO_IMAGE_SETTINGS["VIDEO_HOSTING_SITES"] = hosting_sites
    
# def __add_plugin_template_dirs(settings):
#     """
#         This is called by Derived after TEMPLATES[0]["DIRS"] is resolved.
#         We just prepend our plugin template dir if it’s not already there.
#     """
#     # settings.TEMPLATES[0]["DIRS"] may still be a Derived; do NOT try to unwrap.
#     # Instead, operate on settings._resolved if available, or prepend via another Derived.
    
#     # The safest way is to redefine the list in a new Derived:
#     return [str(TEMPLATES_DIR)] + list(settings.TEMPLATES[0]["DIRS"])