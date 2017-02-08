from django.shortcuts import redirect, get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import logout
from django_simple_forum.models import Topic


class AdminMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_superuser:
            return redirect(reverse('django_simple_forum:topic_list'))
        return super(AdminMixin, self).dispatch(request, *args, **kwargs)


class CanUpdateTopicMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_anonymous():
            return redirect(reverse("django_simple_forum:topic_list"))
        pk = kwargs.get("slug")
        self.object = get_object_or_404(Topic, slug=pk)
        if request.user != self.object.created_by and not request.user.is_staff:
            return redirect(reverse("django_simple_forum:topic_list"))
        return super(CanUpdateTopicMixin, self).dispatch(request, *args, **kwargs)


class LoginRequiredMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated():
            if user.is_active:
                return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
            else:
                logout(self.request)
        return redirect(reverse('django_simple_forum:topic_list'))
