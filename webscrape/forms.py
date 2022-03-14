from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# Create your forms here.

class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'required':'',
            'name':'username',
            'id':'username',
            'type':'text',
            'placeholder':'John Doe',
        })
        self.fields['email'].widget.attrs.update({
            'required':'',
            'name': 'email',
            'id': 'email',
            'type' :'email',
            'placeholder': 'JohnDoe@mail.com',
        })
        self.fields['password1'].widget.attrs.update({
            'required':'',
            'name':'password1',
            'id':'password1',
            'type':'password',
            'placeholder':'password',
            'maxlength':'22',
            'minlength':'8'
        })
        self.fields['password2'].widget.attrs.update({
            'required': '',
            'name':' password2',
            'id':'password2',
            'type':'password',
            'placeholder':'password',
            'maxlength':'22',
            'minlength':'8'
        })

    username = forms.CharField(max_length=20, label=False)
    email = forms.EmailField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
