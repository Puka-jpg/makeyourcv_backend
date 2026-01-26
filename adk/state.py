from typing import Optional, TypedDict


class GraphState(TypedDict, total=False):
    """
    Agent graph state - shared across all agents in a conversation.

    MINIMAL STATE PRINCIPLE:
    - Only store IDs, File Paths, and Status Flags.
    - Large data (Text, JSON, YAML) must be stored in DB or on Disk.
    """

    # Identifiers
    user_id: str
    resume_id: str
    session_id: str

    # File Paths (Source of Truth for Inputs)
    resume_file_path: Optional[str]
    job_description_file_path: Optional[str]

    # Workflow Status Flags (Used for Routing)
    resume_uploaded: bool
    job_description_provided: bool
    tailored_content_ready: bool
    yaml_ready: bool
    rendering_complete: bool

    # Metadata
    current_step: str
    error_message: Optional[str]
