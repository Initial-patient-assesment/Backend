from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    name: str = Field(...)
    birth: str = Field(...)
    login: str = Field(...) #should be changed to EmailStr
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Aditya",
                "birth": "19.02.2004",
                "login": "aditya@gmail.com",
                "password": "12345",
            }
        }
'''
class UpdateAppointModel_User(BaseModel):
    doctor_email: str
    token: str #cannot be updated
 
    request: dict
    class Config:
        schema_extra = {
            "example": {
                "doctor_email": "ankit@gmail.com",
                "token": "",     
                "request": {"date":"12.12.2012","time":"10:30"},          
            }
        }
'''

class UpdateAppointModel_User(BaseModel):
    doctor_email: str
    token: str #cannot be updated
    
    day: str
    month : str
    year : str
    hour: str
    minutes: str
  #  request: dict
    class Config:
        schema_extra = {
            "example": {
                "doctor_email": "ankit@gmail.com",
                "token": "", 
                "day": "09",
                "month": "04",    
                "year": "24",
                "hour":"10",
                "minutes": "00"     
            }
        }

class doc_conf(BaseModel):
    token: str 
    #flag: bool
    user_id: str
    day: str
    month : str
    year : str
    hour: str
    minutes: str
 #   request: dict
    class Config:
        schema_extra = {
            "example": {
            	"token": "",  
            	"user_id": "",  
                "day": "09",
                "month": "04",    
                "year": "24",
                "hour":"10",
                "minutes": "00"          
            }
        }
    
class doc_conf1(BaseModel):	
    token: str 
    class Config:
        schema_extra = {
            "example": {
                "token": ""   
            }
        }

###
class AppointmentSchema(BaseModel):
    doctor_id: str = Field()
    request = {"id" : int}
###

class DoctorSchema(BaseModel):
    name: str = Field(...)
    surname: str = Field(...)
    father_name: str = Field(...)
    specialty: str = Field(...)
    working_days: Optional[dict] = None
    email: str = Field(...) #should be changed to EmailStr
    login: str = Field(...) 
    password: str = Field(...)
    clinic_name: str =Field(...)
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ankit",
                "surname": "Sarode",
    		"father_name": "Radjendra",
    		"specialty": "Paediatrics",
    		"working_days": {"Monday": "10:00-15:00","Wednesday": "10:00-17:00","Suturday": "12:00-15:00"},
    		"email": "ankit@gmail.com",
    		"login": "login123",
                "password": "12345",
                "clinic_name": "",
            }
        }
        
class ClinicSchema(BaseModel):
    name: str = Field(...)   
    address: str = Field(...)  
    working_days: Optional[dict]
    email: str = Field(...) #should be changed to EmailStr
    phone_number: str = Field(...)  
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Clinic1",
                "address": "Russia, Taganrog",
    		"working_days": {"Monday": "10:00-15:00","Wednesday": "10:00-17:00","Suturday": "12:00-15:00"},
    		"email": "clinic@gmail.com",
		"phone_number": "+78232345328",
            }
        }
   

class UpdateUserModel(BaseModel):
    name: Optional[str]
    login: Optional[str]
    birth: Optional[str]
    #password: Optional[str]
    address: Optional[str]
    main_doctor_id: Optional[str]
    clinic_id: Optional[str]
   # history: Optional[list]

    class Config:
        schema_extra = {
            "example": {
                "address": "India",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }

class UserLoginSchema(BaseModel):
    login: EmailStr = Field(...)
    password: str = Field(...)
    class Config:
        schema_extra = {
            "example": {
                "login": "aditya@gmail.com",
                "password": "12345"
            }
        }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}

