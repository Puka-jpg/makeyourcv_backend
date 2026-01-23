from pathlib import Path
from typing import Any, Dict

from ruamel.yaml import YAML

# We assume rendercv is installed as a library (though it's main interface is CLI, we can import data_model)
# For simplicity and robustness, we might shell out to the CLI, or use the python API if stable.
# Let's try to shell out for now as it isolates the process, OR usage of the library if simple.
# Since I cannot easily explore the library API in REPL, I will assume a subprocess call to `rendercv render` is safest.
from tools.resume_tools import get_user_profile_tool
from utils.logger import get_logger

logger = get_logger()
yaml = YAML()


async def generate_resume_pdf(user_id: str, theme: str = "classic") -> str:
    """
    Generates a PDF resume for the given user using RenderCV.
    Returns the path to the generated PDF.

    Args:
        user_id: The UUID of the user.
        theme: The RenderCV theme to use (classic, moderncv, sb2nov, etc.)
    """
    try:
        # 1. Fetch Profile
        try:
            profile = await get_user_profile_tool(user_id)
        except Exception as e:
            # In case the async loop sharing is an issue, we might need to fix `resume_tools` to reusing session differently
            # But since `get_user_profile_tool` creates its own session gen, it should be fine if awaited.
            raise e

        if not profile:
            return "Error: User profile not found."

        # 2. Map to RenderCV Data Model
        cv_data = _map_to_rendercv_model(profile, theme)

        # 3. Write to YAML
        work_dir = Path(f"/tmp/rendercv_gen_{user_id}")
        work_dir.mkdir(parents=True, exist_ok=True)

        yaml_path = work_dir / "cv.yaml"
        with open(yaml_path, "w") as f:
            yaml.dump(cv_data, f)

        # 4. Run RenderCV
        # rendercv render <file>
        output_dir = work_dir / "output"
        cmd = f"rendercv render {yaml_path} --output-folder_name {output_dir}"

        logger.info("Running RenderCV: %s", cmd)

        # We run this synchronously or in threadpool since it's CPU bound/IO
        import subprocess

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error("RenderCV Failed: %s", result.stderr)
            return f"Error rendering CV: {result.stderr}"

        # 5. Find PDF
        # Result normally is inside output_dir based on name
        # We search specifically
        pdfs = list(output_dir.glob("*.pdf"))
        if not pdfs:
            return "Error: PDF not generated."

        # Move to a stable public or storage location?
        # For now return the local path
        return str(pdfs[0])

    except Exception as e:
        logger.exception("Error in generate_resume_pdf")
        return f"Error: {str(e)}"


def _map_to_rendercv_model(p: Dict[str, Any], theme: str) -> Dict[str, Any]:
    """Maps the makeyour.cv profile dict to RenderCV YAML structure."""

    # Extract sections
    pi = p.get("personal_info") or {}
    edu = p.get("education") or []
    exp = p.get("experiences") or []
    pro = p.get("projects") or []
    ski = p.get("skills") or []

    # Construct base
    cv_model = {
        "cv": {
            "name": pi.get("full_name") or "Your Name",
            "location": pi.get("location"),
            "email": pi.get("email"),
            "phone": pi.get("phone"),
            "website": pi.get("website_url"),
            "social_networks": [],
            "sections": {
                # We need to explicitly order sections or just provide them
                # RenderCV schema usually expects specific keys like 'education', 'experience_and_education' etc or generic
            },
        },
        "design": {"theme": theme},
    }

    # Socials
    if pi.get("linkedin_url"):
        cv_model["cv"]["social_networks"].append(
            {"network": "LinkedIn", "username": pi["linkedin_url"]}
        )  # Simplified
    if pi.get("github_url"):
        cv_model["cv"]["social_networks"].append(
            {"network": "GitHub", "username": pi["github_url"]}
        )

    # Sections - Populating the specific list fields
    # Note: RenderCV 2.x structure might vary, we assume standard fields

    # Education
    cv_edu = []
    for e in edu:
        entry = {
            "institution": e.get("institution_name"),
            "area": e.get("degree"),  # Mapping degree to area/degree
            "start_date": e.get("start_date"),
            "end_date": e.get("end_date") or "Present",
            "highlights": [e.get("description")] if e.get("description") else [],
        }
        cv_edu.append(entry)

    if cv_edu:
        cv_model["cv"]["sections"]["education"] = cv_edu

    # Experience
    cv_exp = []
    for e in exp:
        entry = {
            "company": e.get("company_name"),
            "position": e.get("job_title"),
            "start_date": e.get("start_date"),
            "end_date": e.get("end_date") or "Present",
            "location": "",  # data might not have it
            "highlights": e.get("achievements")
            or ([e.get("description")] if e.get("description") else []),
        }
        cv_exp.append(entry)

    if cv_exp:
        cv_model["cv"]["sections"]["experience"] = cv_exp

    # Projects
    cv_proj = []
    for pr in pro:
        entry = {
            "name": pr.get("project_name"),
            "date": pr.get("start_date"),  # or range
            "highlights": ([pr.get("description")] if pr.get("description") else []),
            "link": pr.get("project_url"),
        }
        cv_proj.append(entry)

    if cv_proj:
        cv_model["cv"]["sections"]["projects"] = cv_proj

    # Skills
    # RenderCV typically wants a list of { label: "Languages", details: "Python, C++" }
    cv_skills = []
    for s in ski:
        entry = {
            "label": s.get("category"),
            "details": ", ".join(s.get("skills") or []),
        }
        cv_skills.append(entry)

    if cv_skills:
        cv_model["cv"]["sections"]["skills"] = cv_skills

    return cv_model
