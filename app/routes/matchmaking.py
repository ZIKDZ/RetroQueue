from fastapi import APIRouter
from app.services.matchmaking import join_queue, get_queue

router = APIRouter()

@router.post("/join")
async def join_matchmaking(steamid: str, map_name: str):
    player = await join_queue(steamid, map_name)
    return {"message": "Player joined", "player": player}

@router.get("/queue/{map_name}")
def queue_status(map_name: str):
    return {"players": get_queue(map_name)}