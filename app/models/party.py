from pydantic import BaseModel
from typing import List

class Party(BaseModel):
    id: str  # unique party ID
    leader_id: str  # Steam ID of the leader
    members: List[str]  # list of Steam IDs