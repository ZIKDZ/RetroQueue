# models/match.py
from pydantic import BaseModel
from typing import List, Dict

class Player(BaseModel):
    steam_id: str
    name: str = None
    health: int
    armor: int
    weapons: Dict[str, Dict]  # weapon_name -> weapon stats
    state: Dict[str, int]     # position, alive, etc.
    match_stats: Dict[str, int]

class Match:
    def __init__(self, match_id, map_name, round_number, players, status, container_id=None):
        self.match_id = match_id
        self.map_name = map_name
        self.round_number = round_number
        self.players = players
        self.status = status
        self.container_id = container_id