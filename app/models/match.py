# models/match.py
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import uuid4

# ------------------------------
# Player model (matches GSI plugin)
# ------------------------------
class Player(BaseModel):
    steam_id: str      # from "steamid"
    name: str          # player name
    team: str          # "T", "CT", or "SPECTATOR"
    kills: int
    deaths: int
    assists: int
    alive: bool

# ------------------------------
# Match model (matches GSI plugin)
# ------------------------------
class Match(BaseModel):
    match_id: str = Field(default_factory=lambda: str(uuid4()))
    container_id: Optional[str] = None  # Link to Docker container/session
    map_name: str
    round_number: int = 0
    phase: str = "warmup"  # "warmup", "live", "ended"
    players: List[Player] = []
