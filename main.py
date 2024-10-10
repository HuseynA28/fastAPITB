from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
from typing import Optional

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Environment variables
LOGIN_URL = os.getenv('LOGIN_URL', 'https://dacs.site/api/auth/login')  # Fallback URL for login
BASE_URL = os.getenv('BASE_URL', 'https://dacs.site')  # Ensure this includes https://
TELEMETRY_URL_TEMPLATE = os.getenv('TELEMETRY_URL_TEMPLATE', "/api/plugins/telemetry/{entityType}/{entityId}/values/timeseries")

# Pydantic models
class AuthCredentials(BaseModel):
    username: str
    password: str

class TelemetryRequest(BaseModel):
    entityType: str
    entityId: str

# Root endpoint
@app.get("/")
async def root():
    return {'message': 'Hi, ThingsBoard 😊'}

# Login endpoint
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

# Latest Telemetry endpoint
@app.get("/latest-telemetry")
async def get_telemetry(
    entityType: str, 
    entityId: str, 
    keys: Optional[str] = Query(None), 
    useStrictDataTypes: Optional[bool] = Query(False),
    token: Optional[str] = None
):
    if not token:
        async with httpx.AsyncClient() as client:
            try:
                auth_response = await client.post(LOGIN_URL, json={
                    "username": USERNAME,
                    "password": PASSWORD
                })
                auth_response.raise_for_status()
                auth_data = auth_response.json()
                token = auth_data.get("token")
                if not token:
                    raise HTTPException(status_code=500, detail="Token not found in authentication response")
            except httpx.RequestError as exc:
                raise HTTPException(status_code=500, detail=f"Authentication failed: {str(exc)}")

    telemetry_url = f"{BASE_URL}{TELEMETRY_URL_TEMPLATE.format(entityType=entityType, entityId=entityId)}"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"keys": keys} if keys else {}
    if useStrictDataTypes:
        params['useStrictDataTypes'] = 'true' if useStrictDataTypes else 'false'

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(telemetry_url, headers=headers, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=exc.response.status_code if exc.response else 500,
                                detail=str(exc))
        except httpx.RequestError as exc:
            raise HTTPException(status_code=500, detail=f"Request failed: {str(exc)}")

        return response.json()
