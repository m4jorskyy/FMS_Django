from django.db import models
from django.utils import timezone


# Create your models here.

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    nick = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255, default="USER")

    def __str__(self):
        return self.nick

    @property
    def is_authenticated(self):
        return True


class Player(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    nick = models.CharField(max_length=255)
    lane = models.CharField(max_length=255)
    champion = models.CharField(max_length=255)
    team_role = models.CharField(max_length=255)

    def __str__(self):
        return self.nick


class SummonerName(models.Model):
    player = models.ForeignKey(Player, related_name='summoner_names', on_delete=models.CASCADE)
    riot_id = models.CharField(max_length=255)
    puuid = models.CharField(max_length=255, default="", db_index=True)


class Match(models.Model):
    match_id = models.CharField(max_length=20, unique=True, db_index=True)
    game_duration = models.IntegerField(default=0)
    game_start = models.DateTimeField(default=timezone.now)


class MatchParticipation(models.Model):
    match = models.ForeignKey(Match, related_name='participations', on_delete=models.CASCADE)
    summoner = models.ForeignKey(SummonerName, related_name='participations', on_delete=models.CASCADE)
    champion = models.CharField(max_length=50)
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    win = models.BooleanField()
    lane = models.CharField(max_length=50)


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.TextField()
    text = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
