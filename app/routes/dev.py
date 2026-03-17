# app/routes/dev.py
from fastapi import APIRouter, Query
from typing import Optional
from app.services.session.session_manager import start_session, stop_session, list_sessions
from app.services.session.port_manager import get_free_port
from app.services.session.rcon_manager import RCONManager  # <- fixed import path

router = APIRouter(prefix="/dev", tags=["dev"])

# Initialize RCON manager (for testing purposes)
rcon_manager = RCONManager()

# ------------------------------
# Start a test session with a chosen map
# ------------------------------
@router.post("/start")
def start_test_session(
    map_name: str = Query("de_dust2", description="Map to start the server on"),
    max_players: int = Query(10, description="Maximum number of players for the server")
):
    # Use fixed RCON password for dev testing
    session = start_session(map_name=map_name, max_players=max_players)
    if not session:
        return {"error": "Failed to start session"}
    return {"session": session}


# ------------------------------
# Stop a session by container_id
# ------------------------------
@router.post("/stop/{container_id}")
def stop_test_session(container_id: str):
    success = stop_session(container_id)
    return {"stopped": success}


# ------------------------------
# List active sessions
# ------------------------------
@router.get("/sessions")
def get_sessions():
    return {"sessions": list_sessions()}


# ------------------------------
# Test free port assignment
# ------------------------------
@router.get("/port")
def test_port():
    return {"port": get_free_port()}


# ------------------------------
# Send a raw RCON command to a running session
# ------------------------------
@router.post("/rcon/{container_id}")
def send_rcon_command(
    container_id: str,
    command: str = Query(..., description="RCON command to send")
):
    """
    Send a command to the CS:GO server via RCON.
    Uses the fixed password from the session manager for dev/testing.
    """
    try:
        result = rcon_manager.send_command(container_id, command)
        return {"container_id": container_id, "command": command, "result": result}
    except Exception as e:
        return {"error": str(e), "container_id": container_id, "command": command}