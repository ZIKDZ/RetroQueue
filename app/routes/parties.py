# app/routes/parties.py
from fastapi import APIRouter
from typing import Optional
from app.services.party import create_party, join_party, leave_party, get_party_by_id, get_party_by_player
from app.models.party import Party

router = APIRouter()

# ------------------------------
# Create a new party (solo or group leader)
# ------------------------------
@router.post("/create")
def api_create_party(leader_steamid: str, max_players: Optional[int] = 5):
    party = create_party(leader_steamid, max_players)
    return {"message": "Party created", "party": party.dict()}

# ------------------------------
# Join an existing party by code
# ------------------------------
@router.post("/join")
def api_join_party(player_steamid: str, party_code: str):
    party = join_party(player_steamid, party_code)
    if not party:
        return {"error": "Unable to join party (invalid code, party full, or already in a party)"}
    return {"message": "Joined party", "party": party.dict()}

# ------------------------------
# Leave current party
# ------------------------------
@router.post("/leave")
def api_leave_party(player_steamid: str):
    party = leave_party(player_steamid)
    if not party:
        return {"message": "Party disbanded or player was not in a party"}
    return {"message": "Left party", "party": party.dict()}

# ------------------------------
# Get party by ID
# ------------------------------
@router.get("/{party_id}")
def api_get_party(party_id: str):
    party = get_party_by_id(party_id)
    if not party:
        return {"error": "Party not found"}
    return {"party": party.dict()}

# ------------------------------
# Get the party the player belongs to
# ------------------------------
@router.get("/self/{steam_id}")
def api_get_party_by_player(steam_id: str):
    party = get_party_by_player(steam_id)
    if not party:
        return {"error": "Player is not in a party"}
    return {"party": party.dict()}