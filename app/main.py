from fastapi import FastAPI
from app.routes import matchmaking, parties, dev, gsi  # <-- added gsi

app = FastAPI()

# include the routers
app.include_router(matchmaking.router, prefix="/matchmaking")
app.include_router(parties.router, prefix="/parties")
app.include_router(dev.router)
app.include_router(gsi.router)  # <-- GSI endpoint (prefix defined in router)
