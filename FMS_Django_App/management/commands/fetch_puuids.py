import os
import time

import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from FMS_Django_App.models import SummonerName


class Command(BaseCommand):
    help = "Fetching players' summoner names' puuids"

    def handle(self, *args, **options):
        load_dotenv()
        api_key = str(os.getenv("RIOT_API_KEY"))

        if not api_key:
            self.stderr.write("Missing RIOT_API_KEY in .env file!")
            return

        headers = {
            "X-Riot-Token": api_key
        }

        for summoner in SummonerName.objects.all():
            if not summoner.puuid:  # łapie "", None, itp.
                try:
                    [gameName, tagLine] = summoner.riot_id.split("#")
                except ValueError:
                    self.stderr.write(f"Niepoprawny riot_id: {summoner.riot_id}")
                    continue

                puuid_url = (
                    f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
                    f"{gameName}/{tagLine}"
                )

                try:
                    response = requests.get(url=puuid_url, headers=headers)
                    response.raise_for_status()
                    puuid = response.json().get("puuid")
                    if not puuid:
                        self.stderr.write(f"Brak PUUID dla: {summoner.riot_id}")
                        continue
                except requests.RequestException as e:
                    self.stderr.write(f"Błąd API: {e}")
                    continue

                summoner.puuid = puuid
                summoner.save()
                self.stdout.write(f"Added puuid for {summoner.player}'s account {summoner.riot_id}: {puuid}")

                time.sleep(1.5)

