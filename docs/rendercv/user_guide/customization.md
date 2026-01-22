# Customization Guide

RenderCV allows you to go beyond the built-in themes and customize every aspect of your CV.

## Custom Themes

If the built-in themes don't fit your needs, you can create a custom theme. A custom theme is a folder containing Typst templates (`.typ` and `.j2.typ` files) that RenderCV uses to generate the final PDF.

### Creating a Theme

Run the following command to create a new theme based on the standard templates:

```bash
rendercv create-theme mytheme
```

This creates a folder named `mytheme` in your current directory.

### Theme Structure

The theme folder contains:

- **`__init__.py`**: (Optional) Python code to define custom design options using Pydantic.
- **`Preamble.j2.typ`**: The header/setup file for Typst.
- **`Header.j2.typ`**: Template for the CV header.
- **`Section.j2.typ`**: Template for section titles and structure.
- **`*Entry.j2.typ`**: Templates for each entry type (Experience, Education, etc.).

### Modifying Templates

RenderCV uses **Jinja2** to generate **Typst** code.

1.  **Edit the `.j2.typ` files**: You can change the layout, fonts, and styling using Typst syntax.
2.  **Use Jinja2 variables**: Use variables like `<< cv.name >>` (note the custom delimiters `<<` and `>>`) to insert data.

### Using Your Custom Theme

In your YAML input file, set the theme to your folder name:

```yaml
design:
  theme: mytheme
```

RenderCV will look for a folder named `mytheme` in the same directory as your input file.

## Custom Fonts

You can use any font installed on your system or provide font files.

### System Fonts
Simply verify the font name on your system and use it in your YAML:

```yaml
design:
  typography:
    font_family: "Comic Sans MS" # Please don't actually use this :)
```

### Formatting Specific Elements
You can apply different fonts to different parts of the CV:

```yaml
design:
  typography:
    font_family:
      name: "Roboto Slab"
      body: "Source Sans 3"
      section_titles: "Roboto Slab"
```

## Advanced Logic with Arbitrary Keys

You can add any custom field to your entries in the YAML file and use it in your styling.

**YAML:**
```yaml
cv:
  sections:
    experience:
      - company: Google
        position: Engineer
        my_custom_tag: "Remote"
```

**Template:**
In your custom theme's entry template, you can access this value:

```typst
#if entry.my_custom_tag == "Remote" [
  (Remote Work)
]
```
