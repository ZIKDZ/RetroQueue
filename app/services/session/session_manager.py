# app/services/session/session_manager.py

import docker
from typing import Dict, Optional
from app.services.session.port_manager import get_free_port, release_port

client = docker.from_env()

CSGO_IMAGE = "cm2network/csgo:sourcemod"

# TEMP: move this later to env file
STEAM_TOKEN = "YOUR_TOKEN_HERE"

# Track active sessions (matches)
active_sessions: Dict[str, dict] = {}


def start_session(map_name: str, max_players: int = 10) -> Optional[dict]:
    """
    Start a CS:GO server container for a match session.
    Automatically assigns a free port.
    """
    port = get_free_port()

    try:
        container_name = f"csgo_match_{port}"

        container = client.containers.run(
            CSGO_IMAGE,
            detach=True,
            network_mode="host",
            environment={
                "SRCDS_TOKEN": STEAM_TOKEN,
                "SRCDS_PORT": str(port),
                "SRCDS_STARTMAP": map_name,
                "SRCDS_MAXPLAYERS": str(max_players),
                "SRCDS_GAMETYPE": "0",
                "SRCDS_GAMEMODE": "1",
                "SRCDS_LAN": "0",
                "SRCDS_TICKRATE": "128",
                "SRCDS_HOSTNAME": f"Match Server {port}",
            },
            volumes={
                "/home/ilias/csgo-server/server": {
                    "bind": "/home/steam/csgo-dedicated",
                    "mode": "rw"
                }
            },
            name=container_name,
            remove=True,
        )

        session_info = {
            "container_id": container.id,
            "port": port,
            "map": map_name,
            "status": "running",
        }

        active_sessions[container.id] = session_info

        return session_info

    except Exception as e:
        print(f"[ERROR] Failed to start session: {e}")

        # IMPORTANT: release port if container failed
        release_port(port)

        return None


def stop_session(container_id: str) -> bool:
    """
    Stop a running match session and release its port.
    """
    try:
        session = active_sessions.get(container_id)

        container = client.containers.get(container_id)
        container.stop()

        # release port AFTER stopping
        if session:
            release_port(session["port"])

        active_sessions.pop(container_id, None)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to stop session: {e}")
        return False


def list_sessions():
    """
    Return all active sessions.
    """
    return list(active_sessions.values())