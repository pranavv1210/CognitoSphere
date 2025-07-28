# backend/main.py

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount # NEW IMPORT
from starlette.middleware import Middleware # NEW IMPORT for correct middleware order on root app
# Temporarily remove or comment out the database import
# from database import mongo_manager # COMMENT THIS OUT OR REMOVE IT

from dotenv import load_dotenv
import os
import httpx
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
import time
import fastapi
import starlette
import base64
import json

# Load environment variables from .env file FIRST and FOREMOST
load_dotenv()

# --- Configuration ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY")

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    raise ValueError("GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in the .env file")
if not APP_SECRET_KEY:
    raise ValueError("APP_SECRET_KEY must be set in the .env file for session security")

# --- Google OAuth 2.0 Endpoints (Manual Configuration) ---
AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"
REDIRECT_URI = "http://127.0.0.1:8000/api/auth/callback"


# --- Pydantic Models for User Data (used for session/API response, NOT DB storage here) ---
class User(BaseModel):
    id: str # Use 'id' directly. For now, this will map to 'google_id' from session.
    google_id: str
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class UserInDB(User): # This model isn't directly used if DB is disabled
    created_at: Optional[int] = None
    last_login_at: Optional[int] = None


# Initialize FastAPI app
# Moved middleware to a list for the main FastAPI app. This helps with StaticFiles routing.
# The order of middleware matters! CORS first, then Session.
middleware = [
    Middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]),
    Middleware(SessionMiddleware, secret_key=APP_SECRET_KEY, max_age=3600),
]

app = FastAPI(
    title="CognitoSphere Backend",
    description="API for the Hyper-Personalized Cognitive Augmentation System",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    middleware=middleware # Pass middleware directly
)

# --- Application Event Handlers (Startup/Shutdown) ---

@app.on_event("startup")
async def startup_event():
    print("Application startup event triggered.")
    print(f"FastAPI Version: {fastapi.__version__}")
    print(f"Starlette Version: {starlette.__version__}")

    # await mongo_manager.connect_to_db() # COMMENT THIS OUT
    print("MongoDB connection temporarily disabled.")

    print("Google OAuth client configured manually.")


@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown event triggered.")
    # await mongo_manager.close_db_connection() # COMMENT THIS OUT
    print("MongoDB connection closure skipped.")


# --- API Endpoints ---

# Health check endpoint
@app.get("/api/health", tags=["Monitoring"])
async def health_check():
    return {"status": "ok", "message": "CognitoSphere backend is running!"}

# Google Login Endpoint (Manual OAuth Step 1: Redirect to Google)
@app.get("/api/auth/login", tags=["Authentication"])
async def login_google(request: Request):
    state = os.urandom(16).hex()
    request.session['oauth_state'] = state

    auth_url = (
        f"{AUTHORIZATION_URL}?"
        f"response_type=code&"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"scope=openid%20email%20profile&" # URL-encoded scopes
        f"state={state}&"
        f"access_type=offline&" # To potentially get a refresh token later
        f"prompt=consent" # To always show consent screen initially
    )
    return RedirectResponse(auth_url)

# Google OAuth Callback Endpoint (Manual OAuth Step 2: Handle redirect from Google)
@app.get("/api/auth/callback", tags=["Authentication"])
async def auth_callback(request: Request):
    code = request.query_params.get("code")
    state_param = request.query_params.get("state")
    session_state = request.session.pop('oauth_state', None)

    if not code:
        raise HTTPException(status_code=400, detail="Authorization code not provided.")
    if not state_param or state_param != session_state:
        raise HTTPException(status_code=400, detail="CSRF Warning! State mismatch.")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            TOKEN_URL,
            data={
                "code": code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        token_response.raise_for_status()
        token_data = token_response.json()

    print("\n--- Manual Token Exchange Result ---")
    print(f"Full Token Data: {token_data}")
    if 'id_token' in token_data:
        print(f"ID Token Found: {token_data['id_token'][:50]}...")
        try:
            id_token_payload_b64 = token_data['id_token'].split('.')[1]
            id_token_payload_b64 += '=' * (-len(id_token_payload_b64) % 4)
            decoded_payload = json.loads(base64.urlsafe_b64decode(id_token_payload_b64))
            print(f"Decoded ID Token Payload: {json.dumps(decoded_payload, indent=2)}")

            if decoded_payload.get('iss') != "https://accounts.google.com":
                raise HTTPException(status_code=401, detail="Invalid ID Token Issuer.")
            if decoded_payload.get('aud') != GOOGLE_CLIENT_ID:
                raise HTTPException(status_code=401, detail="Invalid ID Token Audience.")
            if time.time() > decoded_payload.get('exp', 0):
                raise HTTPException(status_code=401, detail="ID Token Expired.")

            user_info_from_google = decoded_payload
            user_data_for_session = {
                'id': user_info_from_google['sub'],
                'google_id': user_info_from_google['sub'],
                'email': user_info_from_google['email'],
                'name': user_info_from_google.get('name', user_info_from_google['email']),
                'picture': user_info_from_google.get('picture')
            }
            request.session['user'] = user_data_for_session

        except Exception as decode_e:
            raise HTTPException(status_code=401, detail=f"Authentication failed: ID Token decode/validation error: {decode_e}")
    else:
        raise HTTPException(status_code=401, detail="Authentication failed: ID Token not found in response.")

    return RedirectResponse(url="/dashboard")

# Endpoint to get current user info (protected)
@app.get("/api/user/me", tags=["User"], response_model=User)
async def get_current_user(request: Request):
    user_session_data = request.session.get('user')
    if not user_session_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return User(**user_session_data)

# Endpoint to log out
@app.post("/api/auth/logout", tags=["Authentication"])
async def logout(request: Request):
    request.session.clear()
    return {"message": "Logged out successfully"}

# --- Serve React Frontend Static Files ---
# This mounts the 'dist' directory as the default static file server.
# The 'html=True' ensures that if a specific file or API route isn't found,
# it serves index.html, allowing the React router to handle client-side routes.
app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="static")