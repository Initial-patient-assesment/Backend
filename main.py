from typing import Dict, List, Optional 
from pymongo.mongo_client import MongoClient
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status, Form, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import time
import jwt
from decouple import config
from pydantic import BaseModel, Field,EmailStr
from rich.console import Console
import motor.motor_asyncio
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware
from passlib.handlers.sha2_crypt import sha512_crypt as crypto
import hashlib 

from sub_app.server.database import (
    add_user,
    delete_user,
    retrieve_user,
    retrieve_users,
    update_user,

)
from sub_app.server.models import (
    ErrorResponseModel,
    ResponseModel,
    UserSchema,
    UpdateUserModel,
)

console = Console()

class User(BaseModel):
    user_id: str
    username: str = Field(...) #should be changed to EmailStr
    hashed_password: str = Field(...)
       
pass_secret = config('pass_secret')
#client = pymongo.MongoClient("mongodb://localhost:27017/")
uri = f"mongodb+srv://sseed932:{pass_secret}@ipa.ciuyw6c.mongodb.net/?retryWrites=true&w=majority&appName=IPA"
client =  MongoClient(uri)

try:
    client.admin.command('ping')
    console.log('db - yes')
except Exception as e:
    console.log(e)

db = client["users"]
user_collection = db["users_collection"]

#helpers
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "login": user["login"],
        "password": user["password"],
    }

# Retrieve all users present in the database
def get_users():
    users = []
    for user in user_collection.find():
      		users.append(user_helper(user))
    return users


def get_user_id(username: str) -> User:
    DB = get_users()
    users = []
    for user in DB:
    	if user.get("login") == username:
    		users.append(user)
    if users:
        res_user = users[0]
     
        return res_user.get('id')
    return None

def get_user_with_id(id):
    DB =  get_users()
    users = []
    for user in DB:
    	if user.get("id") == id:
    		users.append(user)
    if users:
        res_user = users[0]
     
        return res_user
    return None

app = FastAPI()
#templates = Jinja2Templates(directory="templates")

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["GET", "POST"],  
    allow_headers=["*"],  
)
# --------------------------------------------------------------------------
# Authentication logic
# --------------------------------------------------------------------------

class UserLoginSchema(BaseModel):
    login: EmailStr = Field(...)
    password: str = Field(...)

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

def token_response(token: str):
    return {
        "access_token": token
    }
    
def signJWT(user_id: str) -> Dict[str, str]:
    
    payload = {
        "user_id": user_id,
        "expires": time.time() + 300
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
        
def check_user(data: UserLoginSchema):
    DB =  get_users() 
    for user in DB:
        if user.get('login') == data.login and crypto.verify(data.password,  user.get("password")):
            return True
    return False
    
@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema):
    if check_user(user):
       console.log("logged in")
       id = get_user_id(user.login)
       console.log("JWT signed")
       return signJWT(id)
      
    	    
    return {
        
           console.log("Wrong login details!")
      
    }    
    
    

    
####################Secure token###################################


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        if payload:
            isTokenValid = True
        return isTokenValid
        
    def get_user(self, jwtoken: str):
        payload = None

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None
        
        return payload
 
        
class token1(BaseModel):
        
	token : str

@app.post("/token", tags=["user"])
async def tok(tok : token1):
    a = JWTBearer()
    if JWTBearer.verify_jwt(a, tok.token):
    	return True
    return False
    
@app.post("/get_user", tags=["user"])
def get_user_data(token: token1) -> dict: 
    a = JWTBearer()
    data = JWTBearer.get_user(a, token.token)
    if data:
    	res_data = get_user_with_id(data.get("user_id"))
    	result = {"name" : res_data.get('name'), "login": res_data.get('login'),"password": res_data.get('password')}
    	if res_data:
    		return result
    	else:
    		return None
        
    

#################registration##########################


def check_login(username: str):
    DB = get_users()
    for user in DB:
    	if user.get("login") == username:
   	   				return False
   	
    return True
	

@app.post("/register", tags=["user"])
async def register_user(user:UserSchema):
    if check_login(user.login):
	    schema_extra = { 
	     		"name": user.name,
		        "login": user.login,
		        "password": crypto.hash(user.password),
		 	   }
	    new_user = await add_user(schema_extra)
	    return {"message": "User registered successfully"}  
    else:
    	    return {"message": "Login already registrated"}	      

##############################################################################
#optional
@app.put("/{id}")
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
    
#optional
@app.delete("/{id}", dependencies=[Depends(JWTBearer())], response_description="user data deleted from the database")
async def delete_user_data(id: str):
    deleted_user = await delete_user(id)
    if deleted_user:
        return ResponseModel(
            "user with ID: {} removed".format(id), "user deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "user with id {0} doesn't exist".format(id)
    )
