from fastapi import FastAPI
from typing import Annotated, Literal
from pydantic import Field, computed_field, BaseModel
import pickle
from fastapi.responses import JSONResponse
import pandas as pd

# Load the data:
with open('model.pkl', 'rb') as f:
    model = pickle.load(f)


app = FastAPI()


# City tier lists:
tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]



# Pydantic model for data validation:
class UserInput(BaseModel):
    
    age: Annotated[int, Field(..., gt=0,lt=120, description="Age of the user")]
    weight: Annotated[float,  Field(..., gt=0, description="Weight of the user in KG")]
    height: Annotated[float,  Field(..., gt=0,lt=3, description="Height of the user in Mt")]
    income_lpa: Annotated[float , Field(..., gt=0, description="Anuual income of the user in LPA")]
    smoker: Annotated[bool, Field(..., description="Does the user smoke")]
    city: Annotated[str, Field(..., description="Name of the city user resides")]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job'], Field(..., description="Occupation of the user")]
    
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round((self.weight)/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 18:
            return "young"
        elif 18 < self.age <40:
            return "adult"
        elif 40 < self.age < 60:
            return "middel_aged"
        return "senior"
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.bmi and self.weight > 30:
            return "high"
        elif self.weight or self.bmi > 27:
            return "medium"
        return "low"
        
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        return 3
    

@app.post("/predict")
def predict_premium(data: UserInput):
    
    input_df = pd.DataFrame([{
        "bmi" : data.bmi,
        "age_group" : data.age_group,
        "lifestyle_risk" : data.lifestyle_risk,
        "city_tier" : data.city_tier,
        "income_lpa" : data.income_lpa,
        "occupation" : data.occupation
    }])
    
    prediction = model.predict(input_df)[0]
    
    return JSONResponse(status_code=200, content={"Predicted catagory" : prediction})