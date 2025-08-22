import os
import time

import requests
from django.core.management import BaseCommand
from dotenv import load_dotenv

from FMS_Django_App.models import SummonerName

"""
Management command for fetching Riot PUUIDs of players stored in the database.

Operations that are made:
1. Getting Riot Games Account ID and splitting it into two separate parts - gameName and tagLine
2. Calling Riot Games API to fetch PUUID of the account
"""


class Command(BaseCommand):
    help = "Fetching players' summoner names' PUUIDs"

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
        headers = {
            "X-Riot-Token": api_key
        }

        # Iterate through summoners one by one to fetch PUUIDs
        for summoner in SummonerName.objects.all():

            # Check if puuid already exists
            if not summoner.puuid:
                try:
                    # Splitting Riot Games Account ID to gameName and tagline.
                    [gameName, tagLine] = summoner.riot_id.split("#")
                except ValueError:
                    self.stderr.write(f"Niepoprawny riot_id: {summoner.riot_id}")
                    continue

                # Request URL for getting puuid of the account
                puuid_url = (
                    f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/"
                    f"{gameName}/{tagLine}"
                )

                try:

                    #Fetching
                    response = requests.get(url=puuid_url, headers=headers)
                    response.raise_for_status()

                    # Getting PUUID immediately
                    puuid = response.json().get("puuid")

                    # Check if there is PUUID of the account
                    if not puuid:
                        self.stderr.write(f"Brak PUUID dla: {summoner.riot_id}")
                        continue
                except requests.RequestException as e:
                    self.stderr.write(f"Błąd API: {e}")
                    continue

                # Save puuid to database
                summoner.puuid = puuid
                summoner.save()

                #Info
                self.stdout.write(f"Added puuid for {summoner.player}'s account {summoner.riot_id}: {puuid}")

                #Bypassing rate limits
                time.sleep(1.5)
