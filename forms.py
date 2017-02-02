from django.contrib.auth.forms import AuthenticationForm
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django import forms
from .models import ForumCategory, Badge, Topic, Comment, UserProfile
from django.template.defaultfilters import slugify


class LoginForm(AuthenticationForm):

    def clean_username(self):
        email = self.cleaned_data['username']
        user = User.objects.filter(email=email)
        if not user:
            raise forms.ValidationError('Email is not registered.')
        elif not user[0].is_active:
            raise forms.ValidationError('Your account is not activated yet!')
        return email


class RegisterForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', 'first_name', 'username', 'password']


class CategoryForm(forms.ModelForm):
    class Meta:
        model = ForumCategory
        exclude = ('slug', 'created_by')

    def clean_title(self):
        if ForumCategory.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Category with this Name already exists.')

        return self.cleaned_data['title']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CategoryForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CategoryForm, self).save(commit=False)
        instance.created_by = self.user
        instance.title = self.cleaned_data['title']
        if str(self.cleaned_data['is_votable']) == 'True':
            instance.is_votable = True
        else:
            instance.is_votable = False
        if str(self.cleaned_data['is_active']) == 'True':
            instance.is_active = True
        else:
            instance.is_active = False
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])

        if commit:
            instance.save()
        return instance


class BadgeForm(forms.ModelForm):
    class Meta:
        model = Badge
        exclude = ('slug',)

    def clean_title(self):
        if Badge.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Badge with this Name already exists.')

        return self.cleaned_data['title']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(BadgeForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(BadgeForm, self).save(commit=False)
        instance.title = self.cleaned_data['title']
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])
        if commit:
            instance.save()
        return instance


class TopicForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(TopicForm, self).__init__(*args, **kwargs)
        self.fields["category"].widget.attrs = {"class": "form-control select2"}
        self.fields["title"].widget.attrs = {"class": "form-control"}
        self.fields["tags"].widget.attrs = {"class": "form-control tags"}

    tags = forms.CharField(required=False)

    class Meta:
        model = Topic
        fields = ("title", "category", "description", "tags")
    
    def clean_title(self):
        if Topic.objects.filter(slug=slugify(self.cleaned_data['title'])).exclude(id=self.instance.id):
            raise forms.ValidationError('Topic with this Name already exists.')

        return self.cleaned_data['title']


    def save(self, commit=True):
        instance = super(TopicForm, self).save(commit=False)
        instance.title = self.cleaned_data['title']
        instance.description = self.cleaned_data['description']
        instance.category = self.cleaned_data['category']
        if not self.instance.id:
            instance.slug = slugify(self.cleaned_data['title'])
            instance.created_by = self.user
            instance.status = 'Draft'
        if commit:
            instance.save()
        return instance


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment', 'topic')

    def clean_comment(self):
        if self.cleaned_data['comment']:
            return self.cleaned_data['comment']
        raise forms.ValidationError('This field is required')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(CommentForm, self).save(commit=False)
        instance.comment = self.cleaned_data['comment']
        instance.topic = self.cleaned_data['topic']
        if not self.instance.id:
            instance.commented_by = self.user
            if 'parent' in self.cleaned_data.keys() and self.cleaned_data['parent']:
                instance.parent = self.cleaned_data['parent']
        if commit:
            instance.save()
        return instance


class UserProfileForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        fields = ['badges']


class ChangePasswordForm(forms.Form):
    oldpassword = forms.CharField(max_length=50)
    newpassword = forms.CharField(max_length=50)
    retypepassword = forms.CharField(max_length=50)


class UserChangePasswordForm(forms.Form):
    newpassword = forms.CharField(max_length=50)
    retypepassword = forms.CharField(max_length=50)


class ForgotPasswordForm(forms.Form):
    email = forms.CharField(max_length=200)

    def clean_username(self):
        user = UserProfile.objects.filter(user__email=self.data.get("email"))
        if user:
            return self.data.get("email")
        else:
            raise forms.ValidationError(
                "User with this email ID doesn't exists.")
