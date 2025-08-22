# views.py
import os
from datetime import datetime, timedelta
import jwt
import requests
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .serializers import UserSerializer, PlayerSerializer, LoginSerializer, PostSerializer, \
    MatchParticipationSerializer, RegisterSerializer, NewsletterSerializer, SummonerNameSerializer
from rest_framework import generics, status
from .models import User, Player, Post, SummonerName, MatchParticipation, Newsletter

"""
GET → get() method (list/retrieve)
POST → post() method (create)
PUT → put() method (update)
PATCH → patch() method (partial update)
DELETE → delete() method (destroy)
"""


class HasSpecificRolePermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user_role = getattr(request.user, 'role', None)

        return user_role == self.required_role or user_role == "ADMIN"


class IsEditorOrAdminUser(HasSpecificRolePermission):
    required_role = "EDITOR"


# Create your views here.

# GET /api/me/
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "nick": user.nick,
            "role": user.role,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })


# GET  /api/users/                  lista użytkowników (admin only)
class UserPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination


# POST /api/users/create/           tworzenie nowego użytkownika (admin only)
class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]


# DELETE  /api/users/delete/<nick>  usuwanie użytkownika (admin only)
class DestroyUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'nick'

    def destroy(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            self.perform_destroy(user)
            return Response(
                {"success": "User deleted succesfully."},
                status=status.HTTP_200_OK
            )

        except Http404:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


# PATCH/PUT /api/users/edit/<nick>  edytowanie uż
class UpdateUserView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'nick'

    def get_object(self):
        obj = super().get_object()
        if not (self.request.user == obj or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to do that!")
        return obj


# GET  /api/users/<nick/            szczegóły użytkownika (konkretny user albo admin)
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    lookup_field = 'nick'

    def get_queryset(self):
        return User.objects.all()

    def get_object(self):
        obj = super().get_object()
        if not (self.request.user == obj or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to do that!")
        return obj


# GET  /api/users/me/posts/         lista postów zalogowanego użytkownika
class ListUserPostsView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user)


# GET  /api/players/                lista graczy (public)
class PlayerListView(generics.ListAPIView):
    queryset = Player.objects.all().annotate(
        lane_order=Case(
            When(lane='Top', then=Value(0)),
            When(lane='Jungle', then=Value(1)),
            When(lane='Middle', then=Value(2)),
            When(lane='Bottom', then=Value(3)),
            When(lane='Utility', then=Value(4)),
            default=Value(5),
            output_field=IntegerField()
        )
    ).order_by('lane_order', 'id')
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]


# GET  /api/players/<nick>/         szczegóły gracza (admin)
class PlayerDetailView(generics.RetrieveAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'nick'

    def get_queryset(self):
        return Player.objects.all()


# GET  /api/players/matches/<nick>/ historia meczów (public, paginowana)
class MatchPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class ListMatchesView(generics.ListAPIView):
    serializer_class = MatchParticipationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'nick'
    pagination_class = MatchPagination

    def get_queryset(self):
        nick = self.kwargs['nick']
        player = Player.objects.get(nick=nick)
        summoner_names = SummonerName.objects.filter(player=player)
        return MatchParticipation.objects.filter(
            summoner__in=summoner_names
        ).select_related('match').order_by('-match__game_start')


# POST /api/players/create/<nick>     tworzenie nowego zawodnika z dashboarda admina
class CreatePlayerView(generics.CreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAdminUser]


# POST /api/register/               rejestracja nowego konta (public)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


# POST /api/login/                  logowanie (public)
class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nick = serializer.validated_data['nick']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(nick=nick)

            if user.check_password(password):
                now = datetime.now()
                expire = now + timedelta(hours=24)

                payload = {
                    'id': user.id,
                    'nick': user.nick,
                    'exp': int(expire.timestamp()),
                    'iat': int(now.timestamp())
                }

                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                response = Response({
                    "nick": user.nick,
                    "role": user.role
                }, status=status.HTTP_200_OK)

                response.set_cookie(
                    key="access_token",
                    value=token,
                    httponly=True,
                    secure=not settings.DEBUG,
                    samesite="None" if not settings.DEBUG else "Lax",
                    max_age=24 * 60 * 60,
                    path="/"
                )

                return response

            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        resp = Response({"detail": "Logged out successfully"}, status=200)
        resp.delete_cookie(
            key="access_token",
            path="/",
            samesite="None" if not settings.DEBUG else "Lax"
        )
        return resp


# GET  /api/posts/                  lista postów (public, paginowana)
class PostPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 20


class PostsView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    pagination_class = PostPagination


# POST /api/posts/create/           tworzenie nowego postu (zalogowany)
class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsEditorOrAdminUser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'posts'


# PUT/PATCH /api/posts/edit/<pk>/   edycja postu (autor lub admin)
class UpdatePostView(generics.UpdateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_object(self):
        obj = super().get_object()
        if not (self.request.user == obj.author or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to do that!")
        return obj


# DELETE /api/posts/delete/<pk>/    usuwanie postu (autor lub admin)
class DestroyPostView(generics.DestroyAPIView):
    queryset = Post.objects.all()

    def get_object(self):
        obj = super().get_object()
        if not (self.request.user == obj.author or self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to do that!")
        return obj


# POST /api/newsletter/             zapisanie do newslettera (public)
class CreateNewsletterView(generics.CreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'newsletter'


# GET /api/pandascore.co            oficjalne mecze (public)
class ListOfficialMatches(generics.ListAPIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'pandascore'

    def get(self, request, *args, **kwargs):
        team_id = request.query_params.get("team_id")
        status = request.query_params.get("status")
        page = request.query_params.get("page", 1)

        url = f"https://api.pandascore.co/lol/matches?filter[opponent_id]={team_id}&filter[status]={status}&page[number]={page}&page[size]=5"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {str(os.getenv('PANDASCORE_API_KEY'))}"
        }

        req = requests.get(url=url, headers=headers)

        return Response(req.json(), status=req.status_code)


# GET /api/csrf                     CSRF Token
@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfView(RetrieveAPIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response(status=204)


# GET /api/players/<nick>/ranks
class ListPlayerRanks(generics.ListAPIView):
    serializer_class = SummonerNameSerializer
    permission_classes = [AllowAny]
    lookup_field = 'nick'

    def get_queryset(self):
        nick = self.kwargs['nick']

        try:
            player = Player.objects.get(nick=nick)
            return SummonerName.objects.filter(player=player).annotate(
                tier_order=Case(
                    When(tier="CHALLENGER", then=Value(0)),
                    When(tier="GRANDMASTER", then=Value(1)),
                    When(tier="MASTER", then=Value(2)),
                    When(tier="DIAMOND", then=Value(3)),
                    When(tier="EMERALD", then=Value(4)),
                    When(tier="PLATINUM", then=Value(5)),
                    When(tier="GOLD", then=Value(6)),
                    When(tier="SILVER", then=Value(7)),
                    When(tier="BRONZE", then=Value(8)),
                    When(tier="IRON", then=Value(9)),
                    When(tier="UNRANKED", then=Value(10)),
                    default=Value(10),
                    output_field=IntegerField()
                ),
                rank_order=Case(
                    When(rank="I", then=Value(1)),
                    When(rank="II", then=Value(2)),
                    When(rank="III", then=Value(3)),
                    When(rank="IV", then=Value(4)),
                    default=Value(5),
                    output_field=IntegerField()
                )
            ).order_by('tier_order', 'rank_order')
        except Player.DoesNotExist:
            return SummonerName.objects.none()