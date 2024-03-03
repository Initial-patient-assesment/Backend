from fastapi import APIRouter, Body, Form, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
import json

#ALGORITHM = "HS256"
templates = Jinja2Templates(directory="templates")


from app.server.database import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,

)
from app.server.models import (
    ErrorResponseModel,
    ResponseModel,
    UserSchema,
    UpdateUserModel,
)


router = APIRouter()

@router.post("/", response_description="user data added into the database")
async def submit(request: Request, name: str = Form(...),login: str = Form(...), password: str = Form(...)):

   
    return templates.TemplateResponse("template.html", {"login":login,"password":password,"request": request,"name":name})
    
    
@router.post("/red")
async def add(name: str = Form(...), login: str = Form(...), password: str = Form(...)):
   
    schema_extra = { 
    		"name": f"{name}",
                "login": f"{login}",   
                "password": crypto.hash(password),
         	   }
   # schema_extraJS = json.dumps(schema_extra)
  
    #user = jsonable_encoder(schema_extraJS)
    new_user = await add_user(schema_extra)
    return RedirectResponse('http://0.0.0.0:8000', status_code=status.HTTP_303_SEE_OTHER)

    
@router.get("/", response_description="users retrieved")
async def get_users():
    users = await retrieve_users()
    if users:
        return ResponseModel(users, " data retrieved successfully")
    return ResponseModel(users, "Empty list returned")


@router.get("/{id}", response_description="users data retrieved")
async def get_user_data(id):
    user = await retrieve_user(id)
    if user:
        return ResponseModel(user, "user data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "user doesn't exist.")

@router.put("/{id}")
async def update_user_data(id: str, req: UpdateUserModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_user = await update_user(id, req)
    if updated_user:
        return ResponseModel(
            "user with ID: {} name update is successful".format(id),
            "user name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the user data.",
    )

@router.delete("/{id}", response_description="user data deleted from the database")
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseModel(
            "user with ID: {} removed".format(id), "user deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "user with id {0} doesn't exist".format(id)
    )

@router.delete("/", response_description="user data deleted from the database")
async def delete_all():
    users = await retrieve_users()
    for i in users:
    	deleted_user = await delete_user(i.get('id'))
    	
######----------------------------------------------------#######

 
