# app/routes/gsi.py
from fastapi import APIRouter, Request, HTTPException
from app.services.gsi_manager import handle_gsi_payload, get_match_by_match_id

router = APIRouter(prefix="/gsi", tags=["gsi"])

@router.post("", include_in_schema=False)
@router.post("/", include_in_schema=False)
async def receive_gsi(request: Request):
    payload = await request.json()

    try:
        match_id = payload.get("match_id")

        if not match_id:
            raise ValueError("match_id is required in GSI payload")

        if match_id == "UNKNOWN":
            raise ValueError("match_id is UNKNOWN - handshake may not have completed yet")

        match_id = handle_gsi_payload(payload, match_id)

        players_data = payload.get('players', [])
        if isinstance(players_data, str):
            import json
            players_data = json.loads(players_data)

        total = len(players_data) if isinstance(players_data, list) else 0
        connected = sum(1 for p in players_data if p.get("connected", True))  # NEW

        print(f"[GSI] ✓ Updated match {match_id} — {connected}/{total} players connected")

    except Exception as e:
        print(f"[GSI] ✗ Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

    return {"status": "ok", "match_id": match_id}

@router.get("/{match_id}")
async def get_match_info(match_id: str):
    match = get_match_by_match_id(match_id)
    if not match:
        raise HTTPException(status_code=404, detail=f"No match found for match_id {match_id}")
    return {"status": "ok", "match": match}