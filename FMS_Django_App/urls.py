#app/urls.py
from django.urls import path
from . import views
urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<str:nick>/', views.UserDetailView.as_view(), name='user_detail'),
    path('players/', views.PlayerListView.as_view(), name='player_list'),
    path('players/<str:nick>/', views.PlayerDetailView.as_view(), name='player_detail'),
    path('players/<str:nick>/matches/', views.ListMatchesView.as_view(), name='player_matches'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('posts/', views.PostsView.as_view(), name='posts'),
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),
    path('newsletter/', views.CreateNewsletterView.as_view(), name='sign_to_newsletter')
]