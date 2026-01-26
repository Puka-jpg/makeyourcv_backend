import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from google.adk.tools import ToolContext
import uuid

# Import the tool directly
from adk.tools.parser_tool import extract_resume_text_tool

@pytest.mark.asyncio
async def test_extract_resume_text_tool_success():
    # Setup
    resume_id = str(uuid.uuid4())
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {
        "resume_file_path": "/tmp/resume.pdf",
        "resume_id": resume_id
    }

    # Patches
    # Note: We must patch where the objects are IMPORTED or USED.
    # Since imports are inside the function, we patch the modules.
    
    with patch("builtins.open", mock_open(read_data=b"PDF CONTENT")), \
         patch("adk.tools.parser_tool.CVParserService") as MockParserService, \
         patch("db.sessionmanager") as mock_sessionmanager, \
         patch("adk.services.resume_service.ResumeService") as MockResumeService:
        
        # Configure Mocks
        mock_parser = MockParserService.return_value
        mock_parser.extract_text_from_pdf.return_value = "Extracted Text"
        
        # Mock session context manager
        mock_session = AsyncMock()
        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__.return_value = mock_session
        mock_sessionmanager.session_factory = mock_session_factory
        
        # Mock Resume Service
        mock_resume_service = MockResumeService.return_value
        mock_resume_service.update_raw_text = AsyncMock()
        
        # Execute
        result = await extract_resume_text_tool(mock_context)
        
        # Assertions
        assert "Resume text extracted and stored" in result
        assert mock_context.state["resume_uploaded"] is True
        
        mock_parser.extract_text_from_pdf.assert_called_once_with(b"PDF CONTENT")
        mock_resume_service.update_raw_text.assert_called_once()
        
        # Verify arguments passed to update_raw_text
        call_args = mock_resume_service.update_raw_text.call_args
        assert str(call_args[0][0]) == resume_id
        assert call_args[0][1] == "Extracted Text"

@pytest.mark.asyncio
async def test_extract_resume_text_tool_missing_file():
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {
        "resume_id": "123"
        # Missing resume_file_path
    }
    
    with pytest.raises(ValueError, match="No resume file found"):
        await extract_resume_text_tool(mock_context)

@pytest.mark.asyncio
async def test_extract_resume_text_tool_missing_id():
    mock_context = MagicMock(spec=ToolContext)
    mock_context.state = {
        "resume_file_path": "/tmp/file.pdf"
        # Missing resume_id
    }
    
    with pytest.raises(ValueError, match="Session not initialized"):
        await extract_resume_text_tool(mock_context)
