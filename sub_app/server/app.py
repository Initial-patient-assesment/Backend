from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


from app.server.routes.user import router as UserRouter




app = FastAPI()
templates = Jinja2Templates(directory="templates")


app.include_router(UserRouter, tags=["User"], prefix="/user")

@app.get("/", tags=["Root"])
async def read_root(request: Request):
   return templates.TemplateResponse("template.html", {"request": request})
    



