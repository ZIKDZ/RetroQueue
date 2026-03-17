# app/services/party.py
from typing import Dict, Optional
from app.models.party import Party

# In-memory storage
parties: Dict[str, Party] = {}            # party_id -> Party
player_to_party: Dict[str, str] = {}      # steam_id -> party_id

# ------------------------------
# Create a new party
# ------------------------------
def create_party(leader_steamid: str, max_players: int = 10) -> Party:
    """
    Create a new party with the leader as the first member.
    """
    # Check if leader is already in a party
    if leader_steamid in player_to_party:
        party_id = player_to_party[leader_steamid]
        return parties[party_id]

    party = Party(
        leader=leader_steamid,
        players=[leader_steamid],
        max_players=max_players,
        state="lobby"
    )
    parties[party.party_id] = party
    player_to_party[leader_steamid] = party.party_id
    return party

# ------------------------------
# Join a party using its code
# ------------------------------
def join_party(player_steamid: str, party_code: str) -> dict:
    """
    Join a party by code. Returns a dict with status or error.
    """
    # Check if player is already in a party
    if player_steamid in player_to_party:
        return {"error": "Player is already in a party"}

    # Find target party by code
    target_party = next((p for p in parties.values() if p.party_code == party_code), None)
    if not target_party:
        return {"error": "Invalid party code"}

    # Check if party is full
    if len(target_party.players) >= target_party.max_players:
        return {"error": "Party is full"}

    # Add player to party
    target_party.players.append(player_steamid)
    player_to_party[player_steamid] = target_party.party_id

    # Party state remains lobby if not queued
    return {"message": "Player joined party", "party": target_party}

# ------------------------------
# Leave a party
# ------------------------------
def leave_party(player_steamid: str) -> Optional[Party]:
    """
    Player leaves their party.
    Returns updated party or None if disbanded.
    """
    party_id = player_to_party.get(player_steamid)
    if not party_id:
        return None

    party = parties.get(party_id)
    if not party:
        return None

    # Remove player
    if player_steamid in party.players:
        party.players.remove(player_steamid)
        del player_to_party[player_steamid]

    # Handle leader leaving
    if party.leader == player_steamid:
        if party.players:
            party.leader = party.players[0]
        else:
            del parties[party_id]
            return None

    # Reset state to lobby if no longer queued
    if party.state != "in_match":
        party.state = "lobby"

    return party

# ------------------------------
# Get party by ID
# ------------------------------
def get_party_by_id(party_id: str) -> Optional[Party]:
    return parties.get(party_id)

# ------------------------------
# Get party a player belongs to
# ------------------------------
def get_party_by_player(steam_id: str) -> Optional[Party]:
    party_id = player_to_party.get(steam_id)
    if not party_id:
        return None
    return parties.get(party_id)