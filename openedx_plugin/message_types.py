# message_types.py
from common.djangoapps.student.message_types import AccountActivation
from django.template.loader import render_to_string

# class AccountActivation(BaseMessageType):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.options['transactional'] = True


class CustomAccountActivation(AccountActivation):
    """
    Override default LMS AccountActivation email to use a custom body.html template.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render(self, context):
        """
        Render email body using custom template instead of default.
        """
        # Use your plugin's template: openedx_plugin/templates/student/edx_ace/customaccountactivation/email/body.html
        print(">>>>>>>>>>>>>>>>>>> student/edx_ace/customaccountactivation/email/body.html")
        return render_to_string("student/edx_ace/customaccountactivation/email/body.html", context)
