# ESOUI Global Variables Reference Analyzer (`ESOUI_AnalyzeGlobalsWithoutRef.py`)

A static Python code analysis tool for **The Elder Scrolls Online (ESO)** `EsoUI` source codebase. It cross-references all global identifiers used across the official Lua UI source files against `ESOUIDocumentation.txt` and in-code definitions to isolate, categorize, and export undocumented native C++ engine globals, constants, events, and XML UI controls as ready-to-use Lua stub files (`eso_undocumented_globals.lua`).

---

## Features

- **Topological Manifest Loading Order (DFS)**:
  - Parses all `.txt` add-on/UI manifests in the extracted `EsoUI` source directory and resolves `## DependsOn:` and `## PCDependsOn:` dependencies via Depth-First Search (`resolve_loading_order`).
  - Caches the resolved loading order and file list per server scope and API version in `_cache/esoui_manifest_cache_<live|pts>.json`.
- **Two-Phase Static Code Analysis**:
  - **Phase 1 (Pre-Scan)**: Extracts documented API globals from `ESOUIDocumentation.txt`, `ZO_CreateStringId(...)` registrations, global Lua assignments/functions, `ZO_*` identifiers, and XML `name="..."` UI control/font definitions.
  - **Phase 2 (Scope-Aware Reference Check)**: Strips comments, multiline strings, and `$(macro)` tokens while preserving exact line and column indices, tracks file-level locals, loop variables, balanced single/multi-line function parameters, and hierarchical block scopes (`if`/`for`/`while`/`do`/`function`/`repeat` ... `end`/`until`).
- **10-Bucket Categorized Lua Stub Output**:
  - Exports all undocumented globals as `<identifier> = nil` definitions with exact file path, line, column, and highlighted source context (`[[ identifier ]]`) into `<YYMMDD_HHMMSS>-<live|pts>-esoui_globals_missing_in_api_doc.lua`:
    1. **Global Constants** (`ITERATION_` / `_MIN_VALUE` / `_MAX_VALUE`)
    2. **Global Constants** (General All-Caps & Flags)
    3. **Global Events** (`EVENT_*`)
    4. **Global Settings** (`*_SETTING_*`)
    5. **Event Handlers** (`On[A-Z]*`)
    6. **String Constants** (`SI_*`)
    7. **ZOs Special API** (`hmake`, `hstructure`, `internalassert`)
    8. **Variables to check** (lowercase / camelCase identifiers without local definition)
    9. **Other Undocumented Variables**
    10. **Global XML defined controls/fonts**
- **Live & PTS Server Scope Support + Optional Debug Log**:
  - Interactive selection between **Live** and **PTS** source trees, optional manifest cache rebuild (`Y/n`), and detailed timestamped logging via `--debug`.

---

## Requirements & Configuration

1. **Python 3.8+** (uses only Python standard library modules: `os`, `re`, `json`, `time`, `sys`, `datetime`).
2. **Extracted EsoUI Source & `ESOUIDocumentation.txt`**:
   - Configure the paths at the top of `ESOUI_AnalyzeGlobalsWithoutRef.py`:
     ```python
     FILENAME_ESOUI_API      = "ESOUIDocumentation.txt"
     DIR_CACHE               = "_cache/"

     # ---- LIVE SERVER CONFIGURATION ----
     LIVE_PATH_ESOUI_DOC     = "Q:/Tools/!Spiele/TESO/EsoUI/esoui_src/live/"
     LIVE_DIR_ESOUI_SOURCES  = LIVE_PATH_ESOUI_DOC
     LIVE_DIR_OUTPUT         = ""

     # ---- PTS (PUBLIC TEST SERVER) CONFIGURATION ----
     PTS_PATH_ESOUI_DOC      = "Q:/Tools/!Spiele/TESO/EsoUI/esoui_src/PTS/"
     PTS_DIR_ESOUI_SOURCES   = PTS_PATH_ESOUI_DOC
     PTS_DIR_OUTPUT          = ""
     ```

---

## Usage

Run the script from the terminal:

```bash
python ESOUI_AnalyzeGlobalsWithoutRef.py
```

For full timestamped diagnostic logs (`<YYMMDD_HHMMSS>-<scope>-debug.log`), pass `--debug`:

```bash
python ESOUI_AnalyzeGlobalsWithoutRef.py --debug
```

### Interactive Prompts

1. **Select server scope**:
   - `1` -> **Live**
   - `2` -> **PTS (Public Test Server)**
2. **Force rebuild manifest cache? (`Y/n`)**:
   - Press `Enter` or `Y` to re-scan all `.txt` manifests and rebuild `_cache/esoui_manifest_cache_<scope>.json`.
   - Enter `n` to reuse the cached loading order if the `APIVersion` matches.

---

## Integration with `ESOUI_AddonCodeChecker`

The generated `*-esoui_globals_missing_in_api_doc.lua` file can be used directly as `eso_undocumented_globals.lua` inside **`ESOUI_AddonCodeChecker`** so that undocumented native ESO globals and constants are recognized during static add-on analysis.
