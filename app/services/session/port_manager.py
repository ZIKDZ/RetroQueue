# app/services/session/port_manager.py

from typing import Set

START_PORT = 27015
MAX_PORT = 27100

used_ports: Set[int] = set()


def get_free_port() -> int:
    """
    Find and reserve a free port.
    """
    for port in range(START_PORT, MAX_PORT):
        if port not in used_ports:
            used_ports.add(port)
            return port

    raise RuntimeError("No free ports available")


def release_port(port: int):
    """
    Release a port after a match ends.
    """
    used_ports.discard(port)


def list_used_ports():
    return list(used_ports)