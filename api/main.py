# Python
from dotenv import load_dotenv

# FastAPI
from fastapi import FastAPI, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

# Routers
from routers import users, token, super_list

load_dotenv()

app = FastAPI()

app.mount(
    path = "/docs",
    app = StaticFiles(directory="./docs"),
    name = "docs"
)

# Routers
app.include_router(token.router)
app.include_router(users.router)
app.include_router(super_list.router)


### PATH OPERATIONS ###

@app.get(
        path = "/",
        response_class = HTMLResponse
)
async def root():
    return FileResponse(
        path = "./docs/index.html",
        status_code = status.HTTP_200_OK
    )