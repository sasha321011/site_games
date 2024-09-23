import datetime
from captcha.fields import CaptchaField
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm


class LoginUserForm(AuthenticationForm):
    class Meta:
        model = get_user_model()
        fields = ['username', 'password']


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    captcha = CaptchaField(label='Пройдите капчу')

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name','date_birth', 'username', 'password1', 'password2', 'email', 'captcha']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такой email уже существует')
        return email


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.CharField(disabled=True, label='E-mail', widget=forms.TextInput(attrs={'class': 'form-input'}))
    this_year = datetime.date.today().year
    date_birth = forms.DateField(widget=forms.SelectDateWidget(years=tuple(range(this_year - 100, this_year - 5))))

    extra_context = {
        'default_image': settings.DEFAULT_USER_IMAGE
    }

    class Meta:
        model = get_user_model()
        fields = ['photo', 'first_name', 'last_name', 'date_birth', 'username', 'email', ]
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
        }


class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password2 = forms.CharField(label='Подтверждение пароля',
                                    widget=forms.PasswordInput(attrs={'class': 'form-input'}))
