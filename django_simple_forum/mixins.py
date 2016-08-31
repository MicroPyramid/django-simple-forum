from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth import logout


class AdminMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_superuser:
            return HttpResponseRedirect(reverse('django_simple_forum:topic_list'))
        return super(AdminMixin, self).dispatch(request, *args, **kwargs)


class UserMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if user:
            if user.is_active:
                return super(UserMixin, self).dispatch(request, *args, **kwargs)
            else:
                logout(self.request)
        return HttpResponseRedirect(reverse('django_simple_forum:topic_list'))
