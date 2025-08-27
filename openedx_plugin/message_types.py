from common.djangoapps.student.message_types import AccountActivation as BaseAccountActivation


class CustomAccountActivation(BaseAccountActivation):
    template_name = "student/edx_ace/accountactivation/email/body.html"
