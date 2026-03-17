from typing import Dict, List
from app.services.steam import get_steam_user

# Map queues: map_name -> list of players waiting
queue: Dict[str, List[dict]] = {}

# Define allowed maps
VALID_MAPS = ["de_dust2", "de_mirage", "de_inferno"]

async def join_queue(steamid: str, map_name: str):
    """
    Add a player to a map queue after validating the map and fetching Steam info.
    """
    # Validate map
    if map_name not in VALID_MAPS:
        return {"error": f"Invalid map. Allowed maps: {', '.join(VALID_MAPS)}"}

    # Fetch player info from Steam
    player_info = await get_steam_user(steamid)
    if not player_info:
        return {"error": "Invalid SteamID or Steam API failed"}

    # Initialize queue if it doesn't exist
    if map_name not in queue:
        queue[map_name] = []

    # Add player to queue (duplicate entries are intentional for now)
    queue[map_name].append(player_info)

    return player_info

def get_queue(map_name: str):
    """
    Return the list of players in a map queue.
    Only minimal info (steam_id and username) is returned for safety.
    """
    if map_name not in VALID_MAPS:
        return {"error": f"Invalid map. Allowed maps: {', '.join(VALID_MAPS)}"}

    players = queue.get(map_name, [])
    # Return minimal info only
    return [{"steam_id": p["steam_id"], "username": p["username"]} for p in players]