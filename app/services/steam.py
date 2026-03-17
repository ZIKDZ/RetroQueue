import os
import httpx
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get Steam API key from environment or fallback
STEAM_API_KEY = os.getenv("STEAM_API_KEY", "YOUR_HARDCODED_KEY")

async def get_steam_user(steam_id: str) -> dict | None:
    """
    Fetch minimal Steam info for matchmaking: steamid, username, and avatar.
    Returns None if the Steam API call fails or the SteamID is invalid.
    """
    url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
    params = {"key": STEAM_API_KEY, "steamids": steam_id}

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            resp = await client.get(url, params=params)
            resp.raise_for_status()  # Raises exception if HTTP status != 200

            if not resp.text.strip():
                print(f"[Steam Service] Empty response for {steam_id}")
                return None

            data = resp.json()
            players = data.get("response", {}).get("players", [])
            if not players:
                print(f"[Steam Service] No player found for {steam_id}")
                return None

            player = players[0]

            return {
                "steam_id": player.get("steamid"),
                "username": player.get("personaname"),
                "avatar": player.get("avatarfull"),
            }

        except httpx.RequestError as e:
            print(f"[Steam Service] Network error for {steam_id}: {e}")
            return None
        except ValueError:
            print(f"[Steam Service] Invalid JSON returned for {steam_id}")
            return None
        except Exception as e:
            print(f"[Steam Service] Unexpected error for {steam_id}: {e}")
            return None