from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Post, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image')
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': "What's on your mind?",
                'rows': 3,
                'maxlength': 500,
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'maxlength': 300,
            })
        }


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    class Meta:
        model = Profile
        fields = ('bio', 'avatar_color', 'avatar', 'website')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'maxlength': 300, 'placeholder': 'Tell people about yourself...'}),
            'avatar_color': forms.TextInput(attrs={'type': 'color'}),
            'website': forms.URLInput(attrs={'placeholder': 'https://yourwebsite.com'}),
        }
