from django import forms


class EnrollUsersForm(forms.Form):
    emails = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "rows": 6,
                "placeholder": "user1@example.com\nuser2@example.com\n(one email per line)",
            }
        ),
        help_text="Enter one email per line (users must already exist).",
    )

