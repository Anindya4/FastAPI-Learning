from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description="ID of the patient", examples= ["P001"])]
    name: Annotated[str, Field(..., description="Name of th patient")]
    city: Annotated[str, Field(..., description="Name of patient's city")]
    age: Annotated[int, Field(...,gt=0, lt=120, description="Age of the patient")]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Gender of the patient")]
    height: Annotated[float, Field(...,gt=0, description="Height of the patient in mts")]
    weight: Annotated[float, Field(...,gt=0, description="Weight of the patient in kgs")]


    # COMPUTING BMI DYNAMICALLY:
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2), 2)
        return bmi
    
    # GENERATING VERDICT BASED ON BMI:
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 < self.bmi < 24.9:
            return "Normal"
        elif 25 < self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]


def load_data():
    with open('patient.json' , 'r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open("patient.json", 'w') as f:
        json.dump(data,f)
    

# Home page:
@app.get('/')
def hello():
    return {"message" : "Welcome Doctor!"}

# About page:
@app.get('/about')
def about():
    return {"message" : "Welcome to PatientX, the next gen patient tracking system"}

# View all patient data:
@app.get('/view')
def view():
    data = load_data()
    return data

# View particular patient data with patient id
@app.get('/patient/{patient_id}')
def view_patient(patient_id : str = Path(..., description="ID of the patient in DB", example="P001")):
    # LOAD THE DATA:
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

# Check by parameters:
@app.get("/sort")
def sort_patients(sort_by : str = Query(...,description="Sort patients by height, weight or bmi"), order : str = Query("asc", description="sort in ascending or decending order")):
    
    valid_field = ["height", "weight", "bmi"]
    
    if sort_by not in valid_field:
        raise HTTPException(status_code=400, detail= f"Invalid field! select from {valid_field}") 
    
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail= "Invalid order select betwenn asc and desc")
    
    data = load_data()
    
    sorted_oder = True if order == "desc" else False
    
    sorted_data = sorted(data.values(), key= lambda x:x.get(sort_by, 0), reverse=sorted_oder)
    
    return sorted_data

@app.post("/create")
def create_patient(patient : Patient):
    
    # load the existing data
    data = load_data()
    
    # check if patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail= "Patient already exists") 
    
    # add the data to the database
    data[patient.id] = patient.model_dump(exclude=['id'])  # model_dump() transform the pydantic object into python dict
    
    # save the data
    save_data(data)
    
    return JSONResponse(status_code=201, content={"message" : "Patient added sucessfully"})

@app.put("/update/{patient_id}")
def update_patient(patient_id : str, req_body : PatientUpdate):
    
    data = load_data()
    
    if patient_id  not in data:
        raise HTTPException(status_code=404, detail="Patient does not exist!")
    
    existing_patient_info = data[patient_id]
    
    updated_patient_info = req_body.model_dump(exclude_unset=True)
    
    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
    
    # updated_patient_info -> pydantic obj -> updated bmi + verdict
    existing_patient_info['id'] = patient_id
    patient_pydantic_obj = Patient(**existing_patient_info)
    
    # Pydantice obj -> dict
    existing_patient_info = patient_pydantic_obj.model_dump(exclude='id')
    
    # Add this dict to data
    data[patient_id] = existing_patient_info
    
    # Save data:
    save_data(data)
    
    return JSONResponse(status_code=200, content={"message": "Patient updated succesfully"})


@app.delete("/delete_patient/{patient_id}")
def delete_patient(patient_id : str):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient does not exists!!")
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={"message":"Patient succesfully deleted!"})