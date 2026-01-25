"""Tests for job analysis agent and shared MCP config."""
from unittest.mock import patch

import pytest

from adk.agents.job_analysis_agent import job_analysis_agent
from adk.agents.job_tailoring_agent import job_tailoring_agent


def test_job_analysis_agent_initialization():
    """Test that job_analysis_agent is properly configured."""
    assert job_analysis_agent.name == "job_analysis_agent"
    # Check that tools are configured (may include MCP toolset)
    assert job_analysis_agent.tools is not None


def test_job_tailoring_agent_initialization():
    """Test that job_tailoring_agent is properly configured."""
    assert job_tailoring_agent.name == "job_tailoring_agent"
    assert job_tailoring_agent.tools is not None


def test_mcp_config_shared_instance():
    """Test that get_mcp_toolset returns cached instance."""
    # Reset the cached instance for testing
    from adk import mcp_config
    mcp_config._mcp_toolset = None
    
    with patch.object(mcp_config.settings, 'MCP_MODE', 'disabled'):
        result1 = mcp_config.get_mcp_toolset()
        result2 = mcp_config.get_mcp_toolset()
        
        # Both should return None when disabled
        assert result1 is None
        assert result2 is None


def test_build_tools_with_mcp_disabled():
    """Test build_tools_with_mcp when MCP is disabled."""
    from adk import mcp_config
    mcp_config._mcp_toolset = None
    
    with patch.object(mcp_config.settings, 'MCP_MODE', 'disabled'):
        def dummy_tool():
            pass
        
        tools = mcp_config.build_tools_with_mcp([dummy_tool])
        
        # Should only contain the local tool, not MCP
        assert len(tools) == 1
        assert tools[0] is dummy_tool
