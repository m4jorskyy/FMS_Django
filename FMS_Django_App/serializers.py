#serializers.py

from rest_framework import serializers
from .models import Player, User, Post, Match, MatchParticipation


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'nick',  'lane', 'champion', 'team_role']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nick', 'email', 'password']
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

class LoginSerializer(serializers.Serializer):
    nick = serializers.CharField()
    password = serializers.CharField(write_only=True)

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'text', 'date']

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['match_id', 'game_duration', 'game_start']

class MatchParticipationSerializer(serializers.ModelSerializer):
    match = MatchSerializer(read_only=True)
    summoner = serializers.CharField(source='summoner.riot_id', read_only=True)

    class Meta:
        model = MatchParticipation
        fields = ['match', 'summoner', 'champion', 'kills', 'deaths', 'assists', 'win', 'lane']