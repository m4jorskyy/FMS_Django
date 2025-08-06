# views.py
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, PlayerSerializer, LoginSerializer, PostSerializer, \
    MatchParticipationSerializer, RegisterSerializer, NewsletterSerializer
from rest_framework import generics, status
from .models import User, Player, Post, SummonerName, MatchParticipation, Newsletter

"""
GET → get() method (list/retrieve)
POST → post() method (create)
PUT → put() method (update)
PATCH → patch() method (partial update)
DELETE → delete() method (destroy)
"""

# Create your views here.
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'nick'

    def get_queryset(self):
        return User.objects.all()


class PlayerListView(generics.ListAPIView):
    queryset = Player.objects.all().annotate(
        lane_order=Case(
            When(lane='Toplane', then=Value(0)),
            When(lane='Jungle', then=Value(1)),
            When(lane='Midlane', then=Value(2)),
            When(lane='Botlane', then=Value(3)),
            When(lane='Support', then=Value(4)),
            default=Value(5),
            output_field=IntegerField()
        )
    ).order_by('lane_order', 'id')
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]


class PlayerDetailView(generics.RetrieveAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'nick'

    def get_queryset(self):
        return Player.objects.all()

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nick = serializer.validated_data['nick']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(nick=nick)

            if user.check_password(password):
                now = datetime.now()
                expire = datetime.now() + timedelta(hours=24)

                payload = {
                    'id': user.id,
                    'nick': user.nick,
                    'exp': int(expire.timestamp()),
                    'iat': int(now.timestamp())
                }

                token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

                return Response({
                    'nick': user.nick,
                    'token': token
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)

        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

class PostsView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class CreatePostView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

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
        match_participations = MatchParticipation.objects.filter(summoner__in=summoner_names)
        return match_participations.select_related('match').order_by('-match__game_start')

class CreateNewsletterView(generics.CreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]
