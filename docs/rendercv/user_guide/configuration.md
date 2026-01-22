# Configuration Reference

RenderCV uses a YAML file to define both the content of your CV and its design. The file is structured into three main top-level fields:

1.  `cv`: Your personal data and CV content.
2.  `design`: Formatting and styling options.
3.  `locale`: Language and translation settings.

---

## 1. `cv` Field

The `cv` field contains all the information that will appear on your resume.

### Top-Level Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `name` | String | Your full name. |
| `headline` | String | A short professional headline (e.g., "Software Engineer"). |
| `location` | String | Your location (e.g., "San Francisco, CA"). |
| `email` | String \| List | One or more email addresses. |
| `phone` | String \| List | One or more phone numbers (international format recommended). |
| `website` | URL \| List | One or more personal website URLs. |
| `photo` | Path | Path to a profile photo (relative to the YAML file). |
| `social_networks` | List | A list of social network profiles. |
| `custom_connections` | List | Custom links/text for the header. |
| `sections` | Dictionary | The main content of your CV. |

### Social Networks

Each item in `social_networks` requires:

- `network`: One of `LinkedIn`, `GitHub`, `GitLab`, `Instagram`, `ORCID`, `Mastodon`, `StackOverflow`, `ResearchGate`, `YouTube`, `Google Scholar`, `Telegram`, `WhatsApp`, `X`, `Bluesky`.
- `username`: Your username on that platform.

### Sections

The `sections` dictionary keys are section titles (e.g., "Education"). The values are lists of entries. RenderCV automatically detects the type of each entry based on its fields.

#### Common Entry Fields
All entry types (except TextEntry) support:
- `summary`: A block of text describing the entry.
- `highlights`: A list of bullet points.

#### Entry Types

**1. Normal Entry**
*Used for: General experience, volunteering, leadership.*
- `name`: Title of the entry.
- `location`
- `date`: Date string (e.g., "2020 – Present").

**2. Experience Entry**
*Used for: Work experience.*
- `company`: Company name.
- `position`: Job title.
- `location`
- `date`

**3. Education Entry**
*Used for: Academic degrees.*
- `institution`: University/School name.
- `area`: Major/Field of study.
- `degree`: Degree type (BS, MS, PhD).
- `location`
- `date`

**4. Publication Entry**
*Used for: Papers, articles.*
- `title`: Title of the publication.
- `authors`: List of authors.
- `doi`: Digital Object Identifier.
- `journal`: Conference or Journal name.
- `date`

**5. One Line Entry**
*Used for: Skills, Languages.*
- `label`: Category (e.g., "Languages").
- `details`: Description (e.g., "English, Spanish").

**6. Text Entry**
*Used for: Simple paragraphs.*
- A simple string value in the section list.

---

## 2. `design` Field

The `design` field controls the appearance of the generated PDF.

### Top-Level Design Fields

- `theme`: The name of the theme to use (`classic`, `moderncv`, `sb2nov`, `engineeringresumes`).

### `page`
Controls page layout.
- `size`: `us-letter` or `a4`.
- `top_margin`, `bottom_margin`, `left_margin`, `right_margin`: Dimensions (e.g., `0.5in`, `2cm`).
- `show_footer`: `true` or `false`.
- `show_top_note`: `true` or `false`.

### `typography`
Controls fonts and text alignment.
- `font_family`: Name of the font (e.g., `Source Sans 3`). Can be a single string or a dictionary specifying fonts for different elements (`body`, `name`, `section_titles`, etc.).
- `font_size`: Dictionary for `body`, `name`, `headline`, etc. (e.g., `10pt`).
- `line_spacing`: Vertical space between lines (e.g., `1.2em`).
- `alignment`: `justified` or `left`.
- `bold`: Dictionary to enable/disable bold for `name`, `section_titles`, etc.
- `small_caps`: Dictionary to enable/disable small caps.

### `colors`
Controls color schemes. Define specific colors for:
- `body`
- `name`
- `headline`
- `links`
- `section_titles`

Colors can be names (`Red`), hex (`#FF0000`), or RGB (`rgb(255, 0, 0)`).

### `sections`
Controls section formatting.
- `allow_page_break`: Allow sections to split across pages.
- `space_between_regular_entries`
- `show_time_spans_in`: List of sections to show duration (e.g., `['experience']`).

### `header`
Controls header layout.
- `alignment`: `left`, `center`, `right`.
- `photo_position`: `left` or `right`.
- `space_below_name`, `space_below_headline`.

---

## 3. `locale` Field

The `locale` field handles translations and date formats.

- `language`: `english` (default). Setting this automatically sets defaults for other fields.
- `month`, `months`: Translation for "month(s)".
- `year`, `years`: Translation for "year(s)".
- `present`: Translation for "present" (current jobs).
- `last_updated`: Text for "Last updated in".
- `month_names`: List of full month names.
- `month_abbreviations`: List of abbreviated month names.

### Adding a New Language
You can specify `language: "custom"` (or any name) and provide all the translation fields manually to support a new language.
