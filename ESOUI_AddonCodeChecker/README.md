# ESOUI Addon Code Checker (`esoui_codecheck.py`)

A modular, cross-platform (**Windows, macOS, and Linux**) Python CLI tool for downloading, validating, and reviewing **The Elder Scrolls Online (ESO)** add-ons hosted on [ESOUI / MMOUI](https://esoui.com). It combines fast local static rule checks (Lua, XML/XSD, Addon Manifests) with an optional local **Ollama** AI code review and generates compact, ready-to-post ESOUI BBCode reports.

---

## Features

- **MMOUI v4 `filelist.json` Integration (with 15-min RAM & Disk Cache)**
  - **`last <spec>`**: Fetches the top 200 live updated add-ons sorted by `lastUpdate` (supports single ranks, comma/space lists, and ranges like `last 5`, `last 1-5 8 10-12`).
  - **`search <q1, q2>`**: Searches live add-ons by title, author, or ID (with 3-stage `+` regex/literal/wildcard fallback).
  - **`search dep <d1, d2>`**: Finds all add-ons depending on specific libraries (e.g. `search dep LibAddonMenu-2.0`).
  - **`search author <a1, a2>`**: Filters add-ons by author name(s) (e.g. `search author Baertram`).
  - **`search api <v1, !v2>`**: Filters add-ons by supported API version or negated API version to find outdated add-ons (e.g. `search api 101051`, `search api !101051`).
  - **`dl <spec>` & ESOUI URLs**: Supports single IDs, lists, and ranges (`dl 5026`, `dl 630 3586`, `dl 630-632`), displays primary add-on metadata, and downloads the archive(s).
  - **Automatic Dependency Resolution & Caching**:
    - Automatically downloads and extracts missing `DependsOn` / `OptionalDependsOn` libraries from ESOUI into `Cache/AddOns/_extracted/` (prioritizing standalone entries, skipping *Outdated & Discontinued* packages and embedded sub-libraries).
    - Scans each dependency once per session to resolve cross-addon globals without false positives.
  - **Rich Terminal Highlights**:
    - Clickable OSC 8 terminal links on add-on IDs (`(ID: 630 | ...)`) opening the ESOUI info page directly in your browser.
    - Color-coded primary `APIVersion` tokens relative to the live API (**Red** = older, **Green** = current live API, **White** = newer/PTS).
    - Add-ons in the **Discontinued & Outdated** category (`categoryId: 157`) are highlighted in **Red** with a `✖` prefix.
  - **Persistent Repeat History (`Cache/cmd_history.json`)**:
    - **`repeat`**, **`repeat dl`**, and **`repeat search`** persist across terminal sessions (`clear` commands are excluded).
  - **`force ` prefix**: Bypasses both the `Cache/filelist.json` TTL cache and today's downloaded ZIP cache (e.g. `force last 1-3`, `force dl 5026`, `force repeat`).
  - **`bpglobal` CLI Toggle**: Toggles the verbose *"Global variable used multiple times w/o a local reference"* report section on/off (`OFF` by default).
- **Static Code & Archive Analysis**
  - **ZIP Structure Audit**:
    - Flags hidden/dev folders (`.git`, `.github`, `.idea`, `.vs`), OS junk (`__MACOSX`, `Thumbs.db`), blocked executables, and unreferenced files.
    - Verifies root folder-to-manifest naming (`Wrong addon zip`) and warns when a ZIP contains multiple top-level folders (`Check addon zip`).
    - Detects legacy `.font` files and recommends migrating to `.slug` files.
  - **Lua Static Rules**:
    - **Global Scope & Naming Hygiene**: Detects missing `local` declarations (including inside single-line closures/callbacks), multiple global addon tables, leaked global functions, and non-unique / too short global names (`< 6` chars or not anchored to the add-on name).
    - **Single-File Strict-Local Detection**: Detects single-file add-ons without `Bindings.xml`, XML global usage, or public API methods (`get*`, `set*`, `is*`, etc.) and instructs keeping everything strictly `local`.
    - **ESO Event Filters (`RegisterForEvent` / `AddFilterForEvent`)**: Syncs filter mappings from the ESOUI Wiki and flags missing event filters or redundant Lua-side parameter/unit-tag checks in event callbacks.
    - **LibGroupBroadcast ID Conflict Check**: Validates `DeclareProtocol` and `DeclareCustomEvent` IDs against the live ESOUI Wiki `LibGroupBroadcast_IDs` table.
    - **Deprecated APIs & AI Code Hints**: Flags deprecated `LibStub`, deprecated `ZO_SavedVars:NewCharacterNameSettings`, missing `local` aliases for addon tables, defensive `pcall()` wrappers, and unnecessary existence checks on documented ESO globals.
  - **Manifest Validation (`.addon` / `.txt`)**:
    - Checks line byte length (`<= 301` bytes), folder-to-manifest name matching, `APIVersion` currency, `SavedVariables` uniqueness/length (`>= 6` chars and anchored to the add-on/global table name), `SavedVariablesPerCharacter` misuse, and duplicate `.addon` + `.txt` manifests.
    - Validates `DependsOn` against live `addOnVersion` values in the v4 `filelist.json` (separating missing `>=` on versioned libraries as **Critical violations** from outdated `>=` minimums as **Best practices**, with inline `[current: X]` / `[AddOnVersion unknown]` annotations).
    - Flags hardcoded 2-letter language files (e.g. `en.lua`, `de.lua`) and recommends dynamic `$(language)` placeholders.
  - **XML & XSD Schema Validation**:
    - Validates UI XML and `Bindings.xml` against local XSD schemas (via `lxml`), resolves `$(parent)` and template control inheritance in the RAM index, and detects inline Lua global leaks inside XML event handlers with exact line numbers.
- **Compact Grouped ESOUI BBCode Report (9,999-Char Safe)**
  - Suppresses all `PASS` noise; displays a nested `[SIZE="2"]` archive tree at the top marking detected manifests with `[MANIFEST]` and files with critical violations with `:mad:`.
  - Groups **Critical violations** by category (`ZIP Archive`, `Manifest (.addon / .txt)`, `Lua Files`, `XML Files`) and rule, and groups **Best practices** (`Possible action: ...`) with `[spoiler][SIZE="2"]...[/SIZE][/spoiler]` code snippets.
  - Automatically compacts spoilers and trees to stay within ESOUI's **9,999-character** comment limit (truncating safely with `[trunc.]` if needed).
---

## Project Structure

```text
ESOUI_AddonCodeChecker/
├── esoui_codecheck.py              # Cross-platform CLI entry point (Windows, macOS, Linux)
├── esoui_codecheck.cmd             # Optional Windows launcher script
├── esoui_rules_bestpractice.py     # Custom AI review prompt rules
├── eso_undocumented_globals.lua    # Optional list of undocumented ESO C/Lua globals
├── smoke_test.py                   # Offline unit & smoke test suite
├── smoketest.cmd                   # Optional Windows launcher for smoke_test.py
├── _XSD/                           # ESO UI & Bindings XSD schema files
└── src/
    ├── __init__.py
    ├── esoui_config.py                 # Paths, file whitelists, URLs, Ollama & ANSI UI settings
    ├── esoui_filelist_search.py        # MMOUI v4 filelist.json cache, DependsOn version lookup & search
    ├── esoui_ram_index.py              # In-memory ESO API dictionary, XML control resolver & dependency cache
    ├── esoui_download_io.py            # Authorized HTTP downloader, CLI input (with ESC support) & cleanup
    ├── esoui_lua_analyzer.py           # Lua lexer & static rule checks (globals, event filters, LGB IDs)
    ├── esoui_manifest_xml_analyzer.py  # Manifest (.addon/.txt) & XML/XSD checks
    └── esoui_ai_and_report.py          # ZIP audit, chunked Ollama review & grouped BBCode report renderer
```

---

## Requirements & Setup

1. **Python 3.10+** (works on Windows, macOS, and Linux).
2. **Optional Python packages** (for XSD validation and local AI review):
   ```bash
   pip install lxml ollama
   ```
3. **Configuration (`src/esoui_config.py`)**:
   - Adjust `ESO_LIVE_SOURCE_DIR`, `ESO_API_DOC_FILE`, and `ESO_ADDONS_DIR` to match your local ESO installation paths on your operating system.
   - Optionally configure `MODEL_NAME`, `OLLAMA_HOST`, and `ESOUI_UPLOAD_RULES_URL`.

---

## Local AI Setup (Ollama)

The add-on checker can use a local **Ollama** LLM (default: `qwen2.5-coder:14b`) to semantically review files containing unverified globals or valid XML structures without sending any add-on code to external cloud services (large Lua files are automatically split into scope-safe chunks, and AI review can be aborted anytime with `ESC`).
### 1. Install Ollama (Windows, macOS, or Linux)
- **Windows / macOS**: Download and run the installer from [ollama.com](https://ollama.com).
  - *Optional (Windows custom installation directory, e.g. `D:\Ollama`)*: Open a terminal in your Downloads folder and run:
    ```powershell
    .\OllamaSetup.exe /DIR="D:\Ollama"
    ```
- **Linux**: Install via the official install script from [ollama.com](https://ollama.com).
- **Optional custom model storage directory**: Before pulling models, set the `OLLAMA_MODELS` environment variable on any OS to store large model files on a separate drive/partition (e.g. `D:\OllamaModels` on Windows or `/mnt/models/ollama` on Linux/macOS).

### 2. Download & Verify the Default Model (`qwen2.5-coder:14b`)
Open a **new** terminal window (so updated `PATH` and `OLLAMA_MODELS` variables are active) and pull/test the default coding model:
```bash
ollama run qwen2.5-coder:14b
```
Once the download finishes and the model responds, exit the interactive prompt with `/bye`.

### 3. Configure `src/esoui_config.py` & Everyday Behavior
- In `src/esoui_config.py`, verify or adjust the AI settings if needed:
  - `MODEL_NAME = "qwen2.5-coder:14b"`
  - `OLLAMA_HOST = "http://localhost:11434"`
  - `AI_NUM_CTX = 16384`
- **Automatic Handling**: When an add-on requires an AI review, `esoui_codecheck.py` automatically checks whether the Ollama server is running, starts `ollama serve` in the background if needed, and verifies that the configured model is available locally. If Ollama is not installed, the checker falls back cleanly to static RAM-tracker reporting.

---

## Usage

The tool runs cross-platform on **Windows, macOS, and Linux**:

```bash
python esoui_codecheck.py
```
*(On Windows, you can also double-click `esoui_codecheck.cmd`.)*

### Supported Interactive & `.txt` Batch Commands

| Command | Example | Description |
| :--- | :--- | :--- |
| `dl <spec>` | `dl 5026` / `dl 630 3586` / `dl 630-632` | Lookup metadata & check add-on(s) by ESOUI ID |
| `<ESOUI URL>` | `https://esoui.com` | Download & check add-on from ESOUI URL |
| `last <spec>` | `last 1-5 8 10-12` | Check top 200 live updated add-ons by rank |
| `search <terms>` | `search LibAddonMenu, Master Merchant` | Search live add-ons by title, author, or ID |
| `search dep <terms>` | `search dep LibAddonMenu-2.0` | Search live add-ons by dependency |
| `search author <terms>` | `search author Baertram` | Search live add-ons by author |
| `search api <ver>` | `search api 101051` / `search api !101051` | Search live add-ons by API version (or missing version) |
| `repeat` / `repeat dl` / `repeat search` | `repeat search` / `force repeat` | Repeat last check, `dl`, or `search` command (persisted) |
| `force <cmd>` | `force last 1-3` | Bypass `filelist.json` and ZIP caches |
| `bpglobal` | `bpglobal` | Toggle repeated global variable best-practice section (`ON`/`OFF`) |
| `clear <target>` | `clear cache` / `clear zips 261115` | Clean up local cache, ZIPs, or reports |
| `<path.zip>` / `<list.txt>` | `batch_list.txt` | Check a local ZIP archive or run a batch list |

### Running the Smoke Tests

```bash
python smoke_test.py
```
