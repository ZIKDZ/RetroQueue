# models/match.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

class Player(BaseModel):
    steam_id: str
    name: str
    team: str
    kills: int
    deaths: int
    assists: int
    alive: bool
    connected: bool = True  # NEW — false when player disconnected but still in roster

class Match(BaseModel):
    match_id: str = Field(default_factory=lambda: str(uuid4()))
    container_id: Optional[str] = None
    map_name: str
    round_number: int = 0
    phase: str = "warmup"
    players: List[Player] = []