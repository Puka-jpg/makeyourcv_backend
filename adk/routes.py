import base64
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import StorageSession
from google.genai import types
from sqlalchemy import select

from adk.agent import root_agent
from adk.memory import get_session_service
from adk.schemas import ChatResponse
from adk.services.resume_service import ResumeService
from db import sessionmanager
from dependencies.auth_dependencies.auth import get_current_user
from models import User
from utils.logger import get_logger

logger = get_logger()
router = APIRouter(prefix="/adk", tags=["ADK Agent"])

APP_NAME = "agents"


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: str = Form(..., description="User message"),
    file: Optional[UploadFile] = File(None, description="Resume PDF"),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    """
    Entry point for the ADK agent.
    Injects file uploads via 'state_delta' in the user event.
    """
    try:
        session_service = get_session_service()
        user_id = str(current_user.id)
        session_id = f"session_{user_id}"

        # 1. Process File Upload (In-Memory -> Base64)
        resume_b64: Optional[str] = None
        file_name: str = ""

        if file:
            content = await file.read()
            resume_b64 = base64.b64encode(content).decode("utf-8")
            file_name = file.filename or "uploaded_resume.pdf"
            logger.info(
                "Processed file upload",
                extra={"user_id": user_id, "size": len(content)},
            )

        # 2. Ensure Session Exists (Create if missing)
        # Check if session exists
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        if not session:
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id,
            )

   
        current_state = session.state if session.state else {}
        if not current_state.get("resume_id"):
            logger.info("Session missing resume_id. Auto-initializing.")
            if not sessionmanager.session_factory:
                raise RuntimeError("Database not initialized")
            async with sessionmanager.session_factory() as db_session:
                # 1. Create Resume Record
                resume_service = ResumeService(db_session)
                # current_user.id is UUID
                resume = await resume_service.create_resume(user_id=current_user.id)
                resume_id = str(resume.id)

                # 2. Persist to Session Table
                stmt = select(StorageSession).where(StorageSession.id == session.id)
                result = await db_session.execute(stmt)
                storage_session = result.scalars().first()

                if storage_session:
                    new_state = (
                        storage_session.state.copy() if storage_session.state else {}
                    )
                    new_state["resume_id"] = resume_id
                    new_state["resume_uploaded"] = False
                    new_state["job_description_provided"] = False

                    storage_session.state = new_state  # type: ignore
                    await db_session.commit()
                    logger.info(
                        "Auto-persisted resume_id to session",
                        extra={"resume_id": resume_id, "session_id": str(session.id)},
                    )

            if session.state is None:
                session.state = {}
            session.state["resume_id"] = resume_id
            session.state["resume_uploaded"] = False
            session.state["job_description_provided"] = False

        state_delta = {"user_id": user_id}

        logger.info(
            "Injecting user_id into session state.",
            extra={"current_state": session.state},
        )
        if resume_b64:
            state_delta.update(
                {"resume_bytes_b64": resume_b64, "resume_filename": file_name}
            )
            message += f"\n\n[System: User uploaded file '{file_name}'. Check state for 'resume_bytes_b64'.]"

        user_content = types.Content(role="user", parts=[types.Part(text=message)])

        # 4. Prepare Runner
        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
            artifact_service=InMemoryArtifactService(),
        )

        # 5. Run Agent
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

        agent_response_log = (
            final_text[:200] + "..." if len(final_text) > 200 else final_text
        )
        logger.info(
            "Agent Response",
            extra={"user_id": user_id, "response_preview": agent_response_log},
        )

        # 6. Fetch Final State for Response
        session = await session_service.get_session(
            app_name=APP_NAME, user_id=user_id, session_id=session_id
        )

        return ChatResponse(
            response=final_text or "No response generated.",
            state=session.state if session else None,
        )

    except Exception as e:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))
