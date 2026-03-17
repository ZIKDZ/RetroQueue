# app/services/party.py
from typing import Dict, Optional
from app.models.party import Party

# In-memory storage
parties: Dict[str, Party] = {}            # party_id -> Party
player_to_party: Dict[str, str] = {}      # steam_id -> party_id

def create_party(leader_steamid: str, max_players: int = 10) -> Party:
    """
    Create a new party with the leader as the first member.
    """
    # Check if leader is already in a party
    if leader_steamid in player_to_party:
        party_id = player_to_party[leader_steamid]
        return parties[party_id]

    party = Party(leader=leader_steamid, players=[leader_steamid], max_players=max_players)
    parties[party.party_id] = party
    player_to_party[leader_steamid] = party.party_id
    return party

def join_party(player_steamid: str, party_code: str) -> Optional[Party]:
    """
    Join a party using its code.
    Returns the updated Party or None if join failed.
    """
    # Check if player is already in a party
    if player_steamid in player_to_party:
        return None

    # Find party by code
    target_party = next((p for p in parties.values() if p.party_code == party_code), None)
    if not target_party:
        return None

    # Check max players
    if len(target_party.players) >= target_party.max_players:
        return None

    # Add player
    target_party.players.append(player_steamid)
    player_to_party[player_steamid] = target_party.party_id
    return target_party

def leave_party(player_steamid: str) -> Optional[Party]:
    """
    Player leaves their party.
    Returns updated party or None if party is disbanded.
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
            # Transfer leadership to next player
            party.leader = party.players[0]
        else:
            # Disband party if empty
            del parties[party_id]
            return None

    # Return updated party
    return party

def get_party_by_id(party_id: str) -> Optional[Party]:
    """
    Retrieve party by its ID.
    """
    return parties.get(party_id)

def get_party_by_player(steam_id: str) -> Optional[Party]:
    """
    Retrieve the party a player belongs to.
    """
    party_id = player_to_party.get(steam_id)
    if not party_id:
        return None
    return parties.get(party_id)