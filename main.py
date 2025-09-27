from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open('patient.json' , 'r') as f:
        data = json.load(f)
    return data

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