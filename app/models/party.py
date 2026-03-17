# app/models/party.py
from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4

class Party(BaseModel):
    party_id: str = Field(default_factory=lambda: str(uuid4()))
    party_code: str = Field(default_factory=lambda: str(uuid4())[:6])  # short join code
    leader: str  # steam_id of the leader
    players: List[str] = []  # list of steam_ids
    max_players: int = 5
    state: str = "lobby"  # "lobby", "queue", "in_match"