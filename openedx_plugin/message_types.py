# message_types.py
from common.djangoapps.student.message_types import AccountActivation
from django.template.loader import render_to_string

class CustomAccountActivation(AccountActivation):
    """
    Override default LMS AccountActivation email to use a custom body.html template.
    """

    def render(self, context):
        """
        Render email body using custom template instead of default.
        """
        # Use your plugin's template: openedx_plugin/templates/student/edx_ace/accountactivation/email/body.html
        return render_to_string("student/edx_ace/accountactivation/email/body.html", context)
