# backend/main.py

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

# Initialize FastAPI app
app = FastAPI(
    title="CognitoSphere Backend",
    description="API for the Hyper-Personalized Cognitive Augmentation System",
    version="0.1.0",
)

# Serve the static HTML file for the landing page (Frontend will replace this later)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CognitoSphere - Cognitive Augmentation System</title>
        <style>
            body { font-family: sans-serif; text-align: center; margin-top: 50px; }
            .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }
            h1 { color: #333; }
            p { color: #666; }
            .button {
                background-color: #4CAF50; /* Green */
                border: none;
                color: white;
                padding: 15px 32px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin-top: 20px;
                cursor: pointer;
                border-radius: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Welcome to CognitoSphere!</h1>
            <p>Your Hyper-Personalized Cognitive Augmentation System.</p>
            <p>This is the backend API. The frontend will be built here soon!</p>
            <button class="button">Login (Coming Soon!)</button>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# A simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "CognitoSphere backend is running!"}