from pydantic import BaseModel
from typing import List

class Match(BaseModel):
    id: str  # unique match ID
    map_name: str
    parties: List[str]  # list of party IDs
    max_players: int