# app/models/match.py
from pydantic import BaseModel
from typing import List, Optional

class Match(BaseModel):
    id: str
    map_name: str
    parties: List[str]
    max_players: int
    container_id: Optional[str] = None
    port: Optional[int] = None
    status: str = "waiting"  # waiting -> in_game -> finished