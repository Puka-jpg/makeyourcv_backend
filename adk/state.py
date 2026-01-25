from typing import Any, Dict, List, Optional, TypedDict


class GraphState(TypedDict, total=False):
    """Agent graph state - shared across all agents in a conversation."""

    # Conversation
    messages: List[Dict[str, Any]]
    current_step: str
    user_id: str
    user_name: Optional[str]

    # Source data
    raw_resume_text: Optional[str]  
    raw_job_description: Optional[str]  
    resume_file_path: Optional[str]  

    # RenderCV Metadata
    rendercv_schema_json: Optional[str]  
    rendercv_templates: Optional[List[str]]  

    # Final output
    tailored_resume_valid_yaml: Optional[str]  
