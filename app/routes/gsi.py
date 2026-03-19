# app/routes/gsi.py
import json
from fastapi import APIRouter, Request, HTTPException
from app.services.gsi_manager import handle_gsi_payload  # keep your existing function

router = APIRouter()

@router.post("")
async def receive_gsi(request: Request):
    body_bytes = await request.body()

    if not body_bytes:
        return {"status": "error", "reason": "Empty payload"}

    try:
        payload = json.loads(body_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        return {"status": "error", "reason": f"Invalid JSON: {str(e)}"}
    except UnicodeDecodeError:
        return {"status": "error", "reason": "Invalid encoding (expected UTF-8)"}

    # Optional: enforce your auth token from cfg
    received_token = payload.get("auth", {}).get("token")
    if received_token != "CCWJu64ZV3JHDT8hZc":  # ← replace with your real token or make configurable
        raise HTTPException(status_code=401, detail="Invalid auth token")

    try:
        match_id = handle_gsi_payload(payload)
        return {"status": "ok", "match_id": match_id}
    except Exception as e:
        return {"status": "error", "reason": str(e)}