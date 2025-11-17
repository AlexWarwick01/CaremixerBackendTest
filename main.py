# This is the main FastAPI application file

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

# Import routers from other modules
from timeline import router as timeline_router
from external_api import router as external_data_router
from chat import router as chat_router


# Create FastAPI app
app = FastAPI(title="CareMixer Technical Assessment API",
              description="Basic Rest API with Timeline, External Data and Chat Features",
              version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Each Router handles a specific task
# tags are used for grouping in the automatic docs
app.include_router(timeline_router, prefix="/timeline", tags=["Timeline"])
app.include_router(external_data_router, prefix="/external_data", tags=["External Data"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

@app.get("/chat-ui", response_class=HTMLResponse)
async def chat_ui():
    # Serve the chat HTML interface
    chat_html_path = os.path.join(os.path.dirname(__file__), "chat.html")
    with open(chat_html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/")
async def root():
    # Root endpoint - Will just give some basic info about the endpoints
    return {
        "message": "Welcome to the CareMixer Technical Assessment API!",
        "endpoints": {
            "/timeline": "Get timeline data",
            "/external_data": "Fetch external data",
            "/chat_get": "Get chat messages (GET)",
            "/chat_post": "Send chat messages (POST)"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) # Run the app with auto-reload for development