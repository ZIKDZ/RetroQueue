# app/services/session/session_manager.py

import docker
import os
import secrets
import time
import threading
from typing import Dict, Optional
from uuid import uuid4
from dotenv import load_dotenv
from app.services.session.port_manager import get_free_port, release_port

load_dotenv()

client = docker.from_env()

CSGO_IMAGE = "cm2network/csgo:sourcemod"

STEAM_TOKEN = os.environ["SRCDS_TOKEN"]  # GSLT from steamcommunity.com/dev/managegameservers

# Track active sessions (matches)
active_sessions: Dict[str, dict] = {}

# ------------------------------
# Start a CS:GO server session
# ------------------------------
def start_session(map_name: str, max_players: int = 10, players: list = None) -> Optional[dict]:
    """
    Start a CS:GO server container for a match session.
    Automatically assigns a free port, generates an RCON password, and creates a match ID.
    players is optional — omit it to start an empty test session.
    Each entry is a dict with keys: steam_id, team (CT or T).
    """
    port = get_free_port()
    rcon_password = secrets.token_hex(12)  # random 24-char hex password
    match_id = uuid4().hex  # unique match identifier in hex format (no dashes)

    try:
        container_name = f"csgo_match_{port}"

        container = client.containers.run(
            CSGO_IMAGE,
            detach=True,
            network_mode="host",
            environment={
                "SRCDS_TOKEN": STEAM_TOKEN,
                "SRCDS_PORT": str(port),
                "SRCDS_RCONPW": rcon_password,
                "SRCDS_STARTMAP": map_name,
                "SRCDS_MAXPLAYERS": str(max_players),
                "SRCDS_GAMETYPE": "0",
                "SRCDS_GAMEMODE": "1",
                "SRCDS_LAN": "0",
                "SRCDS_TICKRATE": "128",
                "SRCDS_HOSTNAME": f"Match Server {port}",
                "MATCH_ID": match_id,
            },
            volumes={
                "/home/ilias/csgo-server/server": {
                    "bind": "/home/steam/csgo-dedicated",
                    "mode": "rw"
                }
            },
            name=container_name,
            remove=True,  # auto-remove when stopped
        )

        session_info = {
            "container_id": container.id,
            "match_id": match_id,
            "port": port,
            "map": map_name,
            "rcon_password": rcon_password,
            "players": players or [],
            "status": "starting",  # Initially 'starting' until handshake succeeds
        }

        active_sessions[container.id] = session_info
        
        # Create initial match entry in gsi_manager
        from app.services.gsi_manager import active_matches
        from app.models.match import Match, Player

        # Pre-populate skeleton Player objects with team already set from matchmaking
        # Stats will be filled in once GSI payloads arrive
        skeleton_players = [
            Player(
                steam_id=p["steam_id"],
                name="",
                team=p.get("team", "UNASSIGNED"),
                kills=0,
                deaths=0,
                assists=0,
                alive=True,
                connected=False,
            )
            for p in (players or [])
        ]

        initial_match = Match(
            match_id=match_id,
            container_id=container.id,
            map_name=map_name,
            round_number=0,
            phase="warmup",
            players=skeleton_players,
        )
        active_matches[match_id] = initial_match
        print(f"[SESSION] Created initial match entry: {match_id} with {len(skeleton_players)} players")
        
        # Start handshake in background thread (non-blocking)
        # This way we return the session immediately and handshake happens in parallel
        handshake_thread = threading.Thread(
            target=_handshake_match_id,
            args=(container.id, match_id, rcon_password, port),
            daemon=True
        )
        handshake_thread.start()
        
        return session_info

    except Exception as e:
        print(f"[ERROR] Failed to start session: {e}")
        # Release port if container failed
        release_port(port)
        return None

# ------------------------------
# Stop a running session
# ------------------------------
def stop_session(container_id: str) -> bool:
    """
    Stop a running match session and release its port.
    """
    try:
        session = active_sessions.get(container_id)
        container = client.containers.get(container_id)
        container.stop()

        # Release port AFTER stopping
        if session:
            release_port(session["port"])

        active_sessions.pop(container_id, None)
        return True

    except Exception as e:
        print(f"[ERROR] Failed to stop session: {e}")
        return False

# ------------------------------
# List all active sessions
# ------------------------------
def list_sessions():
    """
    Return all active sessions.
    """
    return list(active_sessions.values())

# ------------------------------
# Handshake: Set match_id via RCON
# ------------------------------
def _handshake_match_id(container_id: str, match_id: str, rcon_password: str, port: int, max_retries: int = 30, retry_delay: float = 1.0, initial_delay: float = 10.0) -> bool:
    """
    Handshake with the server to set the match_id via RCON command.
    Runs in background thread. Updates session status when complete.
    """
    print(f"[HANDSHAKE] Waiting {initial_delay}s for server startup...")
    time.sleep(initial_delay)

    from app.services.session.rcon_manager import RCONManager
    rcon = RCONManager()
    print(f"[HANDSHAKE] Starting match_id handshake for {container_id}")

    for attempt in range(max_retries):
        try:
            result = rcon.send_command(container_id, f"sm_set_match_id {match_id}")

            if "[GSI_MATCHID_ACK]" in result and match_id in result:
                print(f"[HANDSHAKE] ✓ Match ID set on container {container_id}")
                if container_id in active_sessions:
                    active_sessions[container_id]["status"] = "running"
                return True
            else:
                print(f"[HANDSHAKE] Attempt {attempt + 1}/{max_retries}: Unexpected response")
        except Exception as e:
            print(f"[HANDSHAKE] Attempt {attempt + 1}/{max_retries}: {type(e).__name__}: {str(e)[:80]}")

        if attempt < max_retries - 1:
            time.sleep(retry_delay)

    print(f"[HANDSHAKE] ✗ FAILED: Could not set match_id on {container_id} after {max_retries} attempts")
    if container_id in active_sessions:
        active_sessions[container_id]["status"] = "handshake_failed"
    return False