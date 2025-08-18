from django.contrib import admin
from .models import Player, SummonerName, Match, User, MatchParticipation, Post, Newsletter


# Register your models here.

class SummonerNameInline(admin.TabularInline):
    model = SummonerName
    extra = 1

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nick',  'lane', 'champion', 'team_role', 'twitter', 'youtube', 'twitch', 'kick', 'instagram', 'tiktok')
    inlines = [SummonerNameInline]

@admin.register(SummonerName)
class SummonerNameAdmin(admin.ModelAdmin):
    list_display = ('riot_id', 'puuid', 'player')

@admin.register(Match)
class MatchesAdmin(admin.ModelAdmin):
    list_display = ('match_id', 'game_duration', 'game_start')

@admin.register(MatchParticipation)
class MatchParticipationAdmin(admin.ModelAdmin):
    list_display = ('match', 'summoner', 'champion', 'kills', 'deaths', 'assists', 'win', 'lane')

@admin.register(User)
class UsersAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'nick', 'email', 'password', 'role')

@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'title', 'text', 'date')

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')