from django.test import TestCase, Client
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_simple_forum.models import ForumCategory, Badge


class TestLoginView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com'
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_user_login(self):
        url = reverse('django_simple_forum:dashboard')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/dashboard_login.html')
        # invalid password
        data = {'username': self.user.email, 'password': 'invalid'}
        response = self.client.post(url, data)
        self.assertTrue('error' in response.json().keys())
        # not superuser
        data = {'username': self.user.email, 'password': self.password}
        response = self.client.post(url, data)
        self.assertTrue('error' in response.json().keys())
        # super user
        self.user.is_superuser = True
        self.user.save()
        data = {'username': self.user.email, 'password': self.password}
        response = self.client.post(url, data)
        self.assertEqual(response.json().get('error'), False)
        # already loggedin user(super user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # already loggedin user(normal user)
        self.user.is_superuser = False
        self.user.save()
        response = self.client.get(url)
        self.assertRedirects(response, reverse('django_simple_forum:topic_list'))


class TestLogoutView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com'
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_user_login(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:out')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.user.is_superuser = True
        self.user.save()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class TestCategoryListView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_category_list(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:categories')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/categories.html')
        response = self.client.post(url, {'is_active': 'True', 'search_text': 'text'})
        self.assertTemplateUsed(response, 'dashboard/categories.html')


class TestCategoryDetailView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.category = ForumCategory.objects.create(
            created_by=self.user,
            title='Python',
            is_active=True,
            slug='python',
            description='dynamic programming language'
        )

    def test_category_detail(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:view_category', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/view_category.html')


class TestCategoryAddView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.category = ForumCategory.objects.create(
            created_by=self.user,
            title='Python',
            is_active=True,
            slug='python',
            description='dynamic programming language'
        )

    def test_category_add(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:add_category')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/category_add.html')
        # post empty data
        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        data = {
            'title': 'django',
            'is_active': True,
            'slug': 'django',
            'description': 'dynamic programming language',
            'color': '#992399',
            'parent': self.category.id
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))
        self.assertEquals(ForumCategory.objects.all().count(), 2)


class TestCategoryDeleteView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.category = ForumCategory.objects.create(
            created_by=self.user,
            title='Python',
            is_active=True,
            slug='python',
            description='dynamic programming language'
        )

    def test_category_delete(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:delete_category', kwargs={'slug': self.category.slug})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestCategoryEditView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.category = ForumCategory.objects.create(
            created_by=self.user,
            title='Python',
            is_active=True,
            slug='python',
            description='dynamic programming language'
        )

    def test_category_update(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:edit_category', kwargs={'slug': self.category.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/category_add.html')
        # post empty data
        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        data = {
            'title': 'django',
            'is_active': True,
            'slug': 'django',
            'description': 'dynamic programming language',
            'color': '#992399',
            'parent': self.category.id
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))
        self.assertEquals(ForumCategory.objects.all().count(), 1)


class TestBadgeListView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_badge_list(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:badges')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/badges.html')
        response = self.client.post(url, {'search_text': 'text'})
        self.assertTemplateUsed(response, 'dashboard/badges.html')


class TestDashboardTopicListView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_topic_list(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topics')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/topics.html')


class TestBadgeDetailView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.badge = Badge.objects.create(
            title='Developer',
            slug='developer'
        )

    def test_badge_detail(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:view_badge', kwargs={'slug': self.badge.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/view_badge.html')
