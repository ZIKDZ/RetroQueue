# app/services/gsi_manager.py
from typing import Dict, Any, Optional
from app.models.match import Match, Player
from app.services.session.session_manager import active_sessions

active_matches: Dict[str, Match] = {}
match_id_to_container: Dict[str, str] = {}

def handle_gsi_payload(payload: Dict[str, Any], match_id: str) -> str:
    import json

    map_name = payload.get("map", "unknown")
    phase = payload.get("phase", "unknown")
    round_number = payload.get("round_number", 0)

    players_data = payload.get("players", [])

    if isinstance(players_data, str):
        try:
            players_data = json.loads(players_data)
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse players JSON string: {players_data}")

    # Build Player objects — now includes connected field
    players = []
    for pdata in players_data:
        players.append(Player(
            steam_id=pdata.get("steamid", "UNKNOWN"),
            name=pdata.get("name", "Unknown"),
            team=pdata.get("team", "SPECTATOR"),
            kills=pdata.get("kills", 0),
            deaths=pdata.get("deaths", 0),
            assists=pdata.get("assists", 0),
            alive=pdata.get("deaths", 0) < 1,
            connected=pdata.get("connected", True),  # NEW
        ))

    if match_id in active_matches:
        match = active_matches[match_id]
        match.round_number = round_number
        match.phase = phase

        # Merge snapshot into existing player roster by steam_id.
        # Players not yet in the snapshot (not connected yet) keep their
        # skeleton entry untouched — only connected players get updated.
        snapshot_by_id = {p.steam_id: p for p in players}
        merged = []
        for existing in match.players:
            if existing.steam_id in snapshot_by_id:
                # Replace skeleton with live data from the snapshot
                merged.append(snapshot_by_id[existing.steam_id])
            else:
                # Player not in snapshot yet — keep skeleton as-is
                merged.append(existing)
        match.players = merged
    else:
        container_id = _get_container_by_match_id(match_id)
        if not container_id:
            raise ValueError(f"No container found for match_id {match_id}")

        match = Match(
            match_id=match_id,
            map_name=map_name,
            round_number=round_number,
            phase=phase,
            players=players,
            container_id=container_id
        )
        active_matches[match_id] = match
        match_id_to_container[match_id] = container_id

    return match_id

def get_match_by_container_id(container_id: str) -> Optional[Match]:
    for session_data in active_sessions.values():
        if session_data.get("container_id") == container_id:
            match_id = session_data.get("match_id")
            if match_id:
                return active_matches.get(match_id)
    return None

def get_match_by_match_id(match_id: str) -> Optional[Match]:
    return active_matches.get(match_id)

def _get_container_by_match_id(match_id: str) -> Optional[str]:
    for session_data in active_sessions.values():
        if session_data.get("match_id") == match_id:
            return session_data.get("container_id")
    return None