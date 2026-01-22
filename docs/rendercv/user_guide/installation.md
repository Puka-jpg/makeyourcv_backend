# Installation & Setup

This guide covers the prerequisites and steps to install RenderCV.

## Prerequisites

RenderCV requires **Python 3.12 or higher**.

To check your Python version, run:

```bash
python --version
```

If you do not have Python installed, visit [python.org](https://www.python.org/downloads/) to download and install the latest version.

## Installation Methods

### 1. Standard Installation (Recommended)

RenderCV is available on PyPI and can be installed using `pip`. We recommend installing the full version, which includes all necessary dependencies for rendering PDFs and using the CLI effectively.

```bash
pip install "rendercv[full]"
```

> [!NOTE]
> The `[full]` extra ensures that tools like `typer` (for the CLI) and `typst` (for rendering) are installed. If you install without it (`pip install rendercv`), you might miss critical components.

### 2. Upgrade RenderCV

To upgrade to the latest version of RenderCV:

```bash
pip install --upgrade "rendercv[full]"
```

## Verifying Installation

After installation, verify that RenderCV is correctly installed by checking its version:

```bash
rendercv --version
```

You should see output similar to:
`RenderCV v2.6` (or the current installed version).

## Troubleshooting

### "command not found: rendercv"
If you see this error after installation, it means the directory containing Python scripts is not in your system's `PATH`.

- **On Linux/macOS**: Ensure `~/.local/bin` is in your `PATH`.
- **On Windows**: Ensure the `Scripts` folder of your Python installation is in your `PATH`.

### LaTeX Issues
RenderCV uses **Typst** under the hood by default (or can generate LaTeX). You strictly do **not** need a full local LaTeX installation (like TeX Live) if you are using the modern Typst-based headers, as RenderCV handles the rendering engine. However, if you are generating legacy LaTeX files to compile manually, you will need a LaTeX distribution.

## Next Steps

Once installed, proceed to the [CLI Reference](cli_reference.md) to learn how to use the tool.
