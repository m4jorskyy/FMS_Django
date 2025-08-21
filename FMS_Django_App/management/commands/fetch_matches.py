import os
import time
from datetime import datetime, timezone

import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from ...models import SummonerName, Match, MatchParticipation


class Command(BaseCommand):
    help = "Fetch recent matches for all summonner names"

    def handle(self, *args, **options):
        load_dotenv()
        api_key = str(os.getenv("RIOT_API_KEY"))
        if not api_key:
            self.stderr.write("Missing RIOT_API_KEY in .env file!")
            return

        headers = {"X-Riot-Token": api_key}

        total_participants = 0  # Globalna statystyka

        for summoner in SummonerName.objects.all():
            self.stdout.write(f"\n=== Gracz: {summoner.riot_id} | PUUID: {summoner.puuid} ===")
            self.stdout.write(f"\n Pobieranie rangi konta: {summoner.riot_id}")

            rank_url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-puuid/{summoner.puuid}"
            rank_resp = requests.get(rank_url, headers=headers)
            time.sleep(1)

            if rank_resp.status_code != 200:
                self.stderr.write(f"Pobieranie rangi konta: {rank_resp.status_code} {rank_resp.text}")
                continue

            rank_api = rank_resp.json()
            if not rank_api:
                self.stdout.write("Brak danych rankingowych.")
                return False

            soloq = None
            for entry in rank_api:
                if entry.get('queueType') == 'RANKED_SOLO_5x5':
                    soloq = entry
                    break

            if not soloq:
                self.stderr.write("Brak Solo Queue rankingu")
                return False

            tier = soloq.get('tier', 'UNRANKED')
            rank = soloq.get('rank', '')
            league_points = soloq.get('leaguePoints', 0)

            SummonerName.objects.filter(id=summoner.id).update(
                tier=tier,
                rank=rank,
                league_points=league_points
            )

            self.stdout.write(f"Zaktualizowano rangę dla {summoner.riot_id}: {tier} {rank} {league_points} LP")

            summoner_participants = 0  # Dla tego gracza

            match_id_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner.puuid}/ids?start=0&count=20"
            resp = requests.get(match_id_url, headers=headers)
            time.sleep(1)

            if resp.status_code != 200:
                self.stderr.write(f"Pobieranie match IDs: {resp.status_code} {resp.text}")
                continue

            match_ids_api = resp.json()
            self.stdout.write(f"Pobrano {len(match_ids_api)} match_id: {match_ids_api}")

            if not match_ids_api:
                self.stderr.write("Brak meczów do przetworzenia")
                continue

            for match_id in match_ids_api:
                if Match.objects.filter(match_id=match_id).exists():
                    self.stdout.write(f"Pomijam {match_id} (już w bazie)")
                    continue

                self.stdout.write(f"Przetwarzam nowy mecz {match_id}")

                match_details_url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
                match_resp = requests.get(match_details_url, headers=headers)
                time.sleep(1)

                if match_resp.status_code != 200:
                    self.stdout.write(
                        f"Pobieranie szczegółów meczu {match_id}: {match_resp.status_code} {match_resp.text}")
                    continue

                match_details_api = match_resp.json()

                # Zapis meczu
                match_obj = Match.objects.create(
                    match_id=match_id,
                    game_duration=match_details_api["info"]["gameDuration"],
                    game_start=datetime.fromtimestamp(match_details_api["info"]["gameStartTimestamp"] / 1000,
                                                      tz=timezone.utc)
                )
                self.stdout.write(f"Dodano mecz: {match_id}")

                # Zapis uczestników
                participants = match_details_api["info"]["participants"]
                match_participants = 0  # Dla tego konkretnego meczu

                for p in participants:
                    puuid = p["puuid"]
                    summoner_in_db = SummonerName.objects.filter(puuid=puuid).first()
                    if not summoner_in_db:
                        continue

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

                self.stdout.write(f"Dodano {match_participants} uczestników do meczu {match_id}")

            self.stdout.write(f"Gracz {summoner.riot_id}: {summoner_participants} uczestników łącznie")

        self.stdout.write(f"PODSUMOWANIE: Dodano {total_participants} uczestników łącznie")