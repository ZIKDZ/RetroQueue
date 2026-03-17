# app/services/matchmaking.py
from typing import Dict, List
from uuid import uuid4
from app.services.party import get_party_by_id
from app.models.party import Party
from app.models.match import Match

# ------------------------------
# Allowed competitive maps
# ------------------------------
ALLOWED_MAPS = ["de_dust2", "de_mirage", "de_inferno"]

# ------------------------------
# In-memory queue: map_name -> list of Party objects
# ------------------------------
queue: Dict[str, List[Party]] = {}

# ------------------------------
# In-memory matches: match_id -> Match object
# ------------------------------
matches: Dict[str, Match] = {}

# ------------------------------
# Join queue with a party
# ------------------------------
def join_queue(party_id: str, maps: List[str]) -> dict:
    """
    Add a party to the selected maps' queues.
    Returns a dict with status and created matches (if any).
    Only allows parties in 'lobby' state to join.
    """
    party = get_party_by_id(party_id)
    if not party:
        return {"error": "Invalid party ID"}

    # Check party state
    if party.state == "queue":
        return {"error": f"Party is already queued on map(s): {', '.join([m for m, q in queue.items() if party in q])}"}
    if party.state == "in_match":
        return {"error": "Party is currently in a match"}

    # Validate maps
    valid_maps = [m for m in maps if m in ALLOWED_MAPS]
    if not valid_maps:
        return {"error": "No valid maps provided. Allowed maps: " + ", ".join(ALLOWED_MAPS)}

    created_matches = []

    for map_name in valid_maps:
        # Initialize map queue if it doesn't exist
        if map_name not in queue:
            queue[map_name] = []

        # Prevent duplicate party entries in the same map queue
        if party in queue[map_name]:
            continue

        # Add party to queue and update state
        queue[map_name].append(party)
        party.state = "queue"

        # Check if enough players to create a match
        total_players = sum(len(p.players) for p in queue[map_name])
        if total_players >= 10:
            match_parties = []
            players_count = 0

            # Select parties in queue order until we reach 10 players
            for p in queue[map_name]:
                if players_count + len(p.players) <= 10:
                    match_parties.append(p)
                    players_count += len(p.players)
                else:
                    break

            # Remove matched parties from queue and update state
            for p in match_parties:
                queue[map_name].remove(p)
                p.state = "in_match"

            # Create the match
            match_id = str(uuid4())
            match = Match(
                id=match_id,
                map_name=map_name,
                parties=[p.party_id for p in match_parties],
                max_players=10
            )
            matches[match_id] = match
            created_matches.append(match)

    return {
        "message": "Party queued successfully",
        "queued_party": party.party_id,
        "created_matches": [m.dict() for m in created_matches]
    }

# ------------------------------
# Get current queue for a map
# ------------------------------
def get_queue(map_name: str) -> List[dict]:
    """
    Returns a list of parties in the queue for the given map.
    """
    return [p.dict() for p in queue.get(map_name, [])]

# ------------------------------
# Get all active matches
# ------------------------------
def get_active_matches() -> List[dict]:
    """
    Returns all current matches.
    """
    return [m.dict() for m in matches.values()]