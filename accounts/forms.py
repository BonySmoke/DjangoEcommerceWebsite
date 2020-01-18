from django import forms
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()


class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'box_input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'box_input'}))

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('This user does not exist')
            if not user.check_password(password):
                raise forms.ValidationError('The password is incorrect')
            if not user.is_active:
                raise forms.ValidationError('The user is not active')
            return super(UserLoginForm, self).clean(*args, **kwargs)


class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'box_input'}))
    email = forms.EmailField(label='Your email', widget=forms.TextInput(attrs={'class':'box_input'}))
    email2 = forms.EmailField(label='Confirm email', widget=forms.TextInput(attrs={'class':'box_input'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'box_input'}))

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'email2',
            'password',
        ]

        def clean(self, *args, **kwargs):
            email = self.cleaned_data.get('email')
            email2 = self.cleaned_data.get('email2')
            if email != email2:
                raise forms.ValidationError('The emails should match')
            emails_qs = User.objects.filter(email=email)
            if emails_qs.exist():
                raise forms.ValidationError('The email is already taken')
            return super(UserRegisterForm, self).clean(*args, **kwargs)
