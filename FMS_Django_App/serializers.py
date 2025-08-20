#serializers.py
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import Player, User, Post, Match, MatchParticipation, Newsletter
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
        read_only_fields = ['role']
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
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'nick', 'email', 'password', 'role']
        extra_kwargs = {
            'role': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            nick=validated_data['nick'],
            password=make_password(validated_data['password'])
        )
        user.save()
        return user

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