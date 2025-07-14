from django.urls import path

from .views import *

urlpatterns = [
    # Home routes
    path('', HomeView.as_view(), name='home'),
    path('search/', SearchView.as_view(), name='search'),

    # Detail routes
    path('article/<int:pk>/', ArticleDetail.as_view(), name='detail'),
    path('article/create/', ArticleCreateView.as_view(), name='create-article'),
    path('article/<int:pk>/update', ArticleUpdateView.as_view(), name='update-article'),
    path('article/<int:pk>/delete', ArticleDeleteView.as_view(), name='delete-article'),

    # Comment routes
    path('article/<int:pk>/add-comment/', CommentView.as_view(), name='comment'),
    path('article/<int:article_pk>/delete-comment/<int:comment_pk>/', CommentDeleteView.as_view(),
         name='delete-comment'),

    # Notification routes
    path('notification/<int:pk>/read/', NotificationReadRedirectView.as_view(), name='read-notification'),
    path('notification/read-all/', ReadAllNotificationsView.as_view(), name='read-all-notifications'),

    # 404 route
    path('not-found/', Custom404.as_view(), name='not-found')
]
