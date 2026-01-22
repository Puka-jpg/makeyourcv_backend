# Architecture Overview

RenderCV handles the conversion of a YAML input file into a high-quality PDF. The process involves three main stages: Validation, Data Processing, and Rendering.

```mermaid
graph LR
    YAML[YAML Input] --> CLI
    CLI --> Schema[Validation (Pydantic)]
    Schema --> Model[Data Model]
    Model --> Renderer[Renderer (Jinja2 + Typst)]
    Renderer --> Typst[Typst Source]
    Typst --> PDF[Final PDF]
```

## 1. Directory Structure

The source code is located in `src/rendercv` and is organized as follows:

- **`cli/`**: Handles command-line arguments and user interaction.
    - `app.py`: Main Typer application.
    - `*_command.py`: Implementations of specific commands (`new`, `render`).
- **`schema/`**: Defines the data structure and validation logic.
    - `models/`: Pydantic models for `cv`, `design`, and `locale`.
    - `models/cv/`: CV-specific models (Experience, Education).
    - `models/design/`: Design options and theme definitions.
- **`renderer/`**: Handles the generation of output files.
    - Uses Jinja2 templates (localized in theme folders) to generate Typst code.
    - Calls the Typst CLI (via `typst` library) to compile the PDF.
- **`themes/`**: (Built-in themes) Contains the Jinja2 templates for standard themes like `classic`.

## 2. Key Components

### CLI (`src/rendercv/cli`)
The CLI uses **Typer** to define commands. It parses arguments, handles errors, and invokes the rendering logic.

### Schema (`src/rendercv/schema`)
Data validation is the core of RenderCV. We use **Pydantic** validation models to ensure:
- Dates are in the correct format.
- URLs are valid.
- Required fields are present.
- Design options match the allowed values.

The `RenderCVModel` is the root model that validates the entire YAML file.

### Renderer (`src/rendercv/renderer`)
The renderer takes the validated `RenderCVModel` and applies it to **Jinja2** templates.
- **Templating**: We use Jinja2 to generate `.typ` (Typst) files. This allows powerful logic (loops, conditionals) within the template.
- **Compilation**: The generated Typst file is compiled into a PDF.

## 3. Extension Points

- **New Themes**: Added by creating a new folder in `src/rendercv/themes` or locally.
- **New Entry Types**: Added in `src/rendercv/schema/models/cv/section.py`.
- **New Locales**: Added in `src/rendercv/schema/models/locale/other_locales`.
