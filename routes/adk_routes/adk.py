import os
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from google.adk.runners import Runner
from google.genai import types

from adk.agent import root_agent
from adk.memory import get_session_service
from adk.schemas import ChatResponse
from dependencies.auth_dependencies.auth import get_current_user
from models import User
from schemas.common import ErrorResponseSchema
from utils.logger import get_logger
from db import get_db

logger = get_logger()


router = APIRouter(
    responses={
        status.HTTP_403_FORBIDDEN: {
            "model": ErrorResponseSchema,
            "description": "Forbidden Response",
        }
    },
)

APP_NAME = "agents"


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: str = Form(..., description="User message"),
    file: Optional[UploadFile] = File(None, description="Resume PDF"),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Entry point for the ADK agent.
    - Saves uploaded file to disk.
    - Injects 'resume_file_path' and 'user_id' via 'state_delta'.
    - Relies on Agent to handle session initialization.
    """
    try:
        session_service = get_db()
        user_id = current_user.id
        session_id = f"session_{user_id}"

        # Ensure session exists in ADK storage
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )
        if not session:
            await session_service.create_session(
                app_name=APP_NAME, user_id=user_id, session_id=session_id
            )
            logger.info(
                "Created new ADK user session", extra={"session_id": session_id}
            )

        # 1. Process File Upload (Save to Disk)
        resume_path: Optional[str] = None
        file_name: str = ""

        if file:
            # Create uploads directory if not exists
            upload_dir = "/home/pukar-kafle/Documents/Resume-Builder/resumes/uploads"
            os.makedirs(upload_dir, exist_ok=True)

            # Generate safe filename
            file_ext = os.path.splitext(file.filename or "")[1]
            if not file_ext:
                file_ext = ".pdf"

            filename = f"{uuid.uuid4()}{file_ext}"
            resume_path = os.path.abspath(os.path.join(upload_dir, filename))

            # Save file
            content = await file.read()
            with open(resume_path, "wb") as f:
                f.write(content)
            if file.filename:
                file_name = file.filename
            logger.info(
                "Processed file upload",
                extra={"user_id": user_id, "path": resume_path, "size": len(content)},
            )

            message += (
                f"\n\n[System: User uploaded file '{file_name}'. Saved to local disk.]"
            )

        # 2. Prepare State Delta (Updates session state before run)

        state_delta: Dict[str, Any] = {"user_id": user_id}

        if resume_path:
            state_delta["resume_file_path"] = resume_path
            state_delta["resume_uploaded"] = True

        logger.info(
            "Injecting data into session state.",
            extra={"state_delta": state_delta},
        )

        user_content = types.Content(role="user", parts=[types.Part(text=message)])

        # 3. Prepare Runner
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        # 4. Run Agent
        final_text = ""
        user_message_log = message[:100] + "..." if len(message) > 100 else message
        logger.info(
            "Agent Request",
            extra={"user_id": user_id, "message_preview": user_message_log},
        )

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=user_content,
            state_delta=state_delta,
        ):
            logger.info(
                "Runner Event",
                extra={
                    "type": str(type(event)),
                    "final": event.is_final_response(),
                    "partial": event.partial,
                },
            )
            if event.content and event.content.parts:
                for p in event.content.parts:
                    logger.info(
                        "Event part",
                        extra={
                            "text": p.text[:50] if p.text else "None",
                            "function_call": p.function_call.name
                            if p.function_call
                            else "None",
                        },
                    )

            if event.is_final_response() and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        final_text += part.text

        # 6. Fetch Final State for Response
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        agent_response_log = (
            final_text[:200] + "..." if len(final_text) > 200 else final_text
        )
        logger.info(
            "Agent Response",
            extra={
                "user_id": user_id,
                "response_preview": agent_response_log,
                "final_state": session.state if session else "None",
            },
        )

        return ChatResponse(
            response=final_text or "No response generated.",
            state=session.state if session else None,
        )

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))
