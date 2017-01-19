from django.conf.urls import url
from .views import (TopicList, IndexView, ForumLoginView, facebook_login, google_login,
                    TopicAdd, TopicView, TopicLike, TopicFollow, TopicVotes,
                    get_mentioned_user, ProfileView, UserChangePassword,
                    ForgotPasswordView, CommentDelete,
                    CommentEdit, ForumCategoryList, ForumTagsList, ForumBadgeList,
                    UserProfileView, UserProfilePicView, UserSettingsView,
                    ForumCategoryView, ForumTagsView, UserDetailView,
                    CommentAdd, LoginView, ChangePassword,
                    getout, CategoryList, CategoryAdd, CategoryDelete,
                    CategoryEdit, CategoryDetailView,
                    BadgeList, BadgeAdd, BadgeDelete, BadgeEdit, BadgeDetailView,
                    UserList, DashboardUserDelete, UserStatus, UserDetail,
                    DashboardUserEdit, DashboardTopicList, DashboardTopicDelete,
                    TopicDetail, TopicStatus)

urlpatterns = [
    url(r'^$', TopicList.as_view(), name="topic_list"),
    url(r'^register/$', IndexView.as_view(), name="signup"),
    url(r'^forum/login/$', ForumLoginView.as_view(), name="user_login"),
    url(r'^fb_login/$', facebook_login, name="facebook_login"),
    url(r'^gp_login/$', google_login, name="google_login"),

    url(r'^topic/add/$', TopicAdd.as_view(), name="new_topic"),

    url(r'^topic/view/(?P<slug>[-\w]+)/$', TopicView.as_view(), name="view_topic"),
    url(r'^topic/like/(?P<slug>[-\w]+)/$', TopicLike.as_view(), name="like_topic"),
    url(r'^topic/follow/(?P<slug>[-\w]+)/$', TopicFollow.as_view(), name="follow_topic"),
    url(r'^topic/votes/(?P<slug>[-\w]+)/$', TopicVotes.as_view(), name="topic_votes"),
    url(r'^mentioned-users/(?P<topic_id>[-\w]+)/$', get_mentioned_user, name="get_mentioned_user"),
    url(r'^user/profile/(?P<user_name>[-\w]+)/$', ProfileView.as_view(), name="view_profile"),
    url(r'^change-password/$', UserChangePassword.as_view(), name="user_change_password"),
    url(r'^forgot-password/$', ForgotPasswordView.as_view(), name="forgot_password"),
    url(r'^comment/delete/(?P<comment_id>[-\w]+)/$',
        CommentDelete.as_view(), name="comment_delete"),
    url(r'^comment/edit/(?P<comment_id>[-\w]+)/$', CommentEdit.as_view(), name="comment_edit"),

    url(r'^categories/$', ForumCategoryList.as_view(), name="forum_categories"),
    url(r'^tags/$', ForumTagsList.as_view(), name="forum_tags"),
    url(r'^badges/$', ForumBadgeList.as_view(), name="forum_badges"),
    url(r'^profile/$', UserProfileView.as_view(), name="user_profile"),
    url(r'^upload/profile-pic/$', UserProfilePicView.as_view(), name="user_profile_pic"),
    url(r'^send-mail/settings/$', UserSettingsView.as_view(), name="user_settings"),

    url(r'^category/(?P<slug>[-\w]+)/$', ForumCategoryView.as_view(), name="forum_category_detail"),
    url(r'^tags/(?P<slug>[-\w]+)/$', ForumTagsView.as_view(), name="forum_tags_detail"),

    url(r'^user/(?P<user_name>[a-zA-Z0-9_-]+.*?)/$', UserDetailView.as_view(), name="user_details"),

    url(r'^comment/add/$', CommentAdd.as_view(), name="new_comment"),

    url(r'^dashboard/$', LoginView.as_view(), name="dashboard"),
    # url(r'^dashboard/$', DashboardView.as_view(), name="dashboard"),
    url(r'^logout/$', getout, name='out'),

    url(r'^dashboard/category/list/$', CategoryList.as_view(), name="categories"),
    url(r'^dashboard/category/add/$', CategoryAdd.as_view(), name="add_category"),
    url(r'^dashboard/category/delete/(?P<slug>[-\w]+)/$',
        CategoryDelete.as_view(), name="delete_category"),
    url(r'^dashboard/category/edit/(?P<slug>[-\w]+)/$',
        CategoryEdit.as_view(), name="edit_category"),
    url(r'^dashboard/category/view/(?P<slug>[-\w]+)/$',
        CategoryDetailView.as_view(), name="view_category"),

    url(r'^dashboard/badge/list/$', BadgeList.as_view(), name="badges"),
    url(r'^dashboard/badge/add/$', BadgeAdd.as_view(), name="add_badge"),
    url(r'^dashboard/badge/delete/(?P<slug>[-\w]+)/$', BadgeDelete.as_view(), name="delete_badge"),
    url(r'^dashboard/badge/edit/(?P<slug>[-\w]+)/$', BadgeEdit.as_view(), name="edit_badge"),
    url(r'^dashboard/badge/view/(?P<slug>[-\w]+)/$', BadgeDetailView.as_view(), name="view_badge"),

    url(r'^dashboard/users/list/$', UserList.as_view(), name="users"),
    url(r'^dashboard/users/delete/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        DashboardUserDelete.as_view(), name="delete_user"),
    url(r'^dashboard/users/status/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        UserStatus.as_view(), name="user_status"),
    url(r'^dashboard/users/view/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        UserDetail.as_view(), name="user_detail"),
    url(r'^dashboard/users/edit/(?P<user_id>[a-zA-Z0-9_-]+.*?)/$',
        DashboardUserEdit.as_view(), name="edit_user"),

    url(r'^dashboard/topics/list/$', DashboardTopicList.as_view(), name="topics"),
    url(r'^dashboard/topics/delete/(?P<slug>[-\w]+)/$',
        DashboardTopicDelete.as_view(), name="delete_topic"),
    url(r'^dashboard/topic/view/(?P<slug>[-\w]+)/$', TopicDetail.as_view(), name="topic_detail"),
    url(r'^dashboard/topic/status/(?P<slug>[-\w]+)/$', TopicStatus.as_view(), name="topic_status"),

    url(r'^dashboard/change-password/$', ChangePassword.as_view(), name="change_password"),

]
