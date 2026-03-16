import os
import httpx
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

STEAM_API_KEY = os.getenv("STEAM_API_KEY")
STEAM_API_URL = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"

# app/services/steam.py
import os
import httpx

STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "YOUR_HARDCODED_KEY")

async def get_steam_user(steam_id: str) -> dict | None:
    """
    Fetch minimal Steam info for matchmaking: steamid and persona name.
    """
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
            players = data.get("response", {}).get("players", [])
            if not players:
                return None
            player = players[0]
            # Return only the minimal info needed
            return {
                "steam_id": player.get("steamid"),
                "username": player.get("personaname"),
                "avatar": player.get("avatarfull"),
            }
        except Exception as e:
            print(f"[Steam Service] Error fetching {steam_id}: {e}")
            return None