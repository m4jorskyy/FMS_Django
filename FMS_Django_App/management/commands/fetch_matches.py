import os
import time
from datetime import datetime, timezone

import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from ...models import SummonerName, Match, MatchParticipation


class Command(BaseCommand):
    help = "Fetch recent matches for all summoner names"

    def handle(self, *args, **options):
        load_dotenv()
        api_key = str(os.getenv("RIOT_API_KEY"))
        if not api_key:
            self.stderr.write("Missing RIOT_API_KEY in .env file!")
            return

        headers = {
            "X-Riot-Token": api_key
        }

        new_matches = 0
        new_parts = 0

        for summoner in SummonerName.objects.all():
            puuid = summoner.puuid

            match_id_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=5"

            match_ids_api = requests.get(url=match_id_url, headers=headers)
            if match_ids_api.status_code != 200:
                self.stderr.write(f"Failed to fetch Match IDs for {summoner.riot_id}: {match_ids_api}")
            try:
                match_ids_api = match_ids_api.json()
            except ValueError as ve:
                self.stderr.write(f"Invalid JSON for {summoner.riot_id}: {ve}")
                continue

            time.sleep(1)

            for match_id in match_ids_api:
                if Match.objects.filter(match_id=match_id).exists():
                    continue
                match_details_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"

                match_details_api = requests.get(url=match_details_url, headers=headers)

                if match_details_api.status_code != 200:
                    self.stderr.write(f"Failed to fetch details for {match_id}: {match_details_api.status_code}")
                    continue
                try:
                    match_details_api = match_details_api.json()
                except ValueError as ve:
                    self.stderr.write(f"Invalid JSON for {match_id}: {ve}")
                    continue

                time.sleep(1)

                match = Match.objects.create(
                    match_id=match_id,
                    game_duration=match_details_api["info"]["gameDuration"],
                    game_start=datetime.fromtimestamp(match_details_api["info"]["gameStartTimestamp"] / 1000, tz=timezone.utc)
                )
                new_matches += 1

                for p in match_details_api["info"]["participants"]:
                    try:
                        summ = SummonerName.objects.get(puuid=p["puuid"])
                        MatchParticipation.objects.create(
                            match=match,
                            summoner=summ,
                            champion=p["championName"],
                            kills=p["kills"],
                            deaths=p["deaths"],
                            assists=p["assists"],
                            win=p["win"],
                            lane=p["lane"]
                        )
                        new_parts += 1
                    except SummonerName.DoesNotExist:
                        continue

        self.stdout.write(f"Added {new_matches} new matches and {new_parts} participations.")