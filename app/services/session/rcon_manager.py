# app/services/session/rcon_manager.py
import time
from valve.rcon import RCON
from app.services.session.session_manager import active_sessions

class RCONManager:
    def __init__(self):
        self.sessions = active_sessions
        self.retry_count = 5
        self.retry_delay = 1  # seconds

    def send_command(self, container_id: str, command: str):
        session = self.sessions.get(container_id)
        if not session:
            raise Exception(f"No active session with container_id {container_id}")

        port = session["port"]
        rcon_password = session.get("rcon_password")
        if not rcon_password:
            raise Exception(f"No RCON password set for container {container_id}")

        last_exception = None
        for _ in range(self.retry_count):
            try:
                # Connect via RCON using a tuple for host/port
                with RCON(("127.0.0.1", port), rcon_password) as rcon:
                    result = rcon(command)
                return result
            except Exception as e:
                last_exception = e
                time.sleep(self.retry_delay)

        raise Exception(f"Failed to connect to RCON for container {container_id} after {self.retry_count} retries: {last_exception}")