from unittest.mock import AsyncMock, mock_open, patch

import pytest

from adk.agents.parser_agent import parser_agent
from adk.tools.parser_tool import parse_cv_tool


@pytest.mark.parametrize("anyio_backend", ["asyncio"])
@pytest.mark.anyio
async def test_parser_tool(anyio_backend):
    # Mock CVParserService
    with patch("adk.tools.parser_tool.CVParserService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.parse_cv = AsyncMock(return_value={"personal_info": {"name": "Test"}})
        
        # Mock ToolContext with state dict
        mock_tool_context = AsyncMock()
        mock_tool_context.state = {}
        
        # Mock open
        with patch("builtins.open", new_callable=mock_open, read_data=b"test pdf"):
            result = await parse_cv_tool("/fake/path.pdf", mock_tool_context)
            
        assert result == {"personal_info": {"name": "Test"}}
        mock_instance.parse_cv.assert_called_once()
        # Verify state was updated
        assert mock_tool_context.state["resume_data"] == {"personal_info": {"name": "Test"}}

def test_parser_agent_initialization():
    assert parser_agent.name == "parser_agent"
    # Check if parse_cv_tool is in tools. 
    # The tools list might contain ToolWrapper objects or whatever ADK does, 
    # but usually it's the function or Tool object.
    # We just check length for now.
    assert len(parser_agent.tools) >= 1
    
    # Check for parse_cv_tool
    found_parser_tool = False
    for t in parser_agent.tools:
        name = getattr(t, "__name__", getattr(t, "name", str(t)))
        if "parse_cv_tool" in name:
            found_parser_tool = True
            break
            
    assert found_parser_tool
