from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates


from app.server.routes.patient import router as PatientRouter

app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.include_router(PatientRouter, tags=["Patient"], prefix="/patient")

@app.get("/", tags=["Root"])
async def read_root(request: Request):
    return templates.TemplateResponse("template.html", {"request": request})
    


