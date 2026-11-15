# ESOUI Addon Code Checker (`esoui_codecheck.py`)

A modular Python CLI tool for downloading, validating, and reviewing **The Elder Scrolls Online (ESO)** add-ons hosted on [ESOUI / MMOUI](https://esoui.com). It combines fast local static rule checks (Lua, XML/XSD, Addon Manifests) with an optional local **Ollama** AI code review and generates compact, ready-to-post ESOUI BBCode reports.

---

## Features

- **MMOUI v4 `filelist.json` Integration (with 15-min RAM & Disk Cache)**
  - **`last <spec>`**: Fetches the top 200 live updated add-ons sorted by `lastUpdate` (supports single ranks, comma/space lists, and ranges like `last 5`, `last 1-5 8 10-12`).
  - **`search <q1, q2>`**: Searches live add-ons by title, author, or ID (with 3-stage `+` regex/literal/wildcard fallback).
  - **`search dep <d1, d2>`**: Finds all add-ons depending on specific libraries (e.g. `search dep LibAddonMenu-2.0`).
  - **`search author <a1, a2>`**: Filters add-ons by author name(s) (e.g. `search author Baertram`).
  - **`search api <v1, !v2>`**: Filters add-ons by supported API version or negated API version to find outdated add-ons (e.g. `search api 101051`, `search api !101051`).
  - **`dl <spec>` & ESOUI URLs**: Supports single IDs, lists, and ranges (`dl 5026`, `dl 630 3586`, `dl 630-632`), displays primary add-on metadata, and downloads the archive(s).
  - **Rich Terminal Highlights**:
    - Clickable OSC 8 terminal links on add-on IDs (`(ID: 630 | ...)`) opening the ESOUI info page directly in your browser.
    - Color-coded primary `APIVersion` tokens relative to the live API (**Red** = older, **Green** = current live API, **White** = newer/PTS).
    - Add-ons in the **Discontinued & Outdated** category (`categoryId: 157`) are highlighted in **Red** with a `✖` prefix.
  - **Persistent Repeat History (`Cache/cmd_history.json`)**:
    - **`repeat`**, **`repeat dl`**, and **`repeat search`** persist across terminal sessions (`clear` commands are excluded).
  - **`force ` prefix**: Bypasses both the `Cache/filelist.json` TTL cache and today's downloaded ZIP cache (e.g. `force last 1-3`, `force dl 5026`, `force repeat`).
- **Static Code & Archive Analysis**
  - **ZIP Structure Audit**: Flags hidden/dev folders (`.git`, `.github`, `.idea`, `.vs`), OS junk (`__MACOSX`, `Thumbs.db`), blocked executables, and unreferenced files.
  - **Lua Static Rules**: Detects deprecated `LibStub`, deprecated `ZO_SavedVars:NewCharacterNameSettings`, global table/function/variable leaks (missing `local`), missing `local` aliases for repeated globals, startup chat spam, and defensive `pcall()` / existence checks.
  - **Manifest Validation (`.addon` / `.txt`)**:
    - Checks line byte length (`<= 301` bytes), folder-to-manifest name matching, `APIVersion` currency, and duplicate `.addon` + `.txt` manifests.
    - Validates `DependsOn` against live `addOnVersion` values in the v4 `filelist.json` (separating missing `>=` on versioned libraries as **Critical violations** from outdated `>=` minimums as **Best practices**, with inline `[current: X]` / `[AddOnVersion unknown]` annotations).
  - **XML & XSD Schema Validation**: Validates UI XML and `Bindings.xml` against local XSD schemas (via `lxml`) and detects inline Lua global leaks inside XML event handlers with exact line numbers.
- **Compact Grouped ESOUI BBCode Report**
  - Suppresses all `PASS` noise; displays a nested `[SIZE="2"]` archive tree at the top marking detected manifests with `[MANIFEST]` and files with critical violations with `:mad:`.
  - Groups **Critical violations** by category (`ZIP Archive`, `Manifest`, `Lua Files`, `XML Files`) and rule, and groups **Best practices** (`Possible action: ...`) with occurrence counts `(xN)` and `[spoiler][SIZE="2"]...[/SIZE][/spoiler]` code snippets.

---

## Project Structure

```text
ESOUI_AddonCodeChecker/
├── esoui_codecheck.py              # CLI entry point, persistent repeat history & batch processor
├── esoui_codecheck.cmd             # Windows launcher script
├── esoui_rules_bestpractice.py     # Custom AI review prompt rules
├── eso_undocumented_globals.lua    # Optional list of undocumented ESO C/Lua globals
├── smoke_test.py                   # Offline unit & smoke test suite
├── smoketest.cmd                   # Windows launcher for smoke_test.py
├── _XSD/                           # ESO UI & Bindings XSD schema files
└── src/
    ├── __init__.py
    ├── esoui_config.py                 # Paths, file whitelists, URLs, Ollama & ANSI UI settings
    ├── esoui_filelist_search.py        # MMOUI v4 filelist.json cache, DependsOn version lookup & search
    ├── esoui_ram_index.py              # In-memory ESO API dictionary & dependency resolver
    ├── esoui_download_io.py            # Authorized HTTP downloader, CLI input & cleanup
    ├── esoui_lua_analyzer.py           # Lua lexer & static rule checks (including global variable leaks)
    ├── esoui_manifest_xml_analyzer.py  # Manifest (.addon/.txt) & XML/XSD checks
    └── esoui_ai_and_report.py          # ZIP audit, Ollama review & grouped BBCode report renderer
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
   - Optionally configure `MODEL_NAME`, `OLLAMA_HOST`, and `ESOUI_UPLOAD_RULES_URL`.

---

## Usage

Run the interactive CLI via `esoui_codecheck.cmd` or directly with Python:

```bash
python esoui_codecheck.py
```

### Supported Interactive & `.txt` Batch Commands

| Command | Example | Description |
| :--- | :--- | :--- |
| `dl <spec>` | `dl 5026` / `dl 630 3586` / `dl 630-632` | Lookup metadata & check add-on(s) by ESOUI ID |
| `<ESOUI URL>` | `https://esoui.com/downloads/info5026` | Download & check add-on from ESOUI URL |
| `last <spec>` | `last 1-5 8 10-12` | Check top 200 live updated add-ons by rank |
| `search <terms>` | `search LibAddonMenu, Master Merchant` | Search live add-ons by title, author, or ID |
| `search dep <terms>` | `search dep LibAddonMenu-2.0` | Search live add-ons by dependency |
| `search author <terms>` | `search author Baertram` | Search live add-ons by author |
| `search api <ver>` | `search api 101051` / `search api !101051` | Search live add-ons by API version (or missing version) |
| `repeat` / `repeat dl` / `repeat search` | `repeat search` / `force repeat` | Repeat last check, `dl`, or `search` command (persisted) |
| `force <cmd>` | `force last 1-3` | Bypass `filelist.json` and ZIP caches |
| `clear <target>` | `clear cache` / `clear zips 261115` | Clean up local cache, ZIPs, or reports |
| `<path.zip>` / `<list.txt>` | `batch_list.txt` | Check a local ZIP archive or run a batch list |

### Running the Smoke Tests

```bash
python smoke_test.py
```
