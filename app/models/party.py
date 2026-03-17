from pydantic import BaseModel, Field
from typing import List
import uuid

class Party(BaseModel):
    party_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    party_code: str = Field(default_factory=lambda: uuid.uuid4().hex[:6].upper())
    leader: str  # SteamID of the party leader
    players: List[str] = []  # List of SteamIDs
    max_players: int = 10  # Optional, default max party size