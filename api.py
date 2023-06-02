from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from models import EmailPayload, EmailOptions
from typing import List

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000","http://0.0.0.0:8000"],  # Adjust this based on your requirements
    allow_methods=["*"],
    allow_headers=["*"],
)

class EmailPayload(BaseModel):
    subject: str
    email_list: List[str]
    body: str

class EmailOptions(BaseModel):
    selected_profiles: List[str]
    browser_language: str
    send_limit_per_profile: int
    loop_profile: int

@app.post("/api/v1/emailcomposer")
async def send_email(payload: EmailPayload, options: EmailOptions):
    # Print the received payload and options
    if not options.selected_profiles:
        return {"error": "Mozilla profile name is required"}
    if not payload.subject:
        return {"error": "Email subject is required"}
    if not payload.email_list:
        return {"error": "Email list is required"}
    if not payload.body:
        return {"error": "Email body is required"}
    
    print("*"*50,"api.py","*"*50)
    
    print("Received Payload:", payload,"\n")
    
    print("Received Options:", options,"\n")
    
    print("*"*50,"api.py","*"*50)

    # Process the data and send the response

    # Return a response indicating success or failure
    return {"message": "Email sent successfully"}
