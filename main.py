from typing import Dict, List, Optional 
from pymongo.mongo_client import MongoClient
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status, Form, Body, File
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
from prompts import (get_token, get_chat_completion)
import json
from datetime import datetime
import time
from pdf.p import create_rep
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.pagesizes import letter
import io
from fastapi.responses import StreamingResponse, FileResponse, Response

from sub_app.server.database import (
    add_user,
    delete_user,
    retrieve_users,
    update_user,
    update_app,
    add_doctor,
    confirm_appointment1,
    add_clinic,
    add_doc_to_userbase,
    reject_appointment,

)
from sub_app.server.models import (
    ErrorResponseModel,
    ResponseModel,
    UserSchema,
    UpdateUserModel,
    DoctorSchema,
    UpdateAppointModel_User,
    doc_conf,
    doc_conf1,
    UserLoginSchema,
    ClinicSchema,
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

db = client["users"] # an organisation name not "users"
user_collection = db["users_collection"]
doctor_collection = db["doctors_collection"]
appointment_collection = db["appointments_collection"]
clinic_collection = db["clinics_collection"]
prom_history = db["prom_history"]

#helpers
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "login": user["login"],
        "birth": user["birth"],
        "address": user["address"],
        "main_doctor_id": user["main_doctor_id"],
        "history": user["history"],
        "password": user["password"],
        "doctors_ids":user["doctors_ids"],
        "convos": user["convos"],
    }

    
def doctor_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "specialty": user["specialty"],
        "name": user["name"],
        "surname": user["surname"],
        "father_name": user["father_name"],
        "email": user["email"],
        "login": user["login"],
        "password": user["password"],

    }
    
def doctor_helper_for_user(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "surname": user["surname"],
        "father_name": user["father_name"],
        "email": user["email"],
        "specialty": user["specialty"],
        "working_days": user["working_days"],
    }    
 
def clinic_helper(user) -> dict:
    return {
        "name": user["name"],
        "address": user["address"],
        "email": user["email"],
        "working_days": user["working_days"],
        "phone_number": user["phone_number"],

    } 
    
    
def prom_helper(user):
    return user["conv_history"]
 
def app_helper(user):
    return user["requests"]

def app_helper_conf(user):
   # return user["confirms"]
    return user["confirms"], user["doctor_id"]
      
def doc_helper_user(user):
    return user["doctors_ids"]

def conf_helper(user) -> dict:
    return user["confirms"]

def app_helper1(user)->dict:
    return user["requests"]
    
def conv_helper(user):
    return user["convos"]

# Retrieve all users present in the database
def get_users():
    users = []
    for user in user_collection.find():
      		users.append(user_helper(user))
    return users

def get_docs():
    users = []
    for user in doctor_collection.find():
      		users.append(doctor_helper(user))
    return users
    
def get_appointments(user_id):
    apps = []
    ask = appointment_collection.find({"requests":{"$elemMatch":{"user_id": user_id}}})
    ask1 = appointment_collection.find({"confirms":{"$elemMatch":{ "user_id": user_id}}})
    for app in ask:
      		apps.append(app_helper1(app))
    for app1 in ask1:
      		apps.append(conf_helper(app1))
      		
    count = 0
    for app_card in apps:
    	for app in app_card:
    		count = count + 1
    if count > 3:
    	return False   	
    return apps
   
def get_docs_for_user():
    users = []
    for user in doctor_collection.find():
      		users.append(doctor_helper_for_user(user))
    return users

# -> User deleted
def get_user_id(username: str) :
    DB = get_users()
    users = []
    for user in DB:
    	if user.get("login") == username:
    		users.append(user)
    if users:
        res_user = users[0]
     
        return res_user.get('id')
    return None
    
def get_doctor_id(username: str) :
    DB = get_docs()
    users = []
    for user in DB:
    	if user.get("login") == username:
    		users.append(user)
    if users:
        res_user = users[0]
     
        return res_user.get('id')
    return None
    
def get_doctor_id_email(username: str) :
    DB = get_docs()
    users = []
    for user in DB:
    	if user.get("email") == username:
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
    
def get_doc_with_id(id):
    DB =  get_docs()
    
    users = []
    for user in DB:
    	if user.get("id") == id:		
    		users.append(user)
    if users:
        res_user = users[0]
     
        return res_user
    return None
	
def get_doc_with_id_for_user(id):
    DB =  get_docs_for_user()
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
    allow_methods=["GET", "POST", "PUT"],  
    allow_headers=["*"],  
)
# --------------------------------------------------------------------------
# Authentication logic
# --------------------------------------------------------------------------

class DoctorLoginSchema(BaseModel):
    login: str = Field(...)
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
        "expires": time.time() + 3000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)

def decodeJWT(token: str) -> dict:  
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if get_user_with_id(decoded_token.get('user_id')):
        	return decoded_token if decoded_token["expires"] >= time.time() else None
       	else : None
    except:
        return {}

def decodeJWT_doc(token: str) -> dict:  
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if get_doc_with_id((decoded_token).get('user_id')):
        	
        	return decoded_token if decoded_token["expires"] >= time.time() else None
       	else : None
    except:
        return {}
        
def check_user(data: UserLoginSchema):
    DB =  get_users() 
    for user in DB:
        if user.get('login') == data.login and crypto.verify(data.password,  user.get("password")):
            return True
    return False
    
def check_dock(data: DoctorLoginSchema):
    DB =  get_docs() 
    for user in DB:
        if user.get('login') == data.login and crypto.verify(data.password,  user.get("password")):
            return True
    return False
    
@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema):
    if check_user(user):
       id = get_user_id(user.login)
       return signJWT(id) 	    
    return ErrorResponseModel(
        	"An error occurred",
        	404,
        	"There was no such user.",
    		)
   
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
        
    def verify_jwt_doc(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT_doc(jwtoken)
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


@app.post("/user_token", tags=["user"])
async def tok(tok : token1):
    a = JWTBearer()
    if JWTBearer.verify_jwt(a, tok.token):
    	return True
    return False
    
@app.post("/token", tags=["doctor"])
async def tok1(tok : token1):
    a = JWTBearer()
    if JWTBearer.verify_jwt_doc(a, tok.token):
    	return True
    return False


@app.post("/get_user", tags=["user"])
def get_user_data(token: token1) -> dict: 
    a = JWTBearer()
    data = JWTBearer.get_user(a, token.token)
    if data:
    	res_data = get_user_with_id(data.get("user_id"))
    	result = {"name" : res_data.get('name'), "login": res_data.get('login'),"birth": res_data.get('birth'),"address": res_data.get('address'), "clinic_id": res_data.get('clinic_id'), "main_doctor_id": res_data.get('main_doctor_id'), "history": res_data.get('history'), "doctors_ids": res_data.get('doctors_ids'),"convos": res_data.get('convos')}
    	if res_data:
    		return result
    	else:
    		return None
    	
    		
class doc_id(BaseModel):
	doc_id : str
	token : str
	
		
@app.put("/add_doc_to_user", tags=["user"])
async def add_doc_to_user(doc_id:doc_id) -> dict: 
    a = JWTBearer()
    data = JWTBearer.get_user(a, doc_id.token) 
    if data:
    	id = data.get("user_id")
    	schema_extra = {"doc_id":doc_id.doc_id, "id":id }
    else : return ErrorResponseModel(
        	"An error occurred",
        	404,
        	"There was no such user.",
    		)
    res = await add_doc_to_userbase(schema_extra)
    if res:
    	return {"message": "User updated successfully"}  
    else: 
    	return {"message": "NO UPDATE"}  
    	
@app.post("/get_user's_docs_by_id", tags=["user"])
async def get_doc_by_id(token:token1): 
    a = JWTBearer()
    data = JWTBearer.get_user(a, token.token) 
    id = ''
    if data:
    	id = data.get("user_id")
    	
    else : return ErrorResponseModel(
        	"An error occurred",
        	404,
        	"There was no such user.",
    		)
    	
    user_doc_ids = []
    for user in user_collection.find({"_id": ObjectId(id)}, {"doctors_ids"}):
    	user_doc_ids.append(doc_helper_user(user))
 
    res = []
    for id in user_doc_ids[0]:
    	res.append(get_doc_with_id_for_user(id))
    return res
 
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
		        "birth": user.birth,
		        "doctors_ids": [],
		        "address": '',
		        "main_doctor_id": '',
		        "history": [{'name':'', 'time':''}],
		        "login": user.login,
		        "password": crypto.hash(user.password),
		        "convos": [],
		 	   }
	    new_user = await add_user(schema_extra)
	    return {"message": "User registered successfully"}  
    else:
    	    return {"message": "Login already registrated"}	      

###################Doctor#####################################################


@app.post("/add_doc", tags=["doctor"])
async def register_doc(doctor:DoctorSchema):
  
	schema_extra = { 
	     		"name": doctor.name,
	     		"surname": doctor.surname,
    			"father_name": doctor.father_name,
    			"specialty": doctor.specialty,
    			"working_days": doctor.working_days,
    			"email": doctor.email,
		        "login": doctor.login,
		        "password": crypto.hash(doctor.password),
		        "clinic_name": doctor.clinic_name,
		 	   }
	new_doctor = await add_doctor(schema_extra)
	#app_schema = {}
		
	return {"message": "Doctor added successfully"} 


@app.post("/doctor/login", tags=["doctor"])
async def doc_login(user: DoctorLoginSchema):
    if check_dock(user):   
       id = get_doctor_id(user.login)
       return signJWT(id)
       	    
    return ErrorResponseModel(
        	"An error occurred",
        	404,
        	"There was no such user.",
    		)  

@app.put("/add_appointment_data",tags=["user"])
async def add_appointment_data(upd: UpdateAppointModel_User):
    try:
        user_id = str(decodeJWT(upd.token).get("user_id"))
    except:
        return ErrorResponseModel("No such user found",404, "login again")
    a = get_appointments(user_id)
    if a != False:
        today = datetime.today().strftime('%Y-%m-%d')
        app_date = f"20{upd.year}-{upd.month}-{upd.day}"
        tod = time.strptime(today, "%Y-%m-%d")
        to_app = time.strptime(app_date, "%Y-%m-%d")
        if to_app < tod:
            return ErrorResponseModel("An error occurred", 405, "You can't appoint before today")
        req = {"date":app_date,"time":f"{upd.hour}:{upd.minutes}"}
        update_schema = {"doctor_id" : get_doctor_id_email(upd.doctor_email),"user_id" : str(user_id), "request" :req}
        updated_app = await update_app(update_schema)
        if updated_app:
            return {"message": "User appointed successfully"}
        return ErrorResponseModel("An error occurred", 111, "There was an error updating the appointment data.")
    else:
        return ErrorResponseModel("You can't appoint more than 4 times",444,"error")


        
class r_id(BaseModel):
	
        token : str
        idd: str
      
@app.post("/conf", tags =['doctor'])
async def conf1(conf_data:r_id):
    doctor_id = str(decodeJWT_doc(conf_data.token).get("user_id"))
    confirm_schema = {"doctor_id":doctor_id,'r_id' : conf_data.idd}
    updated_app = await confirm_appointment1(confirm_schema)
    if updated_app:
        return {"message": "User appointed successfully"} 
          
    return ErrorResponseModel(
     "An error occurred",
        404,
        "There was an error updating the appointment data.",
    )
    
@app.post("/reject", tags =['doctor'])
async def conf1(conf_data:r_id):
    doctor_id = str(decodeJWT_doc(conf_data.token).get("user_id"))
    confirm_schema = {"doctor_id":doctor_id,'r_id' : conf_data.idd}
    updated_app = await reject_appointment(confirm_schema)
    if updated_app:
        return {"message": "User rejected successfully"} 
          
    return ErrorResponseModel(
     "An error occurred",
        404,
        "There was an error updating the appointment data.",
    )    

##############################################################################
#optional
'''
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
   ''' 
    
@app.put("/change_user_data",tags=["user"])
async def update_user_data(token: token1,req: UpdateUserModel= Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    a = JWTBearer()
    data = JWTBearer.get_user(a, token.token)
    if data:
    	id = data.get("user_id")
    else: 
    	 return ErrorResponseModel(
        "No such user",
        404,
        "There was an error updating the user data.",
    )    
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

##############################################################################
def get_confirms(doctor_id):
	elems = []
	appointment_card = appointment_collection.find({"doctor_id" : doctor_id})
	for elem in appointment_card:
			elems.append(conf_helper(elem))
	return elems

def get_requests(doctor_id):
	elems = []
	appointment_card = appointment_collection.find({"doctor_id" : doctor_id})
	for elem in appointment_card:
			elems.append(app_helper(elem))
	return elems


@app.post("/events_docs", tags=["doctor"])
def get_events(token:token1):
    doctor_id = str(decodeJWT_doc(token.token).get("user_id"))
    reqs = get_confirms(doctor_id)
    try:
    	requests = reqs[0]
    except:
    	pass
    returned = []
    for req in requests:
    	date = req.get("date")
    	time = req.get("time")
    	user = get_user_with_id(req.get("user_id")).get("name")
    	new = {"title": user, "start": f'{date}T{time}:00', "end": f'{date}T{time[0]}{time[1]}:30:00', "allDay": False }
    	returned.append(new)
	
    return returned
    

@app.post("/suggested_events", tags=["doctor"])
def get_suggested_events(token:token1):
    doctor_id = str(decodeJWT_doc(token.token).get("user_id"))
    reqs = get_requests(doctor_id)
    requests = reqs[0]
    returned = []
    for req in requests:
    	date = req.get("date")
    	time = req.get("time")
    	user = get_user_with_id(req.get("user_id")).get("name")
    	new = {"username": user,"id":req.get('req_id'),"title": "Appointment", "start": f'{date}T{time}:00', "end": f'{date}T{time[0]}{time[1]}:30:00', "allDay": False}
    	returned.append(new)
    return returned

@app.post("/recent_patients", tags=["doctor"])
async def get_events(token:token1):
    doctor_id = str(decodeJWT_doc(token.token).get("user_id"))
    reqs = get_confirms(doctor_id)
  
    try:
    	requests = reqs[0]
    except:
    	pass
    returned = []
    for req in requests:
    	id = req.get("user_id")
    	u = get_user_with_id(id)
    	user = u.get("name")
    	user_birth = u.get('birth')
    	new = {'username': user, 'birth':user_birth,'user_id': req.get("user_id") }
    	if new not in returned:
    		returned.append(new)
    	console.log(returned)	

    return returned
	
def get_confirms_user(user_id):
	elems = []
	appointment_card = appointment_collection.find({"confirms":{"$elemMatch":{"user_id" : user_id}}})
	for elem in appointment_card:
			elems.append(app_helper_conf(elem))
	return elems

class Item(BaseModel):
    start: str = "2024-04-09T10:00:00"
    end: str = "2024-04-09T10:30:00"
    doc_name: str = "Aniket"
    doc_surname: str = "Sarode"
    doc_specialty: str = "Paediatrics"
    email: str = "ankit@gmail.com"
    
@app.post("/user_confirmed_events",tags=["user"],response_model=list[Item])
def get_events(token:token1):
    user_id = str(decodeJWT(token.token).get("user_id"))
    reqs = get_confirms_user(user_id)
    returned = []
    for appointment in reqs:
	    requests = appointment[0]	    
	    for req in requests:
	    	date = req.get("date")
	    	time = req.get("time")
	    	doc = get_doc_with_id(appointment[1])
	    	new = {"start": f'{date}T{time}:00', "end": f'{date}T{time[0]}{time[1]}:30:00',"doc_name": doc.get('name'),"doc_surname": doc.get('surname'),"father_name": doc.get('father_name'),"doc_specialty": doc.get('specialty'), "email": doc.get('email') }
	    	returned.append(new)
	
    return returned

###################Clinic#####################################################


@app.post("/add_clinic", tags=["clinic"])
async def register_clinic(clin:ClinicSchema):
  
	schema_extra = { 
	     		"name": clin.name,
	     		"address": clin.address,
    			"working_days": clin.working_days,
    			"email": clin.email,
		        "phone_number": clin.phone_number,
		 	   }
	new_doctor = await add_clinic(schema_extra)
		
	return {"message": "Clinic added successfully"} 
	
class clin_name(BaseModel):       
	clinic_name : str

@app.post("/get_clinics_by_name", tags=["clinic", "user"])
def get_clinics(clin:clin_name):
    clinics = []
    for user in clinic_collection.find({"name":clin.clinic_name}):
      		clinics.append(clinic_helper(user))
    return clinics

@app.post("/get_doctors_by_clinic_name", tags=["clinic", "user"])
def get_docs_by_clinics(clin:clin_name):
    docs = []
    for user in doctor_collection.find({"clinic_name":clin.clinic_name}):
      		 docs.append(doctor_helper_for_user(user))
    return  docs

###################Prompts#####################################################

class prompt(BaseModel):
    token: str
    prompt_text: str
    
class prompt_examp(BaseModel):
    response: str

@app.post("/promt_bot", tags=["bot", "user"],response_model=prompt_examp)
async def send_prompt(pr:prompt):
    auth = str(config('auth'))
    response2 = get_token(auth)
    giga_token = ''
    if response2 != 1:
        giga_token = response2.json()['access_token']
    user_id = str(decodeJWT(pr.token).get("user_id"))
    exist = None
    try:
        exist = prom_history.find_one({"user_id": user_id})
    except:
        pass
    if exist == None:
        pr_data = {"user_id": user_id, "conv_history":[]}
        prom_history.insert_one(pr_data)
    history = [{
    	'role': 'system',
    	'content': 'You are a doctor(your name: "GigaDoc", surname: "AIowitch")talking to a real patient. You have to understand the person''s illness and set potential diagnosis by asking questions about their health. After asking many questions about health then ALWAYS ASK the person if they have made an appointment with a dcoctor, if no, ONLY THEN recommend a type of doctor they should visit In the end of each conversation. Never reveal diagnosis when asked by the patient - just say that the real doctor will set the diagnosis. Talk about medicine only. In the end of each conversation say - "Take care!'
}]
	
    updated_prom = prom_history.update_one(
        	{"user_id": user_id}, {"$push": {"conv_history": { "role": "user", "content": pr.prompt_text}}})
        	
    strings = 0  	
    his = prom_history.find_one({"user_id": user_id})
    t = datetime.today().strftime("d%d-%m t%H_%M")
    try:
        conv = prom_helper(his)
        for el in conv:
            history.append(el)
            strings = strings + 1
    except: pass
    if strings <= 22:
	    response = get_chat_completion(giga_token, history)
	    resp_data = response.json()['choices'][0]['message']['content']	    
    else:
       resp_data = 'This is the end of our conversation. Take care!'
    updated_prom = prom_history.update_one(
			{"user_id": user_id}, {"$push": {"conv_history": { "role": "assistant", "content": resp_data}}}
		)
    if 'Take care!' in resp_data:   	    
        f = open("demofile2.txt", "a")
        conv.append({"role": "assistant", "content": resp_data})
        fileinput = []
        fileinput.append({"convo":conv})
        history.append(
        {
        'role':'user',
        'content':"give several potential diagnosis in one field 'potential_diagnosis' and only patient'symptomps in another field 'patient_symptoms' - this all in json - asked by real doctor"
        }
        )
        diag = get_chat_completion(giga_token, history)
        print(diag.json()['choices'][0]['message']['content'])
        fileinput.append(diag.json()['choices'][0]['message']['content'])
        f.write(str(fileinput)+'\n'+'-------------------------------------------------------------------'+"\n")
        f.close()
        prom_history.delete_one({"user_id": user_id})
        user_collection.update_one({"_id": ObjectId(user_id)}, {"$push": {"convos": {'filename':t, 'convo':fileinput}}})
        
    return {'response': resp_data.split('\n',1)[0]}
    
class pdflist(BaseModel):
    user_id: str
    
@app.post("/get_pdfs_list", tags=["doctor"])
def pdflist(sch:pdflist):
    convos = user_collection.find({"_id": ObjectId(sch.user_id)})
    l = []
    for conv in convos:
    	l.append(conv_helper(conv))
    filenames = []
    for elem in l[0]:
    	filenames.append(elem["filename"])
    return filenames


class forpdf(BaseModel):
    user_id: str
    filename: str

@app.post("/get_pdf", tags=["doctor"])
def pdf(sch:forpdf):
    datadb = user_collection.find_one({"_id": ObjectId(sch.user_id)}, {"convos":{"$elemMatch":{ "filename": sch.filename}}})
    data = datadb['convos'][0]['convo']
    doc = create_rep(data)
    buf = io.BytesIO() 
    pdf = SimpleDocTemplate(buf, pagesize=letter,rightMargin=12,leftMargin=36,topMargin=12,bottomMargin=6)
    pdf.build(doc)
    buf.seek(0) 
    
    return Response(content = buf.getvalue(), headers={'content-disposition': 'attachment','media_type':'application/pdf'})

