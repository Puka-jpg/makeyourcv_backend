import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.adk.tools import ToolContext
import uuid

from adk.tools.state_tools import (
    init_resume_session,
    fetch_resume_data,
    store_tailored_content_json,
    store_tailored_resume_valid_yaml
)

# Test init_resume_session
@pytest.mark.asyncio
async def test_init_resume_session_success():
    user_id = str(uuid.uuid4())
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {"user_id": user_id}
    mock_context.session_id = "session_123"

    with patch("adk.tools.state_tools.sessionmanager") as mock_sessionmanager, \
         patch("adk.tools.state_tools.ResumeService") as MockResumeService:
        
        mock_session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_sessionmanager.session_factory = mock_session_factory
        
        mock_service = MockResumeService.return_value
        mock_service.create_resume = AsyncMock()
        # Mock returned resume object
        mock_resume = MagicMock()
        mock_resume.id = uuid.UUID(resume_id)
        mock_service.create_resume.return_value = mock_resume
        
        # Mock database_session_service imports inside function if we were using them, 
        # but refactored init_resume_session does NOT use StorageSession anymore.
        # It just sets state.
        
        result = await init_resume_session(tool_context=mock_context)
        
        assert result["status"] == "success"
        assert result["resume_id"] == resume_id
        
        # Verify state updates
        assert mock_context.state["resume_id"] == resume_id
        assert mock_context.state["resume_uploaded"] is False
        assert mock_context.state["job_description_provided"] is False

@pytest.mark.asyncio
async def test_init_resume_session_with_existing_file():
    user_id = str(uuid.uuid4())
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {
        "user_id": user_id,
        "resume_file_path": "/path/to/resume.pdf" # Route injected this
    }

    with patch("adk.tools.state_tools.sessionmanager") as mock_sessionmanager, \
         patch("adk.tools.state_tools.ResumeService") as MockResumeService:
        
        mock_session = AsyncMock()
        mock_sessionmanager.session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_service = MockResumeService.return_value
        mock_resume = MagicMock()
        mock_resume.id = uuid.UUID(resume_id)
        mock_service.create_resume = AsyncMock(return_value=mock_resume)
        
        await init_resume_session(tool_context=mock_context)
        
        # Verify resume_uploaded is True because file path exists
        assert mock_context.state["resume_uploaded"] is True


# Test fetch_resume_data
@pytest.mark.asyncio
async def test_fetch_resume_data_success():
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {"resume_id": resume_id}
    
    with patch("adk.tools.state_tools.sessionmanager") as mock_sessionmanager, \
         patch("adk.tools.state_tools.ResumeService") as MockResumeService:
        
        mock_session = AsyncMock()
        mock_sessionmanager.session_factory.return_value.__aenter__.return_value = mock_session
        
        mock_service = MockResumeService.return_value
        mock_service.get_resume = AsyncMock()
        
        # Mock Resume Data
        mock_resume_record = MagicMock()
        mock_resume_record.raw_resume_text = "Resume Text"
        mock_resume_record.job_description = "JD Text"
        mock_resume_record.tailored_content_json = "{}"
        mock_resume_record.tailored_resume_yaml = "YAML"
        
        mock_service.get_resume.return_value = mock_resume_record
        
        result = await fetch_resume_data(mock_context)
        
        assert result["status"] == "success"
        assert result["raw_resume_text"] == "Resume Text"
        assert result["job_description"] == "JD Text"

# Test store tools
@pytest.mark.asyncio
async def test_store_tailored_content():
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {"resume_id": resume_id}
    
    with patch("adk.tools.state_tools.sessionmanager") as mock_sessionmanager, \
         patch("adk.tools.state_tools.ResumeService") as MockResumeService:
        
        mock_session = AsyncMock()
        mock_sessionmanager.session_factory.return_value.__aenter__.return_value = mock_session
        mock_service = MockResumeService.return_value
        mock_service.update_tailored_content = AsyncMock()
        
        await store_tailored_content_json('{"key": "val"}', mock_context)
        
        assert mock_context.state["tailored_content_ready"] is True
        mock_service.update_tailored_content.assert_called_once()
