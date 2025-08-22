from django.urls import path
from . import views

urlpatterns = [
    # GET /api/me                       info zalogowanego usera
    path('me/', views.MeView.as_view(), name="me"),

    # GET  /api/users/                  lista użytkowników (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),

    # POST /api/users/create/           tworzenie nowego użytkownika (admin only)
    path('users/create/', views.CreateUserView.as_view(), name='create_user'),

    # DELETE /api/users/<nick>/delete/  usuwanie użytkownika (admin only)
    path('users/<str:nick>/delete/', views.DestroyUserView.as_view(), name='delete_user'),

    # PUT/PATCH /api/users/<nick>/edit/ edytowanie użytkownika (user albo admin)
    path('users/<str:nick>/edit/', views.UpdateUserView.as_view(), name='edit_user'),

    # GET  /api/users/<nick>/           szczegóły użytkownika (konkretny user albo admin)
    path('users/<str:nick>/', views.UserDetailView.as_view(), name='user_detail'),

    # GET  /api/users/me/posts/         lista postów zalogowanego użytkownika
    path('users/me/posts/', views.ListUserPostsView.as_view(), name='user_posts'),

    # GET  /api/players/                lista graczy (public)
    path('players/', views.PlayerListView.as_view(), name='player_list'),

    # GET  /api/players/<nick>/         szczegóły gracza (zalogowany)
    path('players/<str:nick>/', views.PlayerDetailView.as_view(), name='player_detail'),

    # GET /api/players/<nick>/ranks/    pobranie rang gracza (public)
    path('players/<str:nick>/ranks/', views.ListPlayerRanks.as_view(), name='player_ranks'),

    # GET  /api/players/<nick>/matches/  historia meczów (public, paginowana)
    path('players/<str:nick>/matches/', views.ListMatchesView.as_view(), name='player_matches'),

    # POST api/players/create/   utworzenie gracza
    path('players/create/', views.CreatePlayerView.as_view(), name='create_player'),

    # POST /api/register/               rejestracja nowego konta (public)
    path('register/', views.RegisterView.as_view(), name='register'),

    # POST /api/login/                  logowanie (public)
    path('login/', views.LoginView.as_view(), name='login'),

    # POST /api/logout                  wylogowanie (zalogowany)
    path('logout/', views.LogoutView.as_view(), name="logout"),

    # GET  /api/posts/                  lista postów (public, paginowana)
    path('posts/', views.PostsView.as_view(), name='posts'),

    # POST /api/posts/create/           tworzenie nowego postu (zalogowany)
    path('posts/create/', views.CreatePostView.as_view(), name='create_post'),

    # PUT/PATCH /api/posts/<pk>/edit/   edycja postu (autor lub admin)
    path('posts/<int:pk>/edit/', views.UpdatePostView.as_view(), name='update_post'),

    # DELETE /api/posts/<pk>/delete/    usuwanie postu (autor lub admin)
    path('posts/<int:pk>/delete/', views.DestroyPostView.as_view(), name='delete_post'),

    # POST /api/newsletter/             zapisanie do newslettera (public)
    path('newsletter/', views.CreateNewsletterView.as_view(), name='sign_to_newsletter'),

    # GET pandascore.co                 pobranie oficjalnych meczy (public)
    path('officialmatches/', views.ListOfficialMatches.as_view(), name='get_official_matches'),

    # GET /api/csrf                     csrf token (public)
    path('csrf/', views.CsrfView.as_view(), name="get_csrf_token"),
]