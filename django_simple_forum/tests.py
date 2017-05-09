from django.test import TestCase, Client
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django_simple_forum.models import (
    ForumCategory, Badge, UserProfile, Topic, Comment, Tags
)


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


class TestBadgeAddView(TestCase):

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

    def test_badge_create(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:add_badge')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/badge_add.html')

        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'title': 'Developer'})
        self.assertFalse(response.json().get('error'))
        self.assertEqual(Badge.objects.count(), 1)


class TestBadgeDeleteView(TestCase):

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

    def test_badge_delete(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:delete_badge', kwargs={'slug': self.badge.slug})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestBadgeEditView(TestCase):

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

    def test_badge_edit(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:edit_badge', kwargs={'slug': self.badge.slug})
        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'title': 'software'})
        self.assertFalse(response.json().get('error'))


class TestUserListView(TestCase):

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

    def test_users_list(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:users')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/users.html')
        response = self.client.post(url, {'search_text': 'text'})
        self.assertTemplateUsed(response, 'dashboard/users.html')


class TestDashboardUserEditView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
            is_superuser=True
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()
        self.badge = Badge.objects.create(
            title='Developer',
            slug='developer'
        )

    def test_user_edit(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:edit_user', kwargs={'user_id': self.user.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/edit_user.html')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'badges': [self.badge.id]})
        self.assertFalse(response.json().get('error'))


class TestIndexView(TestCase):

    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        url = reverse('django_simple_forum:signup')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/topic_list.html')
        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'password': 'secret', 'username': 'ravi@micropyramid.com'})
        self.assertFalse(response.json().get('error'))


class TestForumLoginView(TestCase):

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

    def test_forum_login(self):
        url = reverse('django_simple_forum:user_login')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/topic_list.html')
        response = self.client.post(url, {})
        response = self.client.post(url, {})
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'password': self.password, 'username': self.user.email})
        self.assertFalse(response.json().get('error'))


class TestTopicAddView(TestCase):

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

    def test_topic_add(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:new_topic')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/new_topic.html')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        data = {
            'title': 'lists',
            'category': self.category.id,
            'sub_category': self.category.id,
            'description': 'desc'
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestTopicUpdateView(TestCase):

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

        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_update(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topic_update', kwargs={"slug": self.topic.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/new_topic.html')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        data = {
            'title': 'django forms',
            'category': self.category.id,
            'description': 'desc'
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestTopicListView(TestCase):

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
        url = reverse('django_simple_forum:topic_list')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/topic_list.html')


class TestTopicView(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_detail(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:view_topic', kwargs={'slug': self.topic.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/view_topic.html')


class TestTopicDeleteView(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_delete(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:delete_topic', kwargs={'slug': self.topic.slug})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 302)


class TestCommentAdd(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )
        self.comment = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
        )
        _ = UserProfile.objects.create(
            user=self.user,
        )

    def test_comment_add(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:new_comment')
        # response = self.client.get(url)
        # self.assertTemplateUsed(response, 'forum/view_topic.html')
        data = {
            'topic': self.topic.id,
            'comment': 'test comment',
            'parent': self.comment.id
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestCommentEditView(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )
        self.comment = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
            comment='test comment'
        )
        self.comment_child = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
            comment='test comment',
            parent=self.comment
        )

    def test_comment_edit(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:comment_edit', kwargs={'comment_id': self.comment_child.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/edit_user.html')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        data = {
            'topic': self.topic.id,
            'comment': 'new comment',
            'parent': self.comment.id
        }
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestCommentDelete(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )
        self.comment = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
            comment='test comment'
        )

    def test_comment_delete(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:comment_delete', kwargs={'comment_id': self.comment.id})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestTopicLike(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_like(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:like_topic', kwargs={'slug': self.topic.slug})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestForumCategoryList(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
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

    def test_forum_category_list(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:forum_categories')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/categories.html')


class TestForumTagsListView(TestCase):

    def setUp(self):
        self.client = Client()

    def test_forum_tags_list(self):
        url = reverse('django_simple_forum:forum_tags')
        response = self.client.post(url, {'alphabet_value': 'text'})
        self.assertTemplateUsed(response, 'forum/tags.html')


class TestForumBadgeListView(TestCase):

    def setUp(self):
        self.client = Client()

    def test_forum_badges_list(self):
        url = reverse('django_simple_forum:forum_badges')
        response = self.client.post(url, {'alphabet_value': 'text'})
        self.assertTemplateUsed(response, 'forum/badges.html')


class TestForumCategoryView(TestCase):

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

    def test_forum_badges_list(self):
        url = reverse(
            'django_simple_forum:forum_category_detail',
            kwargs={'slug': self.category.slug}
        )
        response = self.client.get(url, {'alphabet_value': 'text'})
        self.assertTemplateUsed(response, 'forum/topic_list.html')


class TestForumTagsView(TestCase):

    def setUp(self):
        self.client = Client()
        self.tag = Tags.objects.create(
            title='django-forms',
            slug='django-forms'
        )

    def test_forum_tags(self):
        url = reverse('django_simple_forum:forum_tags_detail', kwargs={'slug': self.tag.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/topic_list.html')


class TestTopicDetail(TestCase):

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

        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_detail(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topic_detail', kwargs={'slug': self.topic.slug})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/view_topic.html')


class TestTopicStatus(TestCase):

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

        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_status_change(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topic_status', kwargs={'slug': self.topic.slug})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestDashboardUserDelete(TestCase):

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
        self.user2 = User.objects.create(
            first_name='Santharao',
            last_name='N',
            email='santharao@micropyramid.com',
            username='santharao@micropyramid.com',
        )

    def test_user_delete(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:delete_user', kwargs={'user_id': self.user2.id})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestUserStatusView(TestCase):

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
        self.user2 = User.objects.create(
            first_name='Santharao',
            last_name='N',
            email='santharao@micropyramid.com',
            username='santharao@micropyramid.com',
        )

    def test_user_status(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_status', kwargs={'user_id': self.user2.id})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestUserDetailView(TestCase):

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
        self.user2 = User.objects.create(
            first_name='Santharao',
            last_name='N',
            email='santharao@micropyramid.com',
            username='santharao@micropyramid.com',
        )
        _ = UserProfile.objects.create(
            user=self.user2,
        )

    def test_user_details(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_detail', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/view_user.html')


class TestTopicFollow(TestCase):

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

        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_follow(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:follow_topic', kwargs={'slug': self.topic.slug})
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestTopicVoteUpView(TestCase):

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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_vote_up(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topic_vote_up', kwargs={'slug': self.topic.slug})
        response = self.client.get(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.get(url)
        self.assertFalse(response.json().get('error'))


class TestTopicVoteDownView(TestCase):

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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )

    def test_topic_vote_down(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:topic_vote_down', kwargs={'slug': self.topic.slug})
        response = self.client.get(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.get(url)
        self.assertFalse(response.json().get('error'))


class TestChangePasswordView(TestCase):

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

    def test_change_password(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:change_password')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'dashboard/change_password.html')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        data = {
            'newpassword': 'secret123',
            'retypepassword': 'secret123'
        }
        response = self.client.post(url, data)
        self.assertTrue(response.json().get('error'))
        data['newpassword'] = 'secret12344'
        response = self.client.post(url, data)
        self.assertTrue(response.json().get('error'))
        data.update({
            'oldpassword': self.password,
            'newpassword': 'secret123'
        })
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestUserProfileView(TestCase):

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

    def test_user_profile(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_profile')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/profile.html')


class TestProfileView(TestCase):

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
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_profile(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:view_profile', kwargs={'user_name': self.user.username})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/profile.html')


class TestUserProfilePicView(TestCase):

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
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_profile_pic(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_profile_pic')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))


class TestUserSettingsView(TestCase):

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
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_user_settings(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_settings')
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))
        response = self.client.post(url)
        self.assertFalse(response.json().get('error'))


class TestBlogUserDetailView(TestCase):

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
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_user_detail(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_details', kwargs={'user_name': self.user.username})
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'forum/profile.html')


class ForgotPasswordView(TestCase):

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

    def test_forgot_password(self):
        url = reverse('django_simple_forum:forgot_password')
        response = self.client.post(url)
        self.assertTrue(response.json().get('error'))
        response = self.client.post(url, {'email': self.user.email})
        self.assertFalse(response.json().get('error'))


class TestUserChangePassword(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
        )
        self.password = 'secret'
        self.user.set_password(self.password)
        self.user.save()

    def test_user_change_password(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:user_change_password')
        response = self.client.post(url)
        data = {
            'newpassword': 'secret123',
            'retypepassword': 'secret1234',
        }
        response = self.client.post(url, data)
        self.assertTrue(response.json().get('error'))
        data.update({
            'retypepassword': 'secret123',
        })
        response = self.client.post(url, data)
        self.assertFalse(response.json().get('error'))


class TestMentionedUser(TestCase):

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

        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )
        self.comment = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
        )

    def test_get_mentioned_user(self):
        url = reverse('django_simple_forum:get_mentioned_user', kwargs={'topic_id': self.topic.id})
        response = self.client.get(url)
        self.assertEqual(len(response.json().get('data')), 1)


class TestCommentVoteUpView(TestCase):

    def setUp(self):
        self.client = Client(HTTP_HOST="django-forum.com")
        self.user = User.objects.create(
            first_name='Ravi',
            last_name='G',
            email='ravi@micropyramid.com',
            username='ravi@micropyramid.com',
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
        self.topic = Topic.objects.create(
            title="django",
            slug='django',
            description="web framework",
            created_by=self.user,
            status='Draft',
            category=self.category
        )
        self.comment = Comment.objects.create(
            commented_by=self.user,
            topic=self.topic,
            comment="new comment"
        )

    def test_comment_vote_up(self):
        login = self.client.login(username=self.user.email, password=self.password)
        self.assertTrue(login)
        url = reverse('django_simple_forum:comment_vote_up', kwargs={'pk': self.comment.id})
        response = self.client.get(url)
        self.assertEqual(response.json().get('status'), 'up')
        response = self.client.get(url)
        self.assertEqual(response.json().get('status'), 'neutral')
