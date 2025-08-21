from django.urls import path
from . import views

urlpatterns = [
    # GET /api/me                       info zalogowanego usera
    path('me/', views.MeView.as_view(), name="me"),

    # GET  /api/users/                  lista użytkowników (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),

    # POST /api/users/create/           tworzenie nowego użytkownika (admin only)
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),

    # DELETE /api/users/delete/<nick>/  usuwanie użytkownika (admin only)
    path('users/delete/<str:nick>/', views.DestroyUserView.as_view(), name='delete_user'),

    # PUT/PATCH /api/users/edit/<nick>/ edytowanie użytkownika (user albo admin)
    path('users/edit/<str:nick>/', views.UpdateUserView.as_view(), name='edit_user'),

    # GET  /api/users/<nick>/           szczegóły użytkownika (konkretny user albo admin)
    path('users/<str:nick>/', views.UserDetailView.as_view(), name='user_detail'),

    # GET  /api/users/me/posts/         lista postów zalogowanego użytkownika
    path('users/me/posts/', views.ListUserPostsView.as_view(), name='user_posts'),

    # GET  /api/players/                lista graczy (public)
    path('players/', views.PlayerListView.as_view(), name='player_list'),

    # POST api/players/create/<nick>    utworzenie gracza
    path('players/create/', views.CreatePlayerView.as_view(), name='create_player'),

    # GET  /api/players/matches/<nick>  historia meczów (public, paginowana)
    path('players/matches/<str:nick>/', views.ListMatchesView.as_view(), name='player_matches'),

    # GET  /api/players/<nick>/         szczegóły gracza (zalogowany)
    path('players/<str:nick>/', views.PlayerDetailView.as_view(), name='player_detail'),

    # POST /api/register/               rejestracja nowego konta (public)
    path('register/', views.RegisterView.as_view(), name='register'),

    # POST /api/login/                  logowanie (public)
    path('login/', views.LoginView.as_view(), name='login'),

    # GET  /api/posts/                  lista postów (public, paginowana)
    path('posts/', views.PostsView.as_view(), name='posts'),

    # POST /api/posts/create/           tworzenie nowego postu (zalogowany)
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),

    # PUT/PATCH /api/posts/edit/<pk>/   edycja postu (autor lub admin)
    path('posts/edit/<int:pk>/', views.UpdatePostView.as_view(), name='update_post'),

    # DELETE /api/posts/delete/<pk>/    usuwanie postu (autor lub admin)
    path('posts/delete/<int:pk>/', views.DestroyPostView.as_view(), name='delete_post'),

    # POST /api/newsletter/             zapisanie do newslettera (public)
    path('newsletter/', views.CreateNewsletterView.as_view(), name='sign_to_newsletter'),

    # GET pandascore.co                 pobranie oficjalnych meczy (public)
    path('officialmatches/', views.ListOfficialMatches.as_view(), name='get_official_matches'),

    # GET /api/csrf                     csrf token (public)
    path('csrf/', views.CsrfView.as_view(), name="get_csrf_token"),

    # POST /api/logout                  wylogowanie (zalogowany)
    path('logout/', views.LogoutView.as_view(), name="logout"),

    # GET /api/players/<nick>/ranks/    pobranie rang gracza (public)
    path('players/<str:nick>/ranks/', views.ListPlayerRanks.as_view(), name='player_ranks'),
]
