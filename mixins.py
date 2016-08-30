from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse


class AdminMixin(object):

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not user.is_superuser:
            return HttpResponseRedirect(reverse('django_simple_forum:topic_list'))
        return super(AdminMixin, self).dispatch(request, *args, **kwargs)
