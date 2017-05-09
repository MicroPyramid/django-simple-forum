import json
import urllib
import requests
from urllib.parse import urlparse
from datetime import datetime

from django.contrib.auth import logout, login, load_backend
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.files import File
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.http import JsonResponse
from django.http.response import HttpResponseRedirect, HttpResponse
from django.views.generic import TemplateView, UpdateView, ListView, CreateView, DetailView,\
    DeleteView, View
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.template import Context,loader
from django.template.defaultfilters import slugify
from django.utils.crypto import get_random_string

try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

# from endless_pagination.views import AjaxListView
from microurl import google_mini

from .forms import LoginForm
from .models import ForumCategory, STATUS, Badge, Topic, Tags, UserProfile, UserTopics, Timeline,\
    Facebook, Google, Comment, Vote
from .mixins import AdminMixin, LoginRequiredMixin, CanUpdateTopicMixin
from .forms import CategoryForm, BadgeForm, RegisterForm, TopicForm, CommentForm, UserProfileForm,\
    ChangePasswordForm, UserChangePasswordForm, ForgotPasswordForm
# from mpcomp.facebook import GraphAPI, get_access_token_from_code
from .sending_mail import Memail


def timeline_activity(user, content_object, namespace, event_type):
    Timeline.objects.create(
        user=user,
        content_object=content_object,
        namespace=namespace,
        event_type=event_type,
    )


class LoginView(FormView):
    template_name = 'dashboard/dashboard_login.html'
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            if request.user.is_superuser:
                return redirect('django_simple_forum:dashboard')
            else:
                return redirect('django_simple_forum:topic_list')
        return super(LoginView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        if user.is_superuser:
            login(self.request, form.get_user())
            data = {
                'error': False,
                'response': 'You have successfully logged into the dashboard'
            }
        else:
            data = {
                'error': True,
                'response': 'You dont have access to login to dashboard'
            }
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})


class DashboardView(AdminMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'


def getout(request):
    if not request.user.is_superuser:
        logout(request)
        return HttpResponseRedirect(reverse('django_simple_forum:topic_list'))
    else:
        logout(request)
        return HttpResponseRedirect(reverse('django_simple_forum:dashboard'))


class CategoryList(AdminMixin, ListView):
    model = ForumCategory
    template_name = 'dashboard/categories.html'
    context_object_name = 'categories_list'

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        categories_list = ForumCategory.objects.filter(parent=None)
        context['categories_list'] = categories_list
        return context

    def post(self, request, *args, **kwargs):
        categories_list = self.model.objects.all()

        if request.POST.get('is_active') == 'True':
            categories_list = categories_list.filter(is_active=True)
        if request.POST.get('search_text', ''):
            categories_list = categories_list.filter(
                title__icontains=request.POST.get('search_text')
            )
        return render(request, self.template_name, {'categories_list': categories_list})


class CategoryDetailView(AdminMixin, DetailView):
    model = ForumCategory
    template_name = 'dashboard/view_category.html'
    slug_field = "slug"
    context_object_name = 'category'

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])


class CategoryAdd(AdminMixin, CreateView):
    model = ForumCategory
    form_class = CategoryForm
    template_name = "dashboard/category_add.html"
    success_url = '/forum/dashboard/categories/add/'

    def get_form_kwargs(self):
        kwargs = super(CategoryAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        menu = form.save()
        if self.request.POST.get('parent'):
            menu.parent_id = self.request.POST.get('parent')
            menu.save()

        data = {'error': False, 'response': 'Successfully Created Category'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:categories'))

    def form_invalid(self, form):
        data = {'error': True, 'response': form.errors}
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super(CategoryAdd, self).get_context_data(**kwargs)
        form = CategoryForm(self.request.GET)
        menus = ForumCategory.objects.filter(parent=None)
        context['form'] = form
        context['menus'] = menus
        return context


class CategoryDelete(AdminMixin, DeleteView):
    model = ForumCategory
    slug_field = 'slug'
    template_name = "dashboard/categories.html"
    success_url = '/forum/dashboard/categories/'

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:categories'))

    def post(self, request, *args, **kwargs):
        category = self.get_object()
        category.delete()
        return JsonResponse({'error': False, 'response': 'Successfully Deleted Category'})


class CategoryEdit(AdminMixin, UpdateView):
    model = ForumCategory
    form_class = CategoryForm
    template_name = "dashboard/category_add.html"
    context_object_name = 'category'

    def get_object(self):
        return get_object_or_404(ForumCategory, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super(CategoryEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        menu = form.save()
        if self.request.POST.get('parent'):
            menu.parent_id = self.request.POST.get('parent')
            menu.save()
        data = {'error': False, 'response': 'Successfully Edited Category'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:categories'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(CategoryEdit, self).get_context_data(**kwargs)
        form = CategoryForm(self.request.GET)
        menus = ForumCategory.objects.filter(parent=None)
        context['form'] = form
        context['menus'] = menus
        return context


class BadgeList(AdminMixin, ListView):
    model = Badge
    template_name = 'dashboard/badges.html'
    context_object_name = 'badges_list'

    def get_context_data(self, **kwargs):
        context = super(BadgeList, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        badges_list = self.model.objects.all()
        if request.POST.get('search_text', ''):
            badges_list = badges_list.filter(
                Q(title__icontains=request.POST.get('search_text')))
        per_page = request.POST.get("filter_per_page") if request.POST.get(
            "filter_per_page") else 10
        return render(request, self.template_name, {'badges_list': badges_list,
                                                    "per_page": per_page})


class DashboardTopicList(AdminMixin, ListView):
    template_name = 'dashboard/topics.html'
    context_object_name = "topic_list"

    def get_queryset(self):
        queryset = Topic.objects.all()
        search_text = self.request.POST.get('search_text')
        if search_text:
            queryset = queryset.filter(
                Q(title__icontains=search_text) | Q(created_by__username__icontains=search_text)
            )
        return queryset


class BadgeDetailView(AdminMixin, DetailView):
    model = Badge
    template_name = 'dashboard/view_badge.html'
    slug_field = "slug"
    context_object_name = 'badge'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])


class BadgeAdd(AdminMixin, CreateView):
    model = Badge
    form_class = BadgeForm
    template_name = "dashboard/badge_add.html"

    def get_form_kwargs(self):
        kwargs = super(BadgeAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        data = {'error': False, 'response': 'Successfully Created Badge'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:badges'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(BadgeAdd, self).get_context_data(**kwargs)
        form = BadgeForm(self.request.GET)
        context['form'] = form
        return context


class BadgeDelete(AdminMixin, DeleteView):
    model = Badge
    slug_field = 'slug'
    template_name = "dashboard/badges.html"
    success_url = '/forum/dashboard/badges/'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:badges'))

    def post(self, request, *args, **kwargs):
        badge = self.get_object()
        badge.delete()
        return JsonResponse({'error': False, 'response': 'Successfully Deleted Badge'})


class BadgeEdit(AdminMixin, UpdateView):
    model = Badge
    template_name = "dashboard/badge_add.html"
    form_class = BadgeForm
    context_object_name = 'badge'

    def get_object(self):
        return get_object_or_404(Badge, slug=self.kwargs['slug'])

    def get_form_kwargs(self):
        kwargs = super(BadgeEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.save()
        data = {'error': False, 'response': 'Successfully Edited Badge'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:badges'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(BadgeEdit, self).get_context_data(**kwargs)
        form = BadgeForm(self.request.GET)
        context['form'] = form
        return context


class UserList(AdminMixin, ListView):
    model = UserProfile
    template_name = 'dashboard/users.html'
    context_object_name = 'users_list'
    queryset = UserProfile.objects.filter()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        users_list = self.model.objects.all()
        if request.POST.get('search_text', ''):
            users_list = list(set(users_list.filter(
                user__email__icontains=request.POST.get('search_text')
            ) | users_list.filter(
                user__username__icontains=request.POST.get('search_text')
            )))
        per_page = request.POST.get("filter_per_page") if request.POST.get(
            "filter_per_page") else 10
        return render(request, self.template_name, {'users_list': users_list,
                                                    "per_page": per_page})


class DashboardUserEdit(AdminMixin, UpdateView):
    model = UserProfile
    template_name = "dashboard/edit_user.html"
    form_class = UserProfileForm
    context_object_name = 'user_profile'

    def get_object(self):
        return get_object_or_404(UserProfile, user_id=self.kwargs['user_id'])

    # def get_form_kwargs(self):
    #     kwargs = super(DashboardUserEdit, self).get_form_kwargs()
    #     kwargs.update({'user': self.request.user})
    #     return kwargs

    def form_valid(self, form):
        user_profile = form.save()
        user_profile.badges.clear()
        user_profile.badges.add(*form.cleaned_data['badges'])
        data = {'error': False, 'response': 'Successfully Edited User'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:users'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(DashboardUserEdit, self).get_context_data(**kwargs)
        form = UserProfileForm(self.request.GET)
        badges = Badge.objects.filter()
        context['form'] = form
        context['badges'] = badges
        context['user_profile'] = self.get_object()
        return context


class IndexView(FormView):
    template_name = 'forum/topic_list.html'
    form_class = RegisterForm

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        topics = Topic.objects.filter(status='Published')
        context['topic_list'] = topics
        return context

    def form_valid(self, form):
        user = User.objects.create(
            username=form.cleaned_data['username'], email=form.cleaned_data['email'])
        user.set_password(form.cleaned_data['password'])
        user.first_name = form.cleaned_data['first_name']
        user.is_active = True
        user.save()
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        UserProfile.objects.create(user=user, user_roles='Publisher')
        login(self.request, user)

        timeline_activity(user=user, content_object=user,
                          namespace='created on', event_type="user-create")

        data = {'error': False, 'response': 'Successfully Created Badge'}
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})


class ForumLoginView(FormView):
    template_name = 'forum/topic_list.html'
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        context = super(ForumLoginView, self).get_context_data(**kwargs)
        topics = Topic.objects.filter(status='Published')
        context['topic_list'] = topics
        return context

    def form_valid(self, form):
        login(self.request, form.get_user())
        data = {'error': False, 'response': 'Successfully user loggedin'}
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})


class TopicAdd(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = TopicForm
    template_name = "forum/new_topic.html"
    success_url = reverse_lazy('django_simple_forum:signup')

    def get_form_kwargs(self):
        kwargs = super(TopicAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        topic = form.save()
        if self.request.POST['sub_category']:
            topic.category_id = self.request.POST['sub_category']
        topic.save()
        if 'tags' in form.cleaned_data.keys() and form.cleaned_data['tags']:
            for tag in form.cleaned_data['tags'].split(','):
                if not Tags.objects.filter(slug=slugify(tag)):
                    each = Tags.objects.create(slug=slugify(tag), title=tag)
                    topic.tags.add(each)
                else:
                    each = Tags.objects.filter(slug=slugify(tag)).first()
                    topic.tags.add(each)
        # liked_users_ids = UserTopics.objects.filter(
        #     topic__category=topic.category, is_like=True).values_list('user', flat=True)
        # followed_users = UserTopics.objects.filter(
        #     topic__category=topic.category, is_followed=True).values_list('user', flat=True)
        # users = UserProfile.objects.filter(user_id__in=set(all_users))

        # for user in users:
        #     mto = [user.user.email]
        #     c = Context({'comment': comment, "user": user.user,
        #                  'topic_url': settings.HOST_URL + reverse('django_simple_forum:view_topic', kwargs={'slug': topic.slug}),
        #                  "HOST_URL": settings.HOST_URL})
        #     t = loader.get_template('emails/new_topic.html')
        #     subject = "New Topic For The Category" + (topic.category.title)
        #     rendered = t.render(c)
        #     mfrom = settings.DEFAULT_FROM_EMAIL
        #     Memail(mto, mfrom, subject, rendered)

        timeline_activity(user=self.request.user, content_object=self.request.user,
                          namespace='created topic on', event_type="topic-create")

        data = {'error': False, 'response': 'Successfully Created Topic'}
        return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(TopicAdd, self).get_context_data(**kwargs)
        form = TopicForm(self.request.GET)
        context['form'] = form
        context['status'] = STATUS
        context['categories'] = ForumCategory.objects.filter(
            is_active=True, is_votable=True, parent=None)
        context['sub_categories'] = ForumCategory.objects.filter(
            is_active=True, is_votable=True).exclude(parent=None)
        return context


class TopicUpdateView(CanUpdateTopicMixin, UpdateView):
    model = Topic
    form_class = TopicForm
    template_name = "forum/new_topic.html"

    def get_initial(self):
        initital = super(TopicUpdateView, self).get_initial();
        topic = self.get_object()
        tags = [tag.title for tag in topic.tags.all()]
        initital.update({
            "tags": ",".join(tags)    
        })
        return initital

    def form_valid(self, form):
        topic = self.get_object()
        old_tags = [tag.title for tag in topic.tags.all()]
        topic = form.save()
        tags_text = form.cleaned_data['tags']
        if tags_text:
            new_tags = tags_text.split(',')
            remove_tags = set(new_tags) - set(old_tags)
            for tag in new_tags:
                tag_slug = slugify(tag)
                if not Tags.objects.filter(slug=tag_slug).exists():
                    tag = Tags.objects.create(slug=tag_slug, title=tag)
                    topic.tags.add(tag)
                else:
                    tag = Tags.objects.filter(slug=tag_slug).first()
                    if tag.title in remove_tags:
                        topic.remove(tag)
                    else:
                        topic.tags.add(tag)
        topic.save()
        return JsonResponse({"error": False, "success_url": reverse('django_simple_forum:signup')})

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'errors': form.errors})


class TopicList(ListView):
    template_name = 'forum/topic_list.html'
    context_object_name = "topic_list"

    def get_queryset(self):
        if self.request.user.is_authenticated():
            query = Q(status='Published')|Q(created_by=self.request.user)
        else:
            query = Q(status='Published')
        queryset = Topic.objects.filter(query).order_by('-created_on')
        return queryset

class TopicView(TemplateView):
    template_name = 'forum/view_topic.html'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(TopicView, self).get_context_data(**kwargs)
        context['topic'] = self.get_object()
        # user_profile = get_object_or_404(UserProfile, user=self.request.user)
        # context['user_profile'] = user_profile
        suggested_topics = Topic.objects.filter(
            category=self.get_object().category).exclude(id=self.get_object().id)
        job_url = 'http://' + self.request.META['HTTP_HOST'] + reverse(
            'django_simple_forum:view_topic', kwargs={'slug': self.get_object().slug})
        try:
            minified_url = google_mini(job_url, settings.MINIFIED_URL)
        except:
            minified_url = job_url

        context['minified_url'] = minified_url
        context['suggested_topics'] = suggested_topics
        return context


class TopicDeleteView(CanUpdateTopicMixin, DeleteView):
    model = Topic
    template_name = "forum/topic_delete.html"
    success_url = reverse_lazy("django_simple_forum:topic_list")

    def get_object(self):
        if not hasattr(self, "object"):
            self.object = super(TopicDeleteView, self).get_object()
        return self.object

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            self.object = self.get_object() 
            self.object.delete()
            return JsonResponse({"error": False, "message": "deleted"})
        else:
            return super(TopicDeleteView, self).delete(request, *args, **kwargs)



def comment_mentioned_users_list(data):
    mentioned_users = data.split(',')
    mentioned_users_list = [user.strip('@') for user in mentioned_users]
    result = User.objects.filter(username__in=mentioned_users_list)
    return result


class CommentVoteUpView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        vote = comment.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="U")
            comment.votes.add(vote)
            comment.save()
            status = "up"
        elif vote and vote.type == "D":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})


class CommentVoteDownView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs.get("pk"))
        vote = comment.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="D")
            comment.votes.add(vote)
            comment.save()
            status = "down"
        elif vote and vote.type == "U":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})



class CommentAdd(LoginRequiredMixin, CreateView):
    model = Topic
    form_class = CommentForm
    template_name = 'forum/view_topic.html'

    def get_form_kwargs(self):
        kwargs = super(CommentAdd, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        comment = form.save()
        if self.request.POST['parent']:
            comment.parent_id = self.request.POST['parent']
            comment.save()
        if self.request.POST.get('mentioned_user', False):
            data = self.request.POST.get('mentioned_user')
            comment.mentioned = comment_mentioned_users_list(data)
            comment.save()

        for user in comment.topic.get_topic_users():
            mto = [user.user.email]
            c = {'comment': comment, "user": user.user,
                 'topic_url': settings.HOST_URL+reverse('django_simple_forum:view_topic', kwargs={'slug': comment.topic.slug}),
                 "HOST_URL": settings.HOST_URL}
            t = loader.get_template('emails/comment_add.html')
            subject = "New Comment For The Topic " + (comment.topic.title)
            rendered = t.render(c)
            mfrom = settings.DEFAULT_FROM_EMAIL
            Memail(mto, mfrom, subject, rendered, email_template_name=None, context=None)

        for user in comment.mentioned.all():
            mto = [user.user.email]
            c = Context({'comment': comment, "user": user.user,
                         'topic_url': settings.HOST_URL+reverse('django_simple_forum:view_topic', kwargs={'slug': comment.topic.slug}),
                         "HOST_URL": settings.HOST_URL})
            t = loader.get_template('emails/comment_mentioned.html')
            subject = "New Comment For The Topic " + (comment.topic.title)
            rendered = t.render(c)
            mfrom = settings.DEFAULT_FROM_EMAIL
            Memail(mto, mfrom, subject, rendered)

        timeline_activity(user=self.request.user, content_object=comment,
                          namespace='commented for the', event_type="comment-create")

        data = {'error': False, 'response': 'Successfully Created Topic'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:signup'))

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(CommentAdd, self).get_context_data(**kwargs)
        form = CommentForm(self.request.GET)
        context['form'] = form
        return context


class CommentEdit(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = "dashboard/edit_user.html"
    form_class = CommentForm
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def form_valid(self, form):
        comment = self.get_object()
        if self.request.user == comment.commented_by:
            self.get_object().mentioned.all().delete()
            comment = form.save()
            if self.request.POST['parent']:
                comment.parent_id = self.request.POST['parent']
                comment.save()
            if self.request.POST.get('mentioned_user', False):
                data = self.request.POST.get('mentioned_user')
                comment.mentioned = comment_mentioned_users_list(data)
                comment.save()
            timeline_activity(user=self.request.user, content_object=comment,
                              namespace='commented for the', event_type="comment-create")
            data = {'error': False, 'response': 'Successfully Edited User'}
        else:
            data = {
                'error': True, 'response': 'Only Commented User Can edit this comment'}
        return JsonResponse(data)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:users'))

    def get_form_kwargs(self):
        kwargs = super(CommentEdit, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})

    def get_context_data(self, **kwargs):
        context = super(CommentEdit, self).get_context_data(**kwargs)
        form = CommentForm(self.request.GET)
        context['form'] = form
        return context


class CommentDelete(LoginRequiredMixin, DeleteView):
    model = Comment
    slug_field = 'comment_id'
    template_name = "dashboard/categories.html"

    def get_object(self):
        return get_object_or_404(Comment, id=self.kwargs['comment_id'])

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:categories'))

    def post(self, request, *args, **kwargs):
        comment = self.get_object()
        if self.request.user == comment.commented_by:
            comment.delete()
            return JsonResponse({'error': False, 'response': 'Successfully Deleted Your Comment'})
        else:
            return JsonResponse({'error': False, 'response': 'Only commented user can delete this comment'})


class TopicLike(LoginRequiredMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:categories'))

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        user_topics = UserTopics.objects.filter(user=request.user, topic=topic)
        if user_topics:
            user_topic = user_topics[0]
        else:
            user_topic = UserTopics.objects.create(
                user=request.user, topic=topic)
        if user_topic.is_like:
            user_topic.is_like = False
            topic.no_of_likes = topic.no_of_likes - 1
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='unlike the', event_type="unlike-topic")
        else:
            user_topic.is_like = True
            topic.no_of_likes = topic.no_of_likes + 1
            timeline_activity(
                user=self.request.user, content_object=topic, namespace='like the', event_type="like-topic")
        user_topic.save()
        topic.save()

        return JsonResponse({'error': False, 'response': 'Successfully Deleted Category',
                             'is_like': user_topic.is_like, 'no_of_likes': topic.no_of_likes,
                             'no_of_users': topic.get_topic_users().count()})


class ForumCategoryList(ListView):
    queryset = ForumCategory.objects.filter(
        is_active=True, is_votable=True).order_by('-created_on')
    template_name = 'forum/categories.html'
    context_object_name = "categories"
    paginate_by = '10'


class ForumTagsList(ListView):
    queryset = Tags.objects.filter()
    template_name = 'forum/tags.html'
    context_object_name = "tags"
    paginate_by = '10'

    def post(self, request, *args, **kwargs):
        tags = self.queryset
        if str(request.POST.get('alphabet_value')) != 'all':
            tags = tags.filter(
                title__istartswith=request.POST.get('alphabet_value'))
        return render(request, self.template_name, {'tags': tags})


class ForumBadgeList(ListView):
    queryset = Tags.objects.filter()
    template_name = 'forum/badges.html'
    context_object_name = "badges_list"
    paginate_by = '10'

    def post(self, request, *args, **kwargs):
        tags = self.queryset
        if str(request.POST.get('alphabet_value')) != 'all':
            tags = tags.filter(
                title__istartswith=request.POST.get('alphabet_value'))
        return render(request, self.template_name, {'tags': tags})


class ForumCategoryView(ListView):
    template_name = 'forum/topic_list.html'

    def get_queryset(self, queryset=None):
        if self.request.user.is_authenticated():
            query = Q(status="Published")|Q(created_by=self.request.user)
        else:
            query = Q(status="Published")
        category = get_object_or_404(ForumCategory, slug=self.kwargs.get("slug"))
        topics = category.topic_set.filter(query) 
        return topics


class ForumTagsView(TemplateView):
    template_name = 'forum/topic_list.html'

    def get_context_data(self, **kwargs):
        tag = get_object_or_404(Tags, slug=kwargs.get("slug"))
        context = super(ForumTagsView, self).get_context_data(**kwargs)
        topics = tag.get_topics()
        context['topic_list'] = topics
        return context


class TopicDetail(AdminMixin, TemplateView):
    template_name = 'dashboard/view_topic.html'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(TopicDetail, self).get_context_data(**kwargs)
        context['topic'] = self.get_object()
        return context


class TopicStatus(AdminMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        if topic.status == 'Draft':
            topic.status = 'Published'
        elif topic.status == 'Published':
            topic.status = 'Draft'
        else:
            topic.status = 'Disabled'
        topic.save()
        return JsonResponse({'error': False, 'response': 'Successfully Updated Topic Status'})


class DashboardUserDelete(AdminMixin, DeleteView):
    model = User
    template_name = "dashboard/topic.html"
    slug_name = "user_id"

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:users'))

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        user.delete()
        return JsonResponse({'error': False, 'response': 'Successfully Deleted User'})


class UserStatus(AdminMixin, View):
    model = User
    slug_name = "user_id"

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:users'))

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_active:
            user.is_active = False
        else:
            user.is_active = True
        user.save()
        return JsonResponse({'error': False, 'response': 'Successfully Updated User Status'})


class UserDetail(AdminMixin, TemplateView):
    template_name = 'dashboard/view_user.html'

    def get_object(self):
        return get_object_or_404(User, id=self.kwargs['user_id'])

    def get_context_data(self, **kwargs):
        context = super(UserDetail, self).get_context_data(**kwargs)
        context['user'] = self.get_object()
        context['user_profile'] = get_object_or_404(
            UserProfile, user=self.get_object())
        user_topics = UserTopics.objects.filter(user=self.get_object())
        context['user_topics'] = user_topics
        context['user_liked_topics'] = user_topics.filter(is_like=True)
        context['user_followed_topics'] = user_topics.filter(is_followed=True)
        context['user_created_topics'] = Topic.objects.filter(
            created_by=self.get_object())
        return context


class TopicFollow(LoginRequiredMixin, View):
    model = Topic
    slug_field = 'slug'

    def get_object(self):
        return get_object_or_404(Topic, slug=self.kwargs['slug'])

    def post(self, request, *args, **kwargs):
        topic = self.get_object()
        user_topics = UserTopics.objects.filter(user=request.user, topic=topic)
        if user_topics:
            user_topic = user_topics[0]
        else:
            user_topic = UserTopics.objects.create(
                user=request.user, topic=topic)
        if user_topic.is_followed:
            user_topic.is_followed = False
            user_topic.followed_on = datetime.now()
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='unfollow the', event_type="unfollow-topic")
        else:
            user_topic.is_followed = True
            user_topic.followed_on = datetime.now()
            timeline_activity(user=self.request.user, content_object=topic,
                              namespace='follow the', event_type="follow-topic")
        user_topic.save()
        return JsonResponse({'error': False, 'response': 'Successfully Followed the topic',
                             'is_followed': user_topic.is_followed})


class TopicVoteUpView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, slug=kwargs.get("slug"))
        vote = topic.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="U")
            topic.votes.add(vote)
            topic.save()
            status = "up"
        elif vote and vote.type == "D":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})


class TopicVoteDownView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, slug=kwargs.get("slug"))
        vote = topic.votes.filter(user=request.user).first()
        if not vote:
            vote = Vote.objects.create(user=request.user, type="D")
            topic.votes.add(vote)
            topic.save()
            status = "down"
        elif vote and vote.type == "U":
            vote.delete()
            status = "removed"
        else:
            status = "neutral"
        return JsonResponse({"status": status})


class ChangePassword(AdminMixin, FormView):
    template_name = 'dashboard/change_password.html'
    form_class = ChangePasswordForm

    def form_valid(self, form):
        user = self.request.user
        if not check_password(self.request.POST['oldpassword'], user.password):
            return JsonResponse({
                'error': True,
                'response': {'oldpassword': 'Invalid old password'}
            })
        if self.request.POST['newpassword'] != self.request.POST['retypepassword']:
            return JsonResponse({
                'error': True,
                'response': {'newpassword': 'New password and Confirm Passwords did not match'}
            })
        user.set_password(self.request.POST['newpassword'])
        user.save()
        return JsonResponse({'error': False, 'message': 'Password changed successfully'})

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'forum/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        user_role = "Publisher"
        if self.request.user.is_superuser:
            user_role = "Admin"
        user_profile, _ = UserProfile.objects.get_or_create(user=self.request.user, user_roles=user_role)
        context['user_profile'] = user_profile
        return context


class ProfileView(TemplateView):
    template_name = 'forum/profile.html'
    slug_field = 'user_name'

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        user_profile = get_object_or_404(
            UserProfile, user__username=self.kwargs['user_name'])
        context['user_profile'] = user_profile
        return context


class UserProfilePicView(LoginRequiredMixin, View):
    model = UserProfile

    def get_object(self):
        return get_object_or_404(UserProfile, user_id=self.request.user.id)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:user_profile'))

    def post(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if 'profile_pic' in request.FILES:
            user_profile.profile_pic = request.FILES['profile_pic']
            user_profile.save()
            return JsonResponse({'error': False, 'response': 'Successfully uploaded'})
        else:
            return JsonResponse({'error': True, 'response': 'Please Upload Your Profile pic'})


class UserSettingsView(LoginRequiredMixin, View):
    model = UserProfile

    def get_object(self):
        return get_object_or_404(UserProfile, user_id=self.request.user.id)

    def get_success_url(self):
        return redirect(reverse('django_simple_forum:user_profile'))

    def post(self, request, *args, **kwargs):
        user_profile = self.get_object()
        if not user_profile.send_mailnotifications:
            user_profile.send_mailnotifications = True
        else:
            user_profile.send_mailnotifications = False
        user_profile.save()
        return JsonResponse({'error': False, 'response': 'You have successfully uploaded the settings',
                             "send_mailnotifications": user_profile.send_mailnotifications})


class UserDetailView(TemplateView):
    template_name = 'forum/profile.html'
    slug_field = 'user_name'

    def get_object(self):
        return get_object_or_404(UserProfile, user__username=self.kwargs['user_name'])

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['user_profile'] = self.get_object()
        return context


def facebook_login(request):
    if 'code' in request.GET:
        accesstoken = get_access_token_from_code(request.GET['code'], request.scheme + '://' + request.META[
                                                 'HTTP_HOST'] + reverse('django_simple_forum:facebook_login'), settings.FB_APP_ID, settings.FB_SECRET)
        if 'error' in accesstoken.keys():
            return render(request, '404.html')
        graph = GraphAPI(accesstoken['access_token'])
        accesstoken = graph.extend_access_token(
            settings.FB_APP_ID, settings.FB_SECRET)['accesstoken']
        profile = graph.get_object("me")
        hometown = profile['hometown'][
            'name'] if 'hometown' in profile.keys() else ''
        location = profile['location'][
            'name'] if 'location' in profile.keys() else ''
        bday = datetime.strptime(profile['birthday'], '%m/%d/%Y').strftime(
            '%Y-%m-%d') if 'birthday' in profile.keys() else '1970-09-09'
        profile_pic = "https://graph.facebook.com/" + \
            profile['id'] + "/picture?type=large"

        if 'email' in profile.keys():
            if User.objects.filter(username=profile['email'], email=profile['email']):
                user = User.objects.filter(
                    username=profile['email'], email=profile['email']).first()
            else:
                user, created = User.objects.get_or_create(
                    username=profile['email'],
                    email=profile['email'],
                    first_name=profile['first_name'],
                    last_name=profile['last_name'],
                    last_login=datetime.now()
                )
            user_profile = UserProfile.objects.filter(user=user).last()
            if not user_profile:
                user_profile = UserProfile.objects.create(
                    user=user, user_roles="Publisher")
            name = urlparse(profile_pic).path.split('/')[-1]
            # content = urllib.urlretrieve(profile_pic)
            content = urllib.request.urlretrieve(profile_pic)
            user_profile.profile_pic.save(
                name, File(open(content[0], 'rb')), save=True)
            user_profile.save()

            fb = Facebook.objects.filter(user=user).last()
            if not fb:
                Facebook.objects.create(
                    user=user,
                    facebook_url=profile['link'],
                    facebook_id=profile['id'],
                    first_name=profile['first_name'],
                    last_name=profile['last_name'],
                    verified=profile['verified'],
                    name=profile['name'],
                    language=profile['locale'],
                    hometown=hometown,
                    email=profile['email'],
                    gender=profile['gender'],
                    dob=bday,
                    location=location,
                    timezone=profile['timezone'],
                    accesstoken=accesstoken
                )
            else:
                fb.user = user
                fb.facebook_url = profile['link']
                fb.facebook_id = profile['id']
                fb.first_name = profile['first_name']
                fb.last_name = profile['last_name']
                fb.verified = profile['verified']
                fb.name = profile['name']
                fb.language = profile['locale']
                fb.hometown = hometown
                fb.email = profile['email']
                fb.gender = profile['gender']
                fb.dob = bday
                fb.location = location
                fb.timezone = profile['timezone']
                fb.accesstoken = accesstoken
                fb.save()
            if not request.user.is_authenticated():
                if not hasattr(user, 'backend'):
                    for backend in settings.AUTHENTICATION_BACKENDS:
                        if user == load_backend(backend).get_user(user.pk):
                            user.backend = backend
                            break
                if hasattr(user, 'backend'):
                    login(request, user)
            return HttpResponseRedirect('/forum/')
        else:
            return render(request, '404.html')
    elif 'error' in request.GET:
        print(request.GET)
    else:
        rty = "https://graph.facebook.com/oauth/authorize?client_id=" + settings.FB_APP_ID + "&redirect_uri=" + request.scheme + '://' + request.META['HTTP_HOST'] + reverse(
            'django_simple_forum:facebook_login') + "&scope=manage_pages,read_stream, user_about_me, user_birthday, user_location, user_work_history, user_hometown, user_website, email, user_likes, user_groups"
        return HttpResponseRedirect(rty)


def google_login(request):
    if 'code' in request.GET:
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': request.scheme + "://" + request.META['HTTP_HOST'] + reverse('django_simple_forum:google_login'),
            'client_id': settings.GP_CLIENT_ID,
            'client_secret': settings.GP_CLIENT_SECRET
        }
        info = requests.post(
            "https://accounts.google.com/o/oauth2/token", data=params)
        info = info.json()
        url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        params = {'access_token': info['access_token']}
        kw = dict(params=params, headers={}, timeout=60)
        response = requests.request('GET', url, **kw)
        user_document = response.json()
        link = "https://plus.google.com/" + user_document['id']
        picture = user_document[
            'picture'] if 'picture' in user_document.keys() else ""
        dob = user_document[
            'birthday'] if 'birthday' in user_document.keys() else ""
        gender = user_document[
            'gender'] if 'gender' in user_document.keys() else ""
        link = user_document[
            'link'] if 'link' in user_document.keys() else link

        if request.user.is_authenticated():
            user = request.user
        else:
            user = User.objects.filter(email=user_document['email']).first()
        if user:
            user.first_name = user_document['name']
            user.last_name = user_document['family_name']
            user.save()
        else:
            user = User.objects.create(
                username=user_document['email'],
                email=user_document['email'],
                first_name=user_document['name'],
                last_name=user_document['family_name'],
            )
        user.save()

        user_profile = UserProfile.objects.filter(user=user).last()
        if not user_profile:
            user_profile = UserProfile.objects.create(
                user=user, user_roles="Publisher")
        google, created = Google.objects.get_or_create(user=user)
        google.user = user
        google.google_url = link
        google.verified_email = user_document['verified_email']
        google.google_id = user_document['id']
        google.family_name = user_document['family_name']
        google.name = user_document['name']
        google.given_name = user_document['given_name']
        google.dob = dob
        google.email = user_document['email']
        google.gender = gender
        google.picture = picture
        google.save()

        if not request.user.is_authenticated():
            if not hasattr(user, 'backend'):
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.pk):
                        user.backend = backend
                        break
            if hasattr(user, 'backend'):
                login(request, user)
        return HttpResponseRedirect('/forum/')
    else:
        rty = "https://accounts.google.com/o/oauth2/auth?client_id=" + settings.GP_CLIENT_ID\
              + "&response_type=code"
        rty += "&scope=https://www.googleapis.com/auth/userinfo.profile \
               https://www.googleapis.com/auth/userinfo.email&redirect_uri=" + request.scheme\
               + "://" + request.META['HTTP_HOST'] + reverse('django_simple_forum:google_login')\
               + "&state=1235dfghjkf123"
        return HttpResponseRedirect(rty)


def get_mentioned_user(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    if request.method == 'GET':
        topic_users = topic.get_topic_users()
        list_data = []
        for user in topic_users:
            data = {}
            data['username'] = user.user.email.split('@')[0]
            # data['avatar'] = user.profile_pic.url if user.profile_pic else ''
            data['fullname'] = user.user.email
            list_data.append(data)
    return JsonResponse({'data': list_data})


def comment_mentioned_users_list(data):
    mentioned_users = data.split(',')
    mentioned_users_list = [user.strip('@') for user in mentioned_users]
    result = User.objects.filter(username__in=mentioned_users_list)
    return result


class UserChangePassword(LoginRequiredMixin, FormView):
    template_name = 'forum/topic_list.html'
    form_class = UserChangePasswordForm

    def form_valid(self, form):
        user = self.request.user
        if self.request.POST['newpassword'] != self.request.POST['retypepassword']:
            return JsonResponse({
                'error': True,
                'response': {
                    'newpassword': 'New password and Confirm Passwords did not match'
                }
            })
        user.set_password(self.request.POST['newpassword'])
        user.save()
        return JsonResponse({
            'error': False,
            'message': 'Password changed successfully'
        })

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})


class ForgotPasswordView(FormView):
    template_name = 'form/topic_list.html'
    form_class = ForgotPasswordForm

    def form_valid(self, form):
        user = User.objects.filter(email=self.request.POST.get('email'))
        if user:
            user = user[0]
            subject = "Password Reset"
            password = get_random_string(6)
            message = '<p>Your Password for the forum account is <strong>'+password + \
                '</strong></p><br/><p>Use this credentials to login into <a href="' + \
                settings.HOST_URL + '/forum/">forum</a></p>'
            to = user.email
            from_email = settings.DEFAULT_FROM_EMAIL
            Memail([to], from_email, subject, message, email_template_name=None, context=None)
            user.set_password(password)
            user.save()
            data = {
                "error": False, "response": "An Email is sent to the entered email id"}
            return JsonResponse(data)
        else:
            data = {
                "error": True, "message": "User With this email id doesn't exists!!!"}
            return JsonResponse(data)

    def form_invalid(self, form):
        return JsonResponse({'error': True, 'response': form.errors})
