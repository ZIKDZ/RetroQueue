from typing import Dict, List
from app.services.steam import get_steam_user

# map_name -> list of players waiting
queue: Dict[str, List[dict]] = {}

async def join_queue(steamid: str, map_name: str):
    player_info = await get_steam_user(steamid)
    if map_name not in queue:
        queue[map_name] = []
    queue[map_name].append(player_info)
    return player_info

def get_queue(map_name: str):
    return queue.get(map_name, [])