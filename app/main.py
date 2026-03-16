from fastapi import FastAPI
from app.routes import matchmaking

app = FastAPI()

# include the router
app.include_router(matchmaking.router, prefix="/matchmaking")