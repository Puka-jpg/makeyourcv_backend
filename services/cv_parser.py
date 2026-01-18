import json
from io import BytesIO
from typing import Any, Dict

from openai import AsyncOpenAI
from PyPDF2 import PdfReader

from settings import settings
from utils.logger import get_logger

logger = get_logger()


class CVParserService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error("Error extracting text from PDF:", extra={"error": str(e)})
            raise ValueError("Could not extract text from the provided PDF file.")

    async def parse_cv(self, file_content: bytes) -> Dict[str, Any]:
        text_content = self._extract_text_from_pdf(file_content)

        system_prompt = """
        You are an expert resume parser. Your job is to extract structured information from a resume text.
        Return the output in strict JSON format.
        
        The JSON structure must match the following keys exactly:
        - personal_info: { full_name, email, phone, location, linkedin_url, github_url, portfolio_url, website_url, professional_title }
        - education: List of { institution_name, degree, field_of_study, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), is_current (bool), grade, location, description }
        - experiences: List of { job_title, company_name, location, employment_type, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), is_current (bool), description, achievements (list of strings), technologies_used (list of strings) }
        - projects: List of { project_name, description, highlights (list of strings), project_url, github_url, start_date (YYYY-MM-DD), end_date (YYYY-MM-DD), technologies_used (list of strings), is_featured (bool) }
        - skills: List of strings (Extract all technical skills found)
        
        If a date is not explicit, try to infer it or leave null.
        If a field is missing, use null.
        """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_content},
                ],
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            parsed_data = json.loads(content)
            return parsed_data

        except Exception as e:
            logger.error("Error parsing CV with AI:", extra={"error": str(e)})
            raise ValueError("Failed to parse CV: ", {str(e)})
