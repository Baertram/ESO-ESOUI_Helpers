# ESOUI Addon Code Checker (`esoui_codecheck.py`)

A modular Python CLI tool for downloading, validating, and reviewing **The Elder Scrolls Online (ESO)** add-ons hosted on [ESOUI / MMOUI](https://esoui.com). It combines fast local static rule checks (Lua, XML/XSD, Addon Manifests) with an optional local **Ollama** AI code review and generates ready-to-post ESOUI BBCode reports.

---

## Features

- **MMOUI `filelist.json` Integration (with 15-min RAM & Disk Cache)**
  - **`last <spec>`**: Fetches the top 200 live updated add-ons sorted by `lastUpdate` (supports single ranks, lists, and ranges like `last 5`, `last 1-5, 8, 10-12`).
  - **`search <q1, q2>`**: Searches live add-ons by title, author, or ID (with 3-stage `+` regex/literal/wildcard fallback).
  - **`search dep <d1, d2>`**: Finds all add-ons depending on specific libraries (e.g. `search dep LibAddonMenu-2.0`).
  - **`search author <a1, a2>`**: Filters add-ons by author name(s) (e.g. `search author Baertram`).
  - **`search api <v1, !v2>`**: Filters add-ons by supported API version or negated API version to find outdated add-ons (e.g. `search api 101043`, `search api !101043`).
  - **`dl <addonId>` & ESOUI URLs**: Displays live add-on metadata (title, version, author, API version) and downloads the archive.
  - **`force ` prefix**: Bypasses both the `Cache/filelist.json` TTL cache and today's downloaded ZIP cache (e.g. `force last 1-3`, `force dl 5026`).
- **Static Code & Archive Analysis**
  - **ZIP Structure Audit**: Flags hidden/dev folders (`.git`, `.github`, `.idea`, `.vs`), OS junk (`__MACOSX`, `Thumbs.db`), blocked executables, and non-addon files.
  - **Lua Static Rules**: Checks for deprecated `LibStub`, deprecated `ZO_SavedVars:NewCharacterNameSettings`, global table/function leaks, missing `local` aliases for repeated globals, startup chat spam, and defensive `pcall()` / existence checks.
  - **Manifest Validation (`.addon` / `.txt`)**: Checks line byte length (`<= 301` bytes), folder-to-manifest name matching, `APIVersion` currency, valid `DependsOn` / `OptionalDependsOn` syntax, and console UI manifest notices.
  - **XML & XSD Schema Validation**: Validates UI XML and `Bindings.xml` against local XSD schemas (via `lxml`) and detects inline Lua global leaks inside XML event handlers.
- **Local AI Code Review (Ollama)**
  - Queues files containing unverified globals or valid XML structures for sequential review using a local Ollama model (default: `qwen2.5-coder:14b`) and outputs formatted ESOUI BBCode reports.

---

## Project Structure

```text
ESOUI_AddonCodeChecker/
├── esoui_codecheck.py              # CLI entry point & batch processor
├── esoui_codecheck.cmd             # Windows launcher script
├── esoui_rules_bestpractice.py     # Custom AI review prompt rules
├── eso_undocumented_globals.lua    # Optional list of undocumented ESO C/Lua globals
├── smoke_test.py                   # Offline unit & smoke test suite
├── smoketest.cmd                   # Windows launcher for smoke_test.py
├── _XSD/                           # ESO UI & Bindings XSD schema files
└── src/
    ├── __init__.py
    ├── esoui_config.py                 # Paths, file whitelists, Ollama & ANSI UI settings
    ├── esoui_filelist_search.py        # MMOUI filelist.json cache, ranking & multi-mode search
    ├── esoui_ram_index.py              # In-memory ESO API dictionary & dependency resolver
    ├── esoui_download_io.py            # Authorized HTTP downloader, CLI input & cleanup
    ├── esoui_lua_analyzer.py           # Lua lexer & static rule checks
    ├── esoui_manifest_xml_analyzer.py  # Manifest (.addon/.txt) & XML/XSD checks
    └── esoui_ai_and_report.py          # ZIP audit, Ollama review & BBCode report formatter
```

---

## Requirements & Setup

1. **Python 3.10+**
2. **Optional Python packages** (for XSD validation and AI review):
   ```bash
   pip install lxml ollama
   ```
3. **Configuration (`src/esoui_config.py`)**:
   - Adjust `ESO_LIVE_SOURCE_DIR`, `ESO_API_DOC_FILE`, and `ESO_ADDONS_DIR` to match your local ESO installation paths.
   - Optionally configure `MODEL_NAME` and `OLLAMA_HOST` if using Ollama.

---

## Usage

Run the interactive CLI via `esoui_codecheck.cmd` or directly with Python:

```bash
python esoui_codecheck.py
```

### Supported Interactive & `.txt` Batch Commands

| Command | Example | Description |
| :--- | :--- | :--- |
| `dl <id>` | `dl 5026` | Lookup metadata & check add-on by ESOUI ID |
| `<ESOUI URL>` | `https://esoui.com/downloads/info5026` | Download & check add-on from ESOUI URL |
| `last <spec>` | `last 1-5, 8, 10-12` | Check top 200 live updated add-ons by rank |
| `search <terms>` | `search LibAddonMenu, Master Merchant` | Search live add-ons by title, author, or ID |
| `search dep <terms>` | `search dep LibAddonMenu-2.0` | Search live add-ons by dependency |
| `search author <terms>` | `search author Baertram` | Search live add-ons by author |
| `search api <ver>` | `search api 101043` / `search api !101043` | Search live add-ons by API version (or missing version) |
| `force <cmd>` | `force last 1-3` | Bypass `filelist.json` and ZIP caches |
| `clear <target>` | `clear cache` / `clear zips 261114` | Clean up local cache, ZIPs, or reports |
| `<path.zip>` / `<list.txt>` | `batch_list.txt` | Check a local ZIP archive or run a batch list |

### Running the Smoke Tests

```bash
python smoke_test.py
```
