from jinja2 import Environment, FileSystemLoader

from settings import settings
from utils.logger import get_logger

logger = get_logger()


def generate_gunicorn_systemd_service_file(template_path: str, output_path: str):
    env = Environment(loader=FileSystemLoader(searchpath="./deploying"))
    template = env.get_template(template_path)
    rendered = template.render(**settings.model_dump())

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)
    logger.info("Deployment config generated.")


if __name__ == "__main__":
    generate_gunicorn_systemd_service_file(
        "resume-builder-fastapi.service.j2", "resume-builder-fastapi.service"
    )
