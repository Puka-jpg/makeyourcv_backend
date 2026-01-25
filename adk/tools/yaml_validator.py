"""
YAML Pre-Validation Helper - Validates YAML structure before MCP calls.

This module provides local validation to catch common errors early,
reducing expensive retry loops from failed MCP render_cv calls.
"""

import re
from typing import Tuple

import yaml

from utils.logger import get_logger

logger = get_logger()


def validate_yaml_structure(yaml_content: str) -> Tuple[bool, str]:
    """
    Validate YAML structure locally before calling render_cv MCP tool.

    This catches common RenderCV validation errors:
    - Invalid YAML syntax
    - Missing required keys
    - Wrong date formats (YYYY-MM not YYYY-MM-DD or "July 2025")
    - Invalid URL formats
    - Incorrect field types (list vs string)

    Args:
        yaml_content: The YAML string to validate

    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if YAML passes all checks
        - error_message: Empty string if valid, detailed error if invalid
    """
    try:
        data = yaml.safe_load(yaml_content)

        if not isinstance(data, dict):
            return False, "YAML must be a dictionary/object at root level"
        if "cv" not in data:
            return False, "Missing required 'cv' key at root level"

        cv = data["cv"]
        if not isinstance(cv, dict):
            return False, "'cv' must be a dictionary"

        required_fields = ["name", "email"]
        for field in required_fields:
            if field not in cv:
                return False, f"Missing required field: cv.{field}"
        if "website" in cv:
            website = cv["website"]
            if not isinstance(website, str):
                return False, "cv.website must be a string"
            if not (website.startswith("http://") or website.startswith("https://")):
                return (
                    False,
                    f"cv.website must include protocol (http:// or https://): '{website}'",
                )

        if "sections" in cv and isinstance(cv["sections"], dict):
            for section_name, section_content in cv["sections"].items():
                if not isinstance(section_content, list):
                    continue

                for idx, item in enumerate(section_content):
                    if not isinstance(item, dict):
                        continue

                    for date_field in ["start_date", "end_date"]:
                        if date_field in item:
                            date_val = item[date_field]
                            if date_val == "present":
                                continue

                            if not isinstance(date_val, str):
                                return (
                                    False,
                                    f"sections.{section_name}[{idx}].{date_field} must be a string",
                                )
                            if not re.match(r"^\d{4}-\d{2}$", date_val):
                                return False, (
                                    f"Invalid date format in sections.{section_name}[{idx}].{date_field}: '{date_val}'. "
                                    f"Expected format: YYYY-MM (e.g., '2025-07' not 'July 2025' or '2025-07-01')"
                                )

                    if "highlights" in item:
                        highlights = item["highlights"]
                        if not isinstance(highlights, list):
                            return False, (
                                f"sections.{section_name}[{idx}].highlights must be a list of strings, "
                                f"got {type(highlights).__name__}"
                            )

                        for h_idx, highlight in enumerate(highlights):
                            if not isinstance(highlight, str):
                                return False, (
                                    f"sections.{section_name}[{idx}].highlights[{h_idx}] must be a string, "
                                    f"got {type(highlight).__name__}"
                                )

        logger.info(
            "YAML pre-validation passed", extra={"yaml_length": len(yaml_content)}
        )
        return True, ""

    except yaml.YAMLError as e:
        error_msg = f"YAML syntax error: {str(e)}"
        logger.warning("YAML pre-validation failed", extra={"error": error_msg})
        return False, error_msg
    except Exception as e:
        error_msg = f"Validation error: {str(e)}"
        logger.error("Unexpected validation error", extra={"error": error_msg})
        return False, error_msg
