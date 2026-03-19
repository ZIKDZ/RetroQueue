# app/services/gsi_manager.py
from typing import Dict, Any
from app.models.match import Match, Player
from fastapi import HTTPException

# In-memory storage for MVP
active_matches: Dict[str, Match] = {}  # match_id → Match object

def handle_gsi_payload(payload: Dict[str, Any]) -> str:
    """
    Process incoming CS:GO/CS2 GSI JSON payload.
    Supports local player + allplayers (observer) payloads.
    Returns match_id for the match.
    """

    # --- 1. Check provider ---
    provider = payload.get("provider", {})
    if not provider.get("name"):
        raise ValueError("No provider info in payload")

    # --- 2. Auth check (optional, can skip if token not required) ---
    auth = payload.get("auth", {})

    # --- 3. Map / Round info ---
    map_info = payload.get("map", {})
    map_name = map_info.get("name", "unknown")
    round_phase = map_info.get("phase", "unknown")
    round_num = payload.get("round", {}).get("round", 0) or map_info.get("round", 0)

    # --- 4. Players ---
    players: Dict[str, Player] = {}

    # 4a. Single local player
    player_data = payload.get("player", {})
    if player_data:
        steam_id = str(player_data.get("steamid") or player_data.get("id"))
        players[steam_id] = _build_player(player_data)

    # 4b. Observer / allplayers
    allplayers_data = payload.get("allplayers", {})
    for steam_id, pdata in allplayers_data.items():
        players[steam_id] = _build_player(pdata)

    if not players:
        raise ValueError("No player data found in payload")

    # --- 5. Generate a match_id (simple MVP: map + round + first player) ---
    first_player_id = next(iter(players))
    match_id = f"{map_name}_{round_num}_{first_player_id[:8]}"

    # --- 6. Update or create Match ---
    if match_id in active_matches:
        match = active_matches[match_id]
        for pid, p in players.items():
            # Replace or add
            for i, mp in enumerate(match.players):
                if mp.steam_id == pid:
                    match.players[i] = p
                    break
            else:
                match.players.append(p)
        match.round_number = round_num
    else:
        match = Match(
            match_id=match_id,
            map_name=map_name,
            round_number=round_num,
            players=list(players.values()),
            status="ongoing"
        )
        active_matches[match_id] = match

    return match_id


def _build_player(player_data: Dict[str, Any]) -> Player:
    """
    Convert a player JSON block into Player object.
    Handles all fields from GSI docs.
    """
    steam_id = str(player_data.get("steamid") or player_data.get("id"))
    name = player_data.get("name", "Unknown")
    team = player_data.get("team", "SPECTATOR")

    state = player_data.get("state", {})
    match_stats = player_data.get("match_stats", {})

    weapons: Dict[str, Dict[str, Any]] = {}
    raw_weapons = player_data.get("weapons", {})
    for key, w in raw_weapons.items():
        if isinstance(w, dict):
            weapons[key] = {
                "name": w.get("name"),
                "ammo_clip": w.get("ammo_clip"),
                "ammo_reserve": w.get("ammo_reserve"),
                "state": w.get("state"),
            }

    return Player(
        steam_id=steam_id,
        name=name,
        team=team,
        health=state.get("health", 0),
        armor=state.get("armor", 0),
        state={
            "flashed": state.get("flashed", 0),
            "burning": state.get("burning", 0),
            "money": state.get("money", 0),
            "round_kills": state.get("round_kills", 0),
            "round_killhs": state.get("round_killhs", 0),
            "alive": state.get("health", 0) > 0,
        },
        weapons=weapons,
        match_stats=match_stats
    )