from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PatientSchema(BaseModel):
    fullname: str = Field(...)
    email: str = Field(...) #should be changed to EmailStr
    age: int = Field(..., gt=0)

    class Config:
        schema_extra = {
            "example": {
                "fullname": "John Doe",
                "email": "jdoe@x.edu.ng",
                "age": 18,
            }
        }


class UpdatePatientModel(BaseModel):
    fullname: Optional[str]
    email: Optional[EmailStr]
    age: Optional[int]


    class Config:
        schema_extra = {
            "example": {
                "fullname": "Alex Doe",
                "email": "jdoe@x.edu.ng",
                "age": 10,
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
