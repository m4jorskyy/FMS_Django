#serializers.py
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Player, User, Post, Match, MatchParticipation, Newsletter, SummonerName, PlayerOfficialStats
import bleach

ALLOWED_TAGS = ['b','i','em','strong','u','a','p','ul','ol','li','br','blockquote','code','pre', 'h1', 'h2']
ALLOWED_ATTRS = {'a': ['href', 'title', 'rel', 'target']}
ALLOWED_PROTOCOLS = ['http','https','mailto']

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'nick',  'lane', 'champion', 'team_role', 'twitter', 'youtube', 'twitch', 'kick', 'instagram', 'tiktok']
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nick', 'email', 'password', 'role']
        extra_kwargs ={
            'password': {
                'write_only': True,
                'required': False
            }
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    nick = serializers.CharField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nick', 'email', 'password', 'role']
        extra_kwargs = {
            'role': {
                'read_only': True
            },
            'email': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            },
            'nick': {
                'validators': [UniqueValidator(queryset=User.objects.all())]
            }
        }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            if hasattr(e, 'messages'):
                raise serializers.ValidationError(e.messages)
            elif hasattr(e, 'message'):
                raise serializers.ValidationError([e.message])
            else:
                raise serializers.ValidationError([str(e)])
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data['email'],
            nick=validated_data['nick'],
            password=validated_data['password']
        )

class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='nick'
    )

    class Meta:
        model = Post
        fields = ['id', 'title', 'text', 'date', 'author']
        extra_kwargs = {
            'id': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

    def validate_title(self, value):
        return bleach.clean(value, tags=[], attributes={}, protocols=[], strip=True)

    def validate_text(self, value):
        cleaned = bleach.clean(
            value,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRS,
            protocols=ALLOWED_PROTOCOLS,
            strip=True
        )

        return bleach.linkify(cleaned)

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

class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = ['email']

class SummonerNameSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = SummonerName
        fields = ['riot_id', 'puuid', 'player', 'tier', 'rank', 'league_points']


class PlayerOfficialStatsSerializer(serializers.ModelSerializer):
    kda = serializers.SerializerMethodField()
    cs_per_min = serializers.SerializerMethodField()
    damage_per_min = serializers.SerializerMethodField()
    kill_participation = serializers.SerializerMethodField()
    gold_participation = serializers.SerializerMethodField()
    dmg_participation = serializers.SerializerMethodField()

    class Meta:
        model = PlayerOfficialStats
        fields = '__all__'

    def get_kda(self, obj):
        if obj.deaths == 0:
            return (obj.kills + obj.assists)  # Perfect KDA
        return round((obj.kills + obj.assists) / obj.deaths, 2)

    def get_cs_per_min(self, obj):
        if not obj.gamelength or obj.gamelength.total_seconds() == 0:
            return 0
        game_minutes = obj.gamelength.total_seconds() / 60
        return round(obj.cs / game_minutes, 1)

    def get_damage_per_min(self, obj):
        if not obj.gamelength or obj.gamelength.total_seconds() == 0:
            return 0
        game_minutes = obj.gamelength.total_seconds() / 60
        return round(obj.damage_to_champions / game_minutes, 1)

    def get_kill_participation(self, obj):
        if obj.team_kills == 0:
            return 0
        return round(((obj.kills + obj.assists) / obj.team_kills) * 100, 1)

    def get_gold_participation(self, obj):
        if obj.team_gold == 0:
            return 0
        return round((obj.gold / obj.team_gold) * 100, 1)

    def get_dmg_participation(self, obj):
        if obj.team_damage_to_champions == 0:
            return 0
        return round((obj.damage_to_champions / obj.team_damage_to_champions) * 100, 1)

class PlayerAggregatedStatsSerializer(serializers.Serializer):
    total_matches = serializers.IntegerField()
    total_kills = serializers.IntegerField()
    total_deaths = serializers.IntegerField()
    total_assists = serializers.IntegerField()
    total_cs = serializers.IntegerField()
    total_gold = serializers.IntegerField()
    total_team_gold = serializers.IntegerField()
    total_damage = serializers.IntegerField()
    total_team_damage = serializers.IntegerField()
    total_vision_score = serializers.IntegerField()
    wins = serializers.IntegerField()

    # Calculated fields
    avg_kda = serializers.SerializerMethodField()
    avg_cs_per_min = serializers.SerializerMethodField()
    avg_damage_per_min = serializers.SerializerMethodField()
    win_rate = serializers.SerializerMethodField()
    avg_kill_participation = serializers.SerializerMethodField()
    avg_gold_participation = serializers.SerializerMethodField()
    avg_dmg_participation = serializers.SerializerMethodField()
    avg_vision_score = serializers.SerializerMethodField()

    def get_avg_kda(self, obj):
        if obj['total_deaths'] == 0:
            return "Perfect"
        return round((obj['total_kills'] + obj['total_assists']) / obj['total_deaths'], 2)

    def get_avg_cs_per_min(self, obj):
        total_minutes = obj['total_gamelength'].total_seconds() / 60 if obj['total_gamelength'] else 0
        if total_minutes == 0:
            return 0
        return round(obj['total_cs'] / total_minutes, 1)

    def get_win_rate(self, obj):
        if obj['total_matches'] == 0:
            return 0
        return round((obj['wins'] / obj['total_matches']) * 100, 1)

    def get_avg_damage_per_min(self, obj):
        total_minutes=obj['total_gamelength'].total_seconds() / 60 if obj['total_gamelength'] else 0
        if total_minutes == 0:
            return 0
        return round((obj['total_damage'] / total_minutes), 1)

    def get_avg_kill_participation(self, obj):
        if obj['total_team_kills'] == 0:
            return 0
        return round(((obj['total_kills'] + obj['total_assists']) / obj['total_team_kills']) * 100, 1)

    def get_avg_gold_participation(self, obj):
        if obj['total_team_gold'] == 0:
            return 0
        return round((obj['total_gold'] / obj['total_team_gold']) * 100, 1)

    def get_avg_dmg_participation(self, obj):
        if obj['total_team_damage'] == 0:
            return 0
        return round((obj['total_damage'] / obj['total_team_damage']) * 100, 1)

    def get_avg_vision_score(self, obj):
        if obj['total_matches'] == 0:
            return 0
        return round((obj['total_vision_score'] / obj['total_matches']), 1)