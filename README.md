# Resume Builder Backend 🚀

A powerful and scalable backend for a modern Resume Builder application, built with **FastAPI** and **Python**. This API provides comprehensive endpoints for managing user profiles, parsing CVs, and handling various resume sections like education, experience, and skills.

## ✨ Features

- **📄 CV Parsing**: intelligent parsing of existing resumes (PDF) to extract structured data.
- **🔐 Secure Authentication**: Robust JWT-based authentication with Argon2 password hashing.
- **👤 User Management**: Full control over user accounts and profiles.
- **🧩 Modular Resume Sections**: granular management of:
    - Personal Information
    - Professional Summaries
    - Education History
    - Work Experience
    - Projects
    - Technical Skills
    - Publications & Certifications
    - Custom Sections
- **🚀 High Performance**: Built on FastAPI for speed and concurrency.
- **🛡️ Type Safe**: Fully typed codebase using Pydantic and Mypy.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **Language**: Python 3.12+
- **Database**: PostgreSQL (AsyncPG + SQLAlchemy 2.0)
- **Migrations**: Alembic
- **Dependency Management**: [uv](https://github.com/astral-sh/uv)
- **Task Runner**: [Just](https://github.com/casey/just)
- **Linting & Formatting**: Ruff
- **AI Integration**: OpenAI (for parsing capabilities)

## 🚀 Getting Started

### Prerequisites

- **Python 3.12** or higher
- **[uv](https://github.com/astral-sh/uv)** (Fast Python package installer)
- **[Just](https://github.com/casey/just)** (Command runner)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Puka-jpg/makeyourcv_backend.git
   cd makeyourcv_backend
   ```

2. **Install Dependencies**
   ```bash
   just install
   ```

3. **Environment Setup**
   Copy the example environment file and configure your variables (Database URL, OpenAI Key, Secret Keys, etc.):
   ```bash
   cp .env.example .env
   ```

### 🏃‍♂️ Running the Server

Start the development server with hot-reloading:
```bash
just dev
```
The API will be available at `http://127.0.0.1:8080`.

### 🧪 Database Migrations

Apply database migrations to set up your schema:
```bash
just migrate
```

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation:

- **Swagger UI**: [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)
- **ReDoc**: [http://127.0.0.1:8080/redoc](http://127.0.0.1:8080/redoc)

## 🛠️ Development Commands

We use `just` to manage development tasks. Run `just` or `just --list` to see all available commands:

| Command | Description |
|---|---|
| `just install` | Install all dependencies |
| `just dev` | Start the dev server |
| `just format` | Format code with Ruff |
| `just lint` | Run code linting |
| `just mypy` | Run type checking |
| `just test` | Run tests with Pytest |
| `just migrate` | Apply Alembic migrations |

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request