from fastapi import FastAPI
from app.routes import matchmaking
from app.routes import parties,dev

app = FastAPI()

# include the router
app.include_router(matchmaking.router, prefix="/matchmaking")
app.include_router(parties.router, prefix="/parties")
app.include_router(dev.router)