from .steam import get_player_info

async def join_matchmaking(steam_id: str):
    player_info = await get_player_info(steam_id)
    if not player_info:
        return {"error": "Invalid Steam ID or API error."}

    username = player_info.get("personaname")
    avatar = player_info.get("avatarfull")
    return {"steam_id": steam_id, "username": username, "avatar": avatar}