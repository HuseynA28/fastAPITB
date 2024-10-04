# main.py

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from typing import Optional

# Load environment variables
load_dotenv()

app = FastAPI()

# Configuration from environment variables
LOGIN_URL = os.getenv('LOGIN_URL', 'https://thingsboard.bda-itnovum.com/api/auth/login')
TELEMETRY_URL_TEMPLATE = os.getenv('TELEMETRY_URL_TEMPLATE', 'https://thingsboard.bda-itnovum.com/api/plugins/telemetry/{DEVICE}/{DEVICE_ID}/values/timeseries')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Pydantic models for request bodies
class AuthCredentials(BaseModel):
    username: str
    password: str

async def authenticate(credentials: Optional[AuthCredentials] = None) -> str:
    """
    Authenticates with the external API and returns a token.
    If credentials are not provided, uses the default ones from the environment.
    """
    auth_data = {}
    if credentials:
        auth_data = {
            "username": credentials.username,
            "password": credentials.password
        }
    else:
        auth_data = {
            "username": USERNAME,
            "password": PASSWORD
        }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(LOGIN_URL, json=auth_data)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=exc.response.status_code if exc.response else 500,
                detail=f"Authentication failed: {str(exc)}"
            ) from exc

        data = response.json()
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=500, detail="Token not found in authentication response")
        
        return token

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/login")
async def login(credentials: AuthCredentials):
    """
    Authenticates with the external API and retrieves a token.
    """
    token = await authenticate(credentials)
    return {"token": token}

@app.get("/telemetry")
async def get_telemetry(device: str, device_id: str, token: Optional[str] = Depends(authenticate)):
    """
    Retrieves telemetry data from the external API using the provided token.
    """
    telemetry_url = TELEMETRY_URL_TEMPLATE.format(DEVICE=device, DEVICE_ID=device_id)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(telemetry_url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(
                status_code=exc.response.status_code if exc.response else 500,
                detail=f"Telemetry fetch failed: {str(exc)}"
            ) from exc
        
        return response.json()
