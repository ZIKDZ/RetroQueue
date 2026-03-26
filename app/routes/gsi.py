# app/routes/gsi.py
from fastapi import APIRouter, Request, HTTPException
from app.services.gsi_manager import handle_gsi_payload, get_match_by_match_id

router = APIRouter(prefix="/gsi", tags=["gsi"])

# --- GSI Webhook: POST match state from CS:GO server (HIDDEN FROM DOCS) ---
# Handle both /gsi and /gsi/ to avoid redirect issues
@router.post("", include_in_schema=False)
@router.post("/", include_in_schema=False)
async def receive_gsi(request: Request):
    """
    Internal endpoint: Receive Game State Interface (GSI) payload from CS:GO server.
    GSI plugin sends match_id in the JSON payload to identify which match to update.
    """
    payload = await request.json()
    
    try:
        # Extract match_id from payload (sent by GSI plugin)
        match_id = payload.get("match_id")
        print(f"[GSI] POST received - match_id: {match_id}, players in payload: {len(payload.get('players', []))}")
        
        if not match_id:
            raise ValueError("match_id is required in GSI payload")
        
        if match_id == "UNKNOWN":
            raise ValueError("match_id is UNKNOWN - handshake may not have completed yet")
        
        match_id = handle_gsi_payload(payload, match_id)
        
        # Parse players if it's a string
        players_data = payload.get('players', [])
        if isinstance(players_data, str):
            import json
            players_data = json.loads(players_data)
        num_players = len(players_data) if isinstance(players_data, list) else 0
        
        print(f"[GSI] ✓ Updated match {match_id} with {num_players} players")
    except Exception as e:
        print(f"[GSI] ✗ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "match_id": match_id}

# --- Get match info by match ID ---
@router.get("/{match_id}")
async def get_match_info(match_id: str):
    """
    Retrieve current match information by match ID.
    Returns match data including all players, stats, phase, and round number.
    """
    match = get_match_by_match_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"No match found for match_id {match_id}")
    
    return {"status": "ok", "match": match}
