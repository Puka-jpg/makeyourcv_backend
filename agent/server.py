import logging
import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
# from google.adk.model import Model # Removed invalid import
# from google.adk.user.types import Content, Part # Removed invalid import

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="MakeYour.CV Agent API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Agent Factory ---

from agent.factory import create_agent

# Initialize Agent & Session Service Global
# In a real app, we might pool agents or create per WebSocket if stateful objects required
# But LlmAgent is mostly stateless config, state is in SessionService.
agent_instance = create_agent()
session_service = InMemorySessionService() 
runner = Runner(
    app_name="makeyour-cv-agent",
    agent=agent_instance,
    session_service=session_service
)

# --- WebSocket Endpoint ---

@app.websocket("/ws/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected: {session_id}")
    
    try:
        while True:
            # Receive text/json from client
            raw_data = await websocket.receive_text()
            
            # Simple protocol: {"text": "Hello"} or just "Hello"
            # We'll assume input is user message
            try:
               data = json.loads(raw_data)
               message_text = data.get("text", raw_data)
            except:
               message_text = raw_data
               
            if not message_text.strip():
                continue

            # Run Agent
            # Runner.run_async yields events
            from google.genai.types import Content, Part
            user_msg = Content(role="user", parts=[Part.from_text(text=message_text)]) 
            
            async for event in runner.run_async(
                session_id=session_id,
                user_id=session_id, # Use session_id as temp user_id for anonymous chat
                new_message=user_msg
            ):
                # We need to serialize events to send back to UI
                # Event typically has types like 'ModelResponse', 'ToolCall', etc.
                # adk events might not be directly JSON serializable, we extract what we need.
                
                # ADK Event structure varies, let's inspect or assume ModelResponse
                # For basic chat, we want the MODEL's text output.
                
                # Using a simplistic serialization for now
                response_payload = {
                   "type": event.__class__.__name__,
                   "data": str(event) 
                }
                
                # If it's the final model response, we usually want the text
                if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                     # Extract text parts
                     text_content = ""
                     for p in event.content.parts:
                         if hasattr(p, 'text'):
                            text_content += p.text
                     response_payload["text"] = text_content

                await websocket.send_json(response_payload)
            
            # Signal turn end?
            await websocket.send_json({"type": "TurnComplete"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.exception(f"Error in websocket loop: {e}")
        await websocket.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("agent.server:app", host="0.0.0.0", port=port, reload=True)
