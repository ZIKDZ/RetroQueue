# app/routes/matchmaking.py
from fastapi import APIRouter
from typing import List
from app.services.matchmaking import join_queue, get_queue, get_active_matches

router = APIRouter()

# ------------------------------
# Allowed competitive maps
# ------------------------------
ALLOWED_MAPS = ["de_dust2", "de_mirage", "de_inferno"]

# ------------------------------
# Join matchmaking queue with a party
# ------------------------------
@router.post("/join")
def join_matchmaking(party_id: str, maps: List[str]):
    """
    Add a party to one or more map queues.
    Returns queued party and any matches created.
    Only allows maps in ALLOWED_MAPS.
    """
    # Filter maps to only include allowed maps
    valid_maps = [m for m in maps if m in ALLOWED_MAPS]
    if not valid_maps:
        return {"error": "No valid maps provided. Allowed maps: " + ", ".join(ALLOWED_MAPS)}

    result = join_queue(party_id, valid_maps)
    return result

# ------------------------------
# Inspect queue for a map
# ------------------------------
@router.get("/queue/{map_name}")
def queue_status(map_name: str):
    """
    Returns all parties currently in the queue for a map.
    """
    if map_name not in ALLOWED_MAPS:
        return {"error": "Invalid map. Allowed maps: " + ", ".join(ALLOWED_MAPS)}
    return {"parties_in_queue": get_queue(map_name)}

# ------------------------------
# Get all active matches
# ------------------------------
@router.get("/matches")
def active_matches():
    """
    Returns all current matches.
    """
    return {"matches": get_active_matches()}