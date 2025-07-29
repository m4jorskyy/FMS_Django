# views.py
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import UserSerializer, PlayerSerializer, LoginSerializer, PostSerializer, MatchParticipationSerializer
from rest_framework import generics, status
from .models import User, Player, Post, SummonerName, MatchParticipation

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
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]


class PlayerDetailView(generics.RetrieveAPIView):
    serializer_class = PlayerSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'nick'

    def get_queryset(self):
        return Player.objects.all()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nick = serializer.validated_data['nick']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(nick=nick)

            now = datetime.now()
            expire = datetime.now() + timedelta(hours=24)


            if password == user.password:
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

class ListMatchesView(generics.ListAPIView):
    serializer_class = MatchParticipationSerializer
    permission_classes = [AllowAny]
    lookup_field = 'nick'

    def get_queryset(self):
        nick = self.kwargs['nick']
        player = Player.objects.get(nick=nick)
        summoner_names = SummonerName.objects.filter(player=player)
        match_participations = MatchParticipation.objects.filter(summoner__in=summoner_names)
        return match_participations.select_related('match').order_by('-match__game_start')