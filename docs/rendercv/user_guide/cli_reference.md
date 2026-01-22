# CLI Reference

The `rendercv` command-line interface (CLI) is the primary way to interact with the application.

## Global Options

- `--version`, `-v`: Show the installed version of RenderCV.
- `--help`, `-h`: Show help messages for commands.

## Commands

### `rendercv new`

Generate a new YAML input file to get started.

```bash
rendercv new "Full Name" [OPTIONS]
```

**Arguments:**

- `FULL_NAME`: Your full name. This will be used to name the input file (e.g., `Full_Name_CV.yaml`) and pre-fill the name field.

**Options:**

- `--theme TEXT`: The name of the theme to use (default: `classic`). Available themes: `classic`, `moderncv`, `sb2nov`, `engineeringresumes`, `engineeringclassic`.
- `--locale TEXT`: The name of the locale to use (default: `english`).
- `--create-typst-templates`: Create Typst templates for advanced customization.
- `--create-markdown-templates`: Create Markdown templates for advanced customization.

**Example:**

```bash
rendercv new "John Doe" --theme moderncv
```

---

### `rendercv render`

Render a YAML input file into PDF, Typst, Markdown, and HTML.

```bash
rendercv render INPUT_FILE [OPTIONS]
```

**Arguments:**

- `INPUT_FILE`: The path to your YAML input file (e.g., `John_Doe_CV.yaml`).

**Input Options (Split YAML):**
You can split your configuration into multiple files.

- `--design`, `-d PATH`: Path to a separate design YAML file.
- `--locale-catalog`, `-lc PATH`: Path to a separate locale YAML file.
- `--settings`, `-s PATH`: Path to a separate settings YAML file.

**Output Path Options:**
By default, outputs are saved in a `rendercv_output` directory. You can customize this:

- `--pdf-path`, `-pdf PATH`: Custom path for the PDF output.
- `--typst-path`, `-typ PATH`: Custom path for the Typst output.
- `--markdown-path`, `-md PATH`: Custom path for the Markdown output.
- `--html-path`, `-html PATH`: Custom path for the HTML output.
- `--png-path`, `-png PATH`: Custom path for PNG output (useful for previews).

**Generation Control:**
Use these flags to skip generating specific formats:

- `--dont-generate-pdf`, `-nopdf`
- `--dont-generate-typst`, `-notyp`
- `--dont-generate-html`, `-nohtml`
- `--dont-generate-markdown`, `-nomd`
- `--dont-generate-png`, `-nopng`

**Other Options:**

- `--watch`, `-w`: Watch the input file for changes and re-render automatically.
- `--quiet`, `-q`: Suppress status messages.

**Overriding Values:**
You can override any value in the YAML file directly from the CLI using dot notation.

**Example:**

```bash
# update the phone number just for this render
rendercv render cv.yaml --cv.phone "555-0199"
```

---

### `rendercv create-theme`

Create a custom theme folder with templates to customize.

```bash
rendercv create-theme THEME_NAME
```

**Arguments:**

- `THEME_NAME`: The name of the new theme. This will create a directory with this name.

**Example:**

```bash
rendercv create-theme mycustomtheme
```
