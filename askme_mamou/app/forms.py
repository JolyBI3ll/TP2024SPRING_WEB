from django import forms
from django.core.exceptions import ValidationError
from .models import *
from django.forms import TextInput, Textarea, FileInput, PasswordInput
import re


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': TextInput(),
            'password': PasswordInput()
        }
        labels = {
            'username': 'Login',
            'password': 'Password'
        }

    def clean(self):
        pass


class RegistrationForm(forms.ModelForm):
    nickname = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        self.cleaned_data['validated_password'] = password
        if len(password) < 8 or len(password) > 12:
            raise ValidationError("Password must be between 8 and 12 characters.")
        if not re.match(r'^[a-zA-Z0-9]+$', password):
            raise ValidationError("Password must contain only latin letters and numbers.")
        return password

    def clean_confirm_password(self):
        password = self.cleaned_data.get("validated_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise ValidationError("Passwords do not match.")
        return confirm_password

    def clean_avatar(self):
        return self.cleaned_data.get("avatar")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class SettingsForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True)
    avatar = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['email', 'avatar']

    def __init__(self, user=None, avatar=None, **kwargs):
        self._user = user
        self.avatar = avatar
        kwargs.update(initial={
            'email': self._user.email,
            'username': self._user.username,
            'avatar': self.avatar,
        })
        super().__init__(**kwargs)

    def clean(self):
        super().clean()

    def clean_email(self):
        if not self.cleaned_data['email']:
            return self._user.email
        if self._user.email != self.cleaned_data['email']:
            if User.objects.filter(email=self.cleaned_data['email']).exists():
                self.add_error(None, 'This email is already in use')
                raise forms.ValidationError('This email is already in use')
        return self.cleaned_data['email']

    def save(self):
        self._user.username = self.cleaned_data['username']
        self._user.email = self.cleaned_data['email']
        self._user.save()

        profile = Profile.objects.get(user=self._user)
        if self.cleaned_data['avatar'] is not None:
            profile.avatar = self.cleaned_data['avatar']
            profile.save()

        return self._user


class AskForm(forms.ModelForm):
    tags = forms.CharField(required=True)

    class Meta:
        model = Question
        fields = ['title', 'text']
        widgets = {
            'title': forms.TextInput(),
            'text': forms.Textarea(),
            'tags': forms.CharField()
        }

    def __init__(self, author=None, **kwargs):
        self._author = author
        super(AskForm, self).__init__(**kwargs)

    def clean_tags(self):
        self.tags = self.cleaned_data['tags'].split()
        if len(self.tags) > 3:
            self.add_error(None, 'Use no more than 3 tags')
            raise forms.ValidationError('Use no more than 3 tags')
        return self.tags

    def save(self, **kwargs):
        published_question = Question()
        published_question.author = self._author
        published_question.title = self.cleaned_data['title']
        published_question.text = self.cleaned_data['text']
        published_question.save()

        tags_id = []
        for tag in self.cleaned_data['tags']:
            if not Tag.objects.filter(name=tag).exists():
                new_tag = Tag.objects.create(name=tag)
                Tag.objects.increase_question_count(tag)
                tags_id.append(new_tag.id)
            else:
                existing_tag = Tag.objects.get(name=tag)
                Tag.objects.increase_question_count(tag)
                tags_id.append(existing_tag.id)
        published_question.tags.set(tags_id)
        published_question.save()

        return published_question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['text']

        widgets = {
            'text': forms.Textarea()
        }

    def __init__(self, author=None, question=None, **kwargs):
        self._author = author
        self._question = question
        super(AnswerForm, self).__init__(**kwargs)

    def save(self, **kwargs):
        new_answer = Answer()
        new_answer.author = self._author
        new_answer.question = self._question
        new_answer.text = self.cleaned_data['text']
        new_answer.save()

        question = Question.objects.get(id=self._question.id)
        buff = int(str(question.num_answers))
        buff += 1
        question.num_answers = str(int(str(question.num_answers)) + 1)
        question.save()

        return new_answer
