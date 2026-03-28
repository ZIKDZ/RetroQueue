# app/services/matchmaking.py
from typing import Dict, List
from app.services.party import get_party_by_id
from app.models.party import Party
from app.services.session.session_manager import start_session

# ------------------------------
# Allowed competitive maps
# ------------------------------
ALLOWED_MAPS = ["de_dust2", "de_mirage", "de_inferno"]

# ------------------------------
# In-memory queue: map_name -> list of Party objects
# ------------------------------
queue: Dict[str, List[Party]] = {}

# ------------------------------
# Join queue with a party
# ------------------------------
def join_queue(party_id: str, maps: List[str]) -> dict:
    """
    Add a party to the selected maps' queues.
    When 10 players are ready, starts a session directly.
    Returns a dict with status and any started sessions.
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

    started_sessions = []

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

        # Check if enough players to start a session
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

            # Assign teams party by party — first party gets CT, second gets T,
            # keeping every party whole on the same team
            players = []
            for i, p in enumerate(match_parties):
                team = "CT" if i % 2 == 0 else "T"
                for steam_id in p.players:
                    players.append({"steam_id": steam_id, "team": team})

            # Remove matched parties from queue and update their state
            for p in match_parties:
                queue[map_name].remove(p)
                p.state = "in_match"

            # Start the session with the map and player+team list
            session = start_session(map_name=map_name, max_players=10, players=players)
            if session:
                session["status"] = "starting"
            else:
                session = {"map_name": map_name, "players": players, "status": "failed"}

            started_sessions.append(session)

    return {
        "message": "Party queued successfully",
        "queued_party": party.party_id,
        "started_sessions": started_sessions,
    }

# ------------------------------
# Get current queue for a map
# ------------------------------
def get_queue(map_name: str) -> List[dict]:
    """
    Returns a list of parties in the queue for the given map.
    """
    return [p.dict() for p in queue.get(map_name, [])]