from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserSchema(BaseModel):
    name: str = Field(...)
    login: str = Field(...) #should be changed to EmailStr
    password: str = Field(...)

    class Config:
        schema_extra = {
            "example": {
                "name": "Aditya",
                "login": "aditya@gmail.com",
                "password": "12345",
            }
        }


class UpdateUserModel(BaseModel):
    name: Optional[str]
    login: Optional[str]
    #password: Optional[EmailStr]
    password: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "Aditya",
                "login": "jdoe@x.edu.ng",
                "password": "1234",
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}

