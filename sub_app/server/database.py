import motor.motor_asyncio
from rich.console import Console
from bson.objectid import ObjectId

MONGO_DETAILS = "mongodb+srv://sseed932:alexapol6044333963@ipa.ciuyw6c.mongodb.net/?retryWrites=true&w=majority&appName=IPA"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.users

user_collection = database.get_collection("users_collection")
doctor_collection = database.get_collection("doctors_collection")
appointment_collection = database.get_collection("appointments_collection")
clinic_collection = database.get_collection("clinics_collection")

# helpers
from sub_app.server.models import (
    ErrorResponseModel,
    ResponseModel,
    UserSchema,
    DoctorSchema,
    UpdateUserModel,
    UpdateAppointModel_User,
)


def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "login": user["login"],
        "password": user["password"],
    }

console = Console()
# Retrieve all users present in the database
async def retrieve_users():
    users = []
    async for user in user_collection.find():
      		users.append(user_helper(user))
    return users


# Add a new user into to the database
async def add_user(user_data: dict):
    user = await user_collection.insert_one(user_data)
    new_user = await user_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)

async def add_doctor(doctor_data: dict):
    doctor = await doctor_collection.insert_one(doctor_data)
    app_data = {"doctor_id": str(doctor.inserted_id),"requests" : [], "confirms" : []}
    app = await appointment_collection.insert_one(app_data)
     
async def add_clinic(clinic_data: dict):
    clin = await clinic_collection.insert_one(clinic_data)
    new_clin = await user_collection.find_one({"_id": clin.inserted_id})
    

# Retrieve a user with a matching ID
async def retrieve_user(id: str) -> dict:
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        return user_helper(user)


async def update_app(data: dict):
    # Return false if an empty request body is sent.
    doc_id = data.get("doctor_id")
    flag = await appointment_collection.find_one({"doctor_id": doc_id}, {"requests":{"$elemMatch":{ "date": (data.get("request")).get("date"), "user_id": data.get("user_id")}}})
    flag1 = await appointment_collection.find_one({"doctor_id": doc_id}, {"confirms":{"$elemMatch":{ "date": (data.get("request")).get("date"), "user_id": data.get("user_id")}}})
    flag2 = await appointment_collection.find_one({"doctor_id": doc_id}, {"confirms":{"$elemMatch": { "date": (data.get("request")).get("date"), "time" : (data.get("request")).get("time")}}})
  
    flag3 = await appointment_collection.find_one({"doctor_id": doc_id}, {"requests":{"$elemMatch": {"date": (data.get("request")).get("date"),"time" : (data.get("request")).get("time")}}})
    #console.log(flag2)
    app = await appointment_collection.find_one({"doctor_id": doc_id})
    if app and not (flag.get("requests") or flag1.get("confirms") or flag2.get("confirms") or flag3.get("requests")):
    	
        updated_app = await appointment_collection.update_one(
        	{"doctor_id": doc_id}, {"$push": {"requests": {"date": (data.get("request")).get("date"), "time" : (data.get("request")).get("time"), "user_id": data.get("user_id") }}}
        )
        if updated_app:
            return True
        return False

async def confirm_appointment(data: dict):
    doc_id = data.get("doctor_id")
   # console.log(data.get("date"))
    app = await appointment_collection.find_one({"doctor_id": doc_id})
    #console.log("database", data.get("flag")
    if app:
        updated_app = await appointment_collection.update_one(
        	{"doctor_id": doc_id}, {"$push": {"confirms": {"date": (data.get("request")).get("date"),"time" : (data.get("request")).get("time"),"user_id": data.get("user_id")}}}
        
        )
        dele = appointment_collection.update_one({"doctor_id": doc_id}, {"$pull": {"requests": {"user_id": data.get("user_id"), "date": (data.get("request")).get("date")}}})
        if updated_app:
            return True
        return False

async def confirm_app(data: dict):
    doc_id = data.get("doctor_id")
    app = await appointment_collection.find_one({"doctor_id": doc_id})
    console.log("database", data.get("flag"))
    if app:
        updated_app = await appointment_collection.update_one(
        	{"doctor_id": doc_id,"requests.Confirm": False}, {"$set": {"requests.$.Confirm": data.get("flag")}}
        )
        if updated_app:
            return True
        return False
	

# Update a user with a matching ID
async def update_user(id: str, data: dict):
    # Return false if an empty request body is sent.
  #  console.log(data)
 #   console.log("   ")
   # console.log("id")
    if len(data) < 1:
        return False
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        updated_user = await user_collection.update_one(
           {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_user:
            return True
        return False


# Delete a user from the database
async def delete_user(id: str):
    user = await user_collection.find_one({"_id": ObjectId(id)})
    if user:
        await user_collection.delete_one({"_id": ObjectId(id)})
        return True

async def add_doc_to_userbase(clinic_data: dict):
    
    updated_user  = await user_collection.update_one(
        	{"_id": ObjectId(clinic_data.get("id"))}, {"$push": {"doctors_ids": clinic_data.get("doc_id")}}
        )
    console.log(updated_user)
    if updated_user:
            return True
    return False

