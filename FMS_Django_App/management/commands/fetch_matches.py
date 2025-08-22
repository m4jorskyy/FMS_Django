import os
import time
from datetime import datetime, timezone

import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from ...models import SummonerName, Match, MatchParticipation

"""
Management command for fetching and updating data of players from Riot Games API

Operations that are made:
1. Getting PUUID of the account
2. Calling Riot Games API to fetch data that include rank of the account, then updating it
3. Calling Riot Games API to fetch 20 match ids of the account and check if there are matching ids from database
4. Calling Riot Games API to fetch details of matches that are not in database and participants stats
"""


class Command(BaseCommand):
    help = "Fetch recent matches for all summoner names"

    def handle(self, *args, **options):

        # Loading environment variables
        load_dotenv()

        # Getting Riot Games API key from environment variables
        api_key = str(os.getenv("RIOT_API_KEY"))

        # Check if there is RGAPI in .env file
        if not api_key:
            self.stderr.write("Missing RIOT_API_KEY in .env file!")
            return

        # RGAPI Key to headers needed for authorization
        headers = {"X-Riot-Token": api_key}

        # Global stat of added participants
        total_participants = 0

        # Iterate through summoners one by one to fetch all the data we need for every one of them
        for summoner in SummonerName.objects.all():

            # Info
            self.stdout.write(f"\n=== Gracz: {summoner.riot_id} | PUUID: {summoner.puuid} ===")
            self.stdout.write(f"\n Pobieranie rangi konta: {summoner.riot_id}")

            # Request URL for getting rank of the account
            rank_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{summoner.puuid}"

            # Fetching
            rank_resp = requests.get(rank_url, headers=headers)

            # Bypassing rate limits
            time.sleep(1)

            # Check if there are errors
            if rank_resp.status_code != 200:
                self.stderr.write(f"Pobieranie rangi konta: {rank_resp.status_code} {rank_resp.text}")
                continue

            # Get JSON data
            rank_api = rank_resp.json()

            # Check if data is empty
            if not rank_api:
                self.stdout.write("Brak danych rankingowych.")
                continue

            # Check if there is field for Ranked Solo
            soloq = None
            for entry in rank_api:
                if entry.get('queueType') == 'RANKED_SOLO_5x5':
                    soloq = entry
                    break

            if not soloq:
                self.stderr.write("Brak Solo Queue rankingu")
                continue

            # Assign values from JSON
            tier = soloq.get('tier', 'UNRANKED')
            rank = soloq.get('rank', '')
            league_points = soloq.get('leaguePoints', 0)

            # Update summoner tier, rank, LP
            SummonerName.objects.filter(id=summoner.id).update(
                tier=tier,
                rank=rank,
                league_points=league_points
            )

            # Info
            self.stdout.write(f"Zaktualizowano rangę dla {summoner.riot_id}: {tier} {rank} {league_points} LP")

            # Local stat
            summoner_participants = 0

            # Request URL for fetching match ids of the account
            match_id_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner.puuid}/ids?start=0&count=20"

            # Fetching
            resp = requests.get(match_id_url, headers=headers)

            # Bypassing rate limits
            time.sleep(1)

            # Check if there are errors
            if resp.status_code != 200:
                self.stderr.write(f"Pobieranie match IDs: {resp.status_code} {resp.text}")
                continue

            # Get JSON data
            match_ids_api = resp.json()

            # Info
            self.stdout.write(f"Pobrano {len(match_ids_api)} match_id: {match_ids_api}")

            # Check if data is empty
            if not match_ids_api:
                self.stderr.write("Brak meczów do przetworzenia")
                continue

            # Iterate through match ids
            for match_id in match_ids_api:

                # Check if there is the match id in the database
                if Match.objects.filter(match_id=match_id).exists():
                    self.stdout.write(f"Pomijam {match_id} (już w bazie)")
                    continue

                # Info
                self.stdout.write(f"Przetwarzam nowy mecz {match_id}")

                # Request URL for new match data
                match_details_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"

                # Fetching
                match_resp = requests.get(match_details_url, headers=headers)

                # Bypassing rate limits
                time.sleep(1)

                # Check if there are errors
                if match_resp.status_code != 200:
                    self.stdout.write(
                        f"Pobieranie szczegółów meczu {match_id}: {match_resp.status_code} {match_resp.text}")
                    continue

                # Get JSON data
                match_details_api = match_resp.json()

                # Save match object to the database
                match_obj = Match.objects.create(
                    match_id=match_id,
                    game_duration=match_details_api["info"]["gameDuration"],
                    game_start=datetime.fromtimestamp(match_details_api["info"]["gameStartTimestamp"] / 1000,
                                                      tz=timezone.utc)
                )

                # Info
                self.stdout.write(f"Dodano mecz: {match_id}")

                # Look for participants in this match
                participants = match_details_api["info"]["participants"]

                # Local stat for checking if our players took part in the same match
                match_participants = 0

                # Iterate through match participants
                for p in participants:

                    # Assign participant puuid to variable
                    puuid = p["puuid"]

                    # Check if puuid is in the database
                    summoner_in_db = SummonerName.objects.filter(puuid=puuid).first()
                    if not summoner_in_db:
                        continue

                    # Create MatchParticipation object
                    MatchParticipation.objects.create(
                        match=match_obj,
                        summoner=summoner_in_db,
                        champion=p["championName"],
                        kills=p["kills"],
                        deaths=p["deaths"],
                        assists=p["assists"],
                        win=p["win"],
                        lane=p["teamPosition"]
                    )
                    match_participants += 1
                    summoner_participants += 1
                    total_participants += 1

                # Info
                self.stdout.write(f"Dodano {match_participants} uczestników do meczu {match_id}")

            # Info
            self.stdout.write(f"Gracz {summoner.riot_id}: {summoner_participants} uczestników łącznie")

        # Info
        self.stdout.write(f"PODSUMOWANIE: Dodano {total_participants} uczestników łącznie")
