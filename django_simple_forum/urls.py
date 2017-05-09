from django.conf.urls import url
from . import  views

urlpatterns = [
    url(r'^$', views.TopicList.as_view(), name="topic_list"),
    url(r'^register/$', views.IndexView.as_view(), name="signup"),
    url(r'^forum/login/$', views.ForumLoginView.as_view(), name="user_login"),
    url(r'^fb_login/$', views.facebook_login, name="facebook_login"),
    url(r'^gp_login/$', views.google_login, name="google_login"),

    url(r'^topic/add/$', views.TopicAdd.as_view(), name="new_topic"),
    url(r'^topic/(?P<slug>[-\w]+)/update/$', views.TopicUpdateView.as_view(), name="topic_update"),
    url(r'^topic/view/(?P<slug>[-\w]+)/$', views.TopicView.as_view(), name="view_topic"),
    url(r'^topic/like/(?P<slug>[-\w]+)/$', views.TopicLike.as_view(), name="like_topic"),
    url(r'^topic/follow/(?P<slug>[-\w]+)/$', views.TopicFollow.as_view(), name="follow_topic"),
    url(r'^topic/votes/(?P<slug>[-\w]+)/up/$', views.TopicVoteUpView.as_view(), name="topic_vote_up"),
    url(r'^topic/votes/(?P<slug>[-\w]+)/down/$', views.TopicVoteDownView.as_view(), name="topic_vote_down"),

    url(r'^mentioned-users/(?P<topic_id>[-\w]+)/$', views.get_mentioned_user, name="get_mentioned_user"),
    url(r'^user/profile/(?P<user_name>[a-zA-Z0-9_.-@]+)/$', views.ProfileView.as_view(), name="view_profile"),
    url(r'^change-password/$', views.UserChangePassword.as_view(), name="user_change_password"),
    url(r'^forgot-password/$', views.ForgotPasswordView.as_view(), name="forgot_password"),
    url(r'^comment/delete/(?P<comment_id>[-\w]+)/$',
        views.CommentDelete.as_view(), name="comment_delete"),
    url(r'^comment/edit/(?P<comment_id>[-\w]+)/$', views.CommentEdit.as_view(), name="comment_edit"),

    url(r'^categories/$', views.ForumCategoryList.as_view(), name="forum_categories"),
    url(r'^tags/$', views.ForumTagsList.as_view(), name="forum_tags"),
    url(r'^badges/$', views.ForumBadgeList.as_view(), name="forum_badges"),
    url(r'^profile/$', views.UserProfileView.as_view(), name="user_profile"),
    url(r'^upload/profile-pic/$', views.UserProfilePicView.as_view(), name="user_profile_pic"),
    url(r'^send-mail/settings/$', views.UserSettingsView.as_view(), name="user_settings"),

    url(r'^category/(?P<slug>[-\w]+)/$', views.ForumCategoryView.as_view(), name="forum_category_detail"),
    url(r'^tags/(?P<slug>[-\w]+)/$', views.ForumTagsView.as_view(), name="forum_tags_detail"),

    url(r'^user/(?P<user_name>[a-zA-Z0-9_-]+.*?)/$', views.UserDetailView.as_view(), name="user_details"),

    url(r'^comment/add/$', views.CommentAdd.as_view(), name="new_comment"),
    url(r'^comment/votes/(?P<pk>[-\w]+)/up/$', views.CommentVoteUpView.as_view(), name="comment_vote_up"),
    url(r'^comment/votes/(?P<pk>[-\w]+)/down/$', views.CommentVoteDownView.as_view(), name="comment_vote_down"),

    url(r'^dashboard/$', views.LoginView.as_view(), name="dashboard"),
    # url(r'^dashboard/$', DashboardView.as_view(), name="dashboard"),
    url(r'^logout/$', views.getout, name='out'),

    url(r'^dashboard/category/list/$', views.CategoryList.as_view(), name="categories"),
    url(r'^dashboard/category/add/$', views.CategoryAdd.as_view(), name="add_category"),
    url(r'^dashboard/category/delete/(?P<slug>[-\w]+)/$',
        views.CategoryDelete.as_view(), name="delete_category"),
    url(r'^dashboard/category/edit/(?P<slug>[-\w]+)/$',
        views.CategoryEdit.as_view(), name="edit_category"),
    url(r'^dashboard/category/view/(?P<slug>[-\w]+)/$',
        views.CategoryDetailView.as_view(), name="view_category"),

    url(r'^dashboard/badge/list/$', views.BadgeList.as_view(), name="badges"),
    url(r'^dashboard/badge/add/$', views.BadgeAdd.as_view(), name="add_badge"),
    url(r'^dashboard/badge/delete/(?P<slug>[-\w]+)/$', views.BadgeDelete.as_view(), name="delete_badge"),
    url(r'^dashboard/badge/edit/(?P<slug>[-\w]+)/$', views.BadgeEdit.as_view(), name="edit_badge"),
    url(r'^dashboard/badge/view/(?P<slug>[-\w]+)/$', views.BadgeDetailView.as_view(), name="view_badge"),

    url(r'^dashboard/users/list/$', views.UserList.as_view(), name="users"),
    url(r'^dashboard/users/delete/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        views.DashboardUserDelete.as_view(), name="delete_user"),
    url(r'^dashboard/users/status/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        views.UserStatus.as_view(), name="user_status"),
    url(r'^dashboard/users/view/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        views.UserDetail.as_view(), name="user_detail"),
    url(r'^dashboard/users/edit/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        views.DashboardUserEdit.as_view(), name="edit_user"),

    url(r'^dashboard/topics/list/$', views.DashboardTopicList.as_view(), name="topics"),
    url(r'^dashboard/topics/delete/(?P<slug>[-\w]+)/$', views.TopicDeleteView.as_view(), name="delete_topic"),
    url(r'^dashboard/topic/view/(?P<slug>[-\w]+)/$', views.TopicDetail.as_view(), name="topic_detail"),
    url(r'^dashboard/topic/status/(?P<slug>[-\w]+)/$', views.TopicStatus.as_view(), name="topic_status"),

    url(r'^dashboard/change-password/$', views.ChangePassword.as_view(), name="change_password"),

]