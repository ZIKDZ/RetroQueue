# app/services/gsi_manager.py
from typing import Dict, Any, Optional
from app.models.match import Match, Player
from app.services.session.session_manager import active_sessions

# In-memory matches
active_matches: Dict[str, Match] = {}  # match_id -> Match object
match_id_to_container: Dict[str, str] = {}  # match_id -> container_id (for GSI identification)

def handle_gsi_payload(payload: Dict[str, Any], match_id: str) -> str:
    """
    Process incoming GSI plugin JSON payload.
    Maps data to Match and Player models.
    Uses match_id (sent by plugin) to identify and update the match.
    Returns match_id.
    """
    import json
    
    # --- Basic validation ---
    map_name = payload.get("map", "unknown")
    phase = payload.get("phase", "unknown")
    round_number = payload.get("round_number", 0)

    players_data = payload.get("players", [])
    
    # Handle case where players is a JSON string (from SourceMod plugin)
    if isinstance(players_data, str):
        try:
            players_data = json.loads(players_data)
        except json.JSONDecodeError:
            raise ValueError(f"Could not parse players JSON string: {players_data}")
    
    if not players_data:
        raise ValueError("No players in GSI payload")

    # --- Build Player objects ---
    players = []
    for pdata in players_data:
        players.append(Player(
            steam_id=pdata.get("steamid", "UNKNOWN"),
            name=pdata.get("name", "Unknown"),
            team=pdata.get("team", "SPECTATOR"),
            kills=pdata.get("kills", 0),
            deaths=pdata.get("deaths", 0),
            assists=pdata.get("assists", 0),
            alive=pdata.get("deaths", 0) < 1
        ))

    # --- Check if match_id already exists ---
    if match_id in active_matches:
        # Update existing match
        match = active_matches[match_id]
        match.players = players
        match.round_number = round_number
        match.phase = phase
    else:
        # --- Get container_id from session tracking ---
        container_id = _get_container_by_match_id(match_id)
        if not container_id:
            raise ValueError(f"No container found for match_id {match_id}")
        
        # --- Create new match linked to container ---
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
    """
    Retrieve match info by container ID.
    Returns Match object or None if not found.
    """
    # Find match_id by looking through session data
    for session_data in active_sessions.values():
        if session_data.get("container_id") == container_id:
            match_id = session_data.get("match_id")
            if match_id:
                return active_matches.get(match_id)
    return None

def get_match_by_match_id(match_id: str) -> Optional[Match]:
    """
    Retrieve match info by match ID.
    Returns Match object or None if not found.
    """
    return active_matches.get(match_id)

def _get_container_by_match_id(match_id: str) -> Optional[str]:
    """
    Internal helper: Get container_id by match_id.
    Looks it up in active_sessions.
    """
    for session_data in active_sessions.values():
        if session_data.get("match_id") == match_id:
            return session_data.get("container_id")
    return None
