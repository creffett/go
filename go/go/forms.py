from django import forms
from go.models import URL
from django.core.validators import MinLengthValidator, MinValueValidator, RegexValidator
from django.core.exceptions import ValidationError

class URLForm( forms.ModelForm ):

    DAY = '1 Day'
    WEEK = '1 Week'
    MONTH = '1 Month'
    NEVER = 'Never'

    EXPIRATION_CHOICES = (
        (DAY, DAY),
        (WEEK, WEEK),
        (MONTH, MONTH),
        (NEVER, NEVER),
    )

    # Add a custom expiration choice field.
    expires = forms.ChoiceField(
        required = True,
        label = 'Expiration',
        choices = EXPIRATION_CHOICES,
        initial = NEVER,
        widget = forms.RadioSelect(),
    )

    # Short field must be only letters.
    alphanumeric = RegexValidator(
        r'^[a-zA-Z]*$',
        'Only letters are allowed.'
    )

    def unique_short( value ):
        try:
            URL.objects.get(short__iexact=value)
        except URL.DoesNotExist:
            return
        raise ValidationError('Short url already exists.')

    # Custom short-url field with validators.
    short = forms.CharField(
        required = False,
        label = 'Short URL (Optional)',
        widget = forms.TextInput(attrs={}),
        validators = [alphanumeric,unique_short],
        max_length = 20,
        min_length = 3,
    )

    class Meta:
        model = URL
        fields = ('target',)
        exclude = ('owner', 'short', 'date_created', 'clicks', 'expires')
        labels = {
            'target': 'Long URL',
        }
        widgets = {
            'target': forms.URLInput(attrs={
                'placeholder': 'http://',
            }),
        }


class SignupForm( forms.Form ):
    username = forms.CharField(
        required = True,
        label = 'Username',
        max_length = 30,
        widget = forms.TextInput(attrs={
        }),
    )
    full_name = forms.CharField(
        required = True,
        label = 'Full Name',
        max_length = 100,
        widget = forms.TextInput(attrs={
        }),
    )
    description = forms.CharField(
        required = False,
        label = 'Description (Optional)',
        max_length = 200,
        widget = forms.Textarea(attrs={
        }),
    )
