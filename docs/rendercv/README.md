# RenderCV Documentation

**RenderCV** is a LaTeX CV/resume generator that allows you to create high-quality, professional CVs from a simple YAML input file. It handles all the complex LaTeX formatting, ensuring a perfect PDF output every time.

## 🚀 Key Features

- **YAML-based Input**: Define your content in a clean, structured YAML file.
- **Automated Formatting**: No more manual tweaking of margins or alignments.
- **Multiple Themes**: Choose from built-in themes or create your own.
- **Schema Validation**: Real-time validation ensures your data is correct before rendering.
- **Cross-Platform**: Works on Linux, macOS, and Windows.

## 📚 Documentation Contents

This documentation is divided into the following sections:

### [User Guide](./user_guide/index.md)

Everything you need to know to use RenderCV.

- **[Installation](./user_guide/installation.md)**: How to install RenderCV on your system.
- **[CLI Reference](./user_guide/cli_reference.md)**: Comprehensive guide to the command-line interface.
- **[Configuration](./user_guide/configuration.md)**: Detailed reference for the YAML data structure and design options.
- **[Customization](./user_guide/customization.md)**: Learn how to customize themes and fonts.

### [Developer Guide](./developer_guide/index.md)

Resources for developers who want to contribute or understand the inner workings.

- **[Architecture](./developer_guide/architecture.md)**: Overview of the codebase structure and design.
- **[Setup & Contributing](./developer_guide/setup_and_contributing.md)**: How to set up your development environment.

---

## ⚡ Quick Start

1.  **Install RenderCV**:
    ```bash
    pip install "rendercv[full]"
    ```

2.  **Create a new CV**:
    ```bash
    rendercv new "John Doe"
    ```

3.  **Render the CV**:
    ```bash
    rendercv render John_Doe_CV.yaml
    ```

4.  **View Results**: Check the `rendercv_output` directory for your PDF and LaTeX files.
