from django import forms
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from django.forms import inlineformset_factory


class CustomCaptchaForm(forms.Form):
    captcha = CaptchaField(
        label='Captcha',
        required=True,
        error_messages={
            'required': 'Captcha cannot be empty'
        }
    )
