from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ім\'я користувача',
            'id': 'username'
        }),
        label='Ім\'я користувача'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'id': 'password'
        }),
        label='Пароль'
    )
    remember_me = forms.BooleanField(
        required=False, 
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'remember-me'
        }),
        label='Запам\'ятати мене'
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'remember_me')

    def clean(self):
        cleaned_data = super().clean()
        remember_me = cleaned_data.get('remember_me')
        if remember_me:
            # Session will be remembered for 30 days
            self.request.session.set_expiry(2592000)
        else:
            # Session will expire when browser closes
            self.request.session.set_expiry(0)
        return cleaned_data


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ім\'я користувача',
            'id': 'username'
        }),
        label='Ім\'я користувача',
        help_text='Обов\'язкове поле. Не більше 30 символів.'
    )
    first_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ім\'я',
            'id': 'first_name'
        }),
        label='Ім\'я',
        required=True
    )
    last_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Прізвище',
            'id': 'last_name'
        }),
        label='Прізвище',
        required=True
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Електронна пошта',
            'id': 'email'
        }),
        label='Електронна пошта'
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Пароль',
            'id': 'password1'
        }),
        label='Пароль',
        help_text='Пароль має містити принаймні 8 символів.'
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Підтвердження пароля',
            'id': 'password2'
        }),
        label='Підтвердження пароля',
        help_text='Введіть той самий пароль, що й вище, для перевірки.'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Користувач з такою електронною поштою вже існує')
        return email


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ім\'я',
            'id': 'first_name'
        }),
        label='Ім\'я',
        required=True
    )
    last_name = forms.CharField(
        max_length=30, 
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Прізвище',
            'id': 'last_name'
        }),
        label='Прізвище',
        required=True
    )
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Електронна пошта',
            'id': 'email'
        }),
        label='Електронна пошта'
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Користувач з такою електронною поштою вже існує')
        return email