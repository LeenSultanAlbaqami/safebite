"""
SafeBite Main Application
Entry point for the FastAPI server. Configures CORS and registers all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, profile, ai_assistant, scanner, emergency

app = FastAPI(title="SafeBite API — Food Safety Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(ai_assistant.router)
app.include_router(scanner.router)
app.include_router(emergency.router)


@app.get("/")
async def root():
    """Health check endpoint to verify the server is running."""
    return {"status": "SafeBite API is live and healthy 🛡️"}