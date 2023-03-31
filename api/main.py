# FastAPI
from fastapi import FastAPI

# Routers
from routers import users, token


app = FastAPI()

# Routers
app.include_router(token.router)
app.include_router(users.router)


### PATH OPERATIONS ###

@app.get("/")
async def root():
    return "Hello FastAPI"