from pydantic import BaseModel
from typing import List

class Party(BaseModel):
    id: str
    leader: str
    players: List[str]