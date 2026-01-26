import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from google.adk.tools import ToolContext
import uuid

# Import the tool directly
from adk.tools.state_tools import store_job_description

@pytest.mark.asyncio
async def test_store_job_description_success():
    # Setup
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {
        "resume_id": resume_id,
        "job_description_provided": False
    }
    job_desc = "Software Engineer at Google"

    # Patches
    # We patch adk.tools.state_tools imports
    with patch("adk.tools.state_tools.sessionmanager") as mock_sessionmanager, \
         patch("adk.tools.state_tools.ResumeService") as MockResumeService:
        
        # Mock session context manager
        mock_session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_sessionmanager.session_factory = mock_session_factory
        
        # Mock Resume Service
        mock_resume_service = MockResumeService.return_value
        mock_resume_service.update_job_description = AsyncMock()
        
        # Execute
        result = await store_job_description(job_desc, mock_context)
        
        # Assertions
        assert "Job description stored in DB" in result
        assert mock_context.state["job_description_provided"] is True
        
        # Verify DB interaction
        mock_resume_service.update_job_description.assert_called_once()
        call_args = mock_resume_service.update_job_description.call_args
        assert str(call_args[0][0]) == resume_id
        assert call_args[0][1] == job_desc

@pytest.mark.asyncio
async def test_store_job_description_missing_id():
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {}
    job_desc = "Software Engineer"
    
    result = await store_job_description(job_desc, mock_context)
    
    assert "Error: No resume_id in state" in result
    assert "job_description_provided" not in mock_context.state or not mock_context.state["job_description_provided"]
