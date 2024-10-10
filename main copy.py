# main.py

from fastapi import FastAPI, HTTPException, Depends

from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from typing import Optional


load_dotenv()
app = FastAPI()
LOGIN_URL = os.getenv('LOGIN_URL', 'https://thingsboard.bda-itnovum.com/api/auth/login')
TELEMETRY_URL_TEMPLATE = os.getenv('TELEMETRY_URL_TEMPLATE', 'https://thingsboard.bda-itnovum.com/api/plugins/telemetry/{DEVICE}/{DEVICE_ID}/values/timeseries')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

class AuthCredentials(BaseModel):
    username: str
    password: str

class TelemetryRequest(BaseModel):
    device: str
    device_id: str

@app.get("/")
async def root():
    return {'message': 'Hi, ThingsBoard 😊'}



@app.post("/login")
async def login(credentials: AuthCredentials):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(LOGIN_URL, json={
                "username": credentials.username,
                "password": credentials.password
            })
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.response.status_code if exc.response else 500,
                                detail=str(exc)) from exc

        data = response.json()
        token = data.get("token")
        if not token:
            raise HTTPException(status_code=500, detail="Token not found in response")
        
        return {"token": token}

@app.get("/telemetry")
async def get_telemetry(device: str, device_id: str, token: Optional[str] = None):
    """
    Retrieves telemetry data from the external API using the provided token.
    """
    if not token:
        # If token is not provided, attempt to authenticate using environment credentials
        async with httpx.AsyncClient() as client:
            try:
                auth_response = await client.post(LOGIN_URL, json={
                    "username": USERNAME,
                    "password": PASSWORD
                })
                auth_response.raise_for_status()
            except httpx.HTTPError as exc:
                raise HTTPException(status_code=exc.response.status_code if exc.response else 500,
                                    detail=str(exc)) from exc

            auth_data = auth_response.json()
            token = auth_data.get("token")
            if not token:
                raise HTTPException(status_code=500, detail="Token not found in authentication response")

    telemetry_url = TELEMETRY_URL_TEMPLATE.format(DEVICE=device, DEVICE_ID=device_id)
    headers = {
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(telemetry_url, headers=headers)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.response.status_code if exc.response else 500,
                                detail=str(exc)) from exc
        
        return response.json()
