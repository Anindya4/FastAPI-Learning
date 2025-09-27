from fastapi import FastAPI, Path, HTTPException
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