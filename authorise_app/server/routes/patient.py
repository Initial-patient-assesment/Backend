from fastapi import APIRouter, Body, Form, Request
from fastapi.encoders import jsonable_encoder
import json

from app.server.database import (
    add_patient,
    delete_patient,
    retrieve_patient,
    retrieve_patients,
    update_patient,
)
from app.server.models import (
    ErrorResponseModel,
    ResponseModel,
    PatientSchema,
    UpdatePatientModel,
)

router = APIRouter()

#@router.post("/", response_description="Patient data added into the database")
#async def add_patient_data(patient: PatientSchema = Body(...)):
 #   patient = jsonable_encoder(patient)
  #  new_patient = await add_patient(patient)
  #  return ResponseModel(f'{patient} category has been registrated.')
    
@router.post("/", response_description="Patient data added into the database")
async def submit(fullname: str = Form(...), email: str = Form(...),age: int = Form(...)):
   
    schema_extra = {
            
                "fullname": f"{fullname}",
                "email": f"{email}",
                "age": age,
            
          }
   # schema_extraJS = json.dumps(schema_extra)
  
    #patient = jsonable_encoder(schema_extraJS)
    new_patient = await add_patient(schema_extra)
    return ResponseModel("template.html", {"fullname":fullname,"email":email,"age":age})
    
@router.get("/", response_description="Patients retrieved")
async def get_patients():
    patients = await retrieve_patients()
    if patients:
        return ResponseModel(patients, " data retrieved successfully")
    return ResponseModel(patients, "Empty list returned")


@router.get("/{id}", response_description="Patients data retrieved")
async def get_patient_data(id):
    patient = await retrieve_patient(id)
    if patient:
        return ResponseModel(patient, "Patient data retrieved successfully")
    return ErrorResponseModel("An error occurred.", 404, "Patient doesn't exist.")

@router.put("/{id}")
async def update_patient_data(id: str, req: UpdatePatientModel = Body(...)):
    req = {k: v for k, v in req.dict().items() if v is not None}
    updated_patient = await update_patient(id, req)
    if updated_patient:
        return ResponseModel(
            "Patient with ID: {} name update is successful".format(id),
            "Patient name updated successfully",
        )
    return ErrorResponseModel(
        "An error occurred",
        404,
        "There was an error updating the patient data.",
    )

@router.delete("/{id}", response_description="Patient data deleted from the database")
async def delete_patient_data(id: str):
    deleted_patient = await delete_patient(id)
    if deleted_patient:
        return ResponseModel(
            "Patient with ID: {} removed".format(id), "Patient deleted successfully"
        )
    return ErrorResponseModel(
        "An error occurred", 404, "Patient with id {0} doesn't exist".format(id)
    )

