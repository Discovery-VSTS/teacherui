from django import forms


class UserForm(forms.Form):
    reg_username = forms.CharField(label='Your name', max_length=100)
    reg_password = forms.CharField(label='Your password', max_length=100)
    reg_password_confirm = forms.CharField(label='Your password', max_length=100)
    reg_email = forms.EmailField(label='Your email', max_length=100)
