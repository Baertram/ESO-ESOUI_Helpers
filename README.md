# ESO-ESOUI_Helpers

A collection of Python developer and moderation utilities for **The Elder Scrolls Online (ESO)** add-on development and quality assurance on [ESOUI / MMOUI](https://esoui.com).

---

## Included Tools

| Folder | Main Script | Description |
| :--- | :--- | :--- |
| [`ESOUI_AnalyzeGlobalsWithoutRef/`](./ESOUI_AnalyzeGlobalsWithoutRef/) | `ESOUI_AnalyzeGlobalsWithoutRef.py` | Scans extracted `EsoUI` Live/PTS source trees against `ESOUIDocumentation.txt` to isolate undocumented native C++ engine globals, events, constants, and XML controls, exporting them as categorized Lua stub files. |
| [`ESOUI_AddonCodeChecker/`](./ESOUI_AddonCodeChecker/) | `esoui_codecheck.py` | Modular CLI tool to query MMOUI v4 `filelist.json`, download ESOUI add-on archives, run static Lua/Manifest/XML/XSD checks plus optional local Ollama AI reviews, and generate ready-to-post ESOUI BBCode reports. |

---

## Recommended Workflow

1. **Generate Undocumented ESO Globals Stub (`ESOUI_AnalyzeGlobalsWithoutRef`)**
   - Extract the latest ESO Live or PTS `EsoUI` source files and `ESOUIDocumentation.txt`.
   - Run `python ESOUI_AnalyzeGlobalsWithoutRef.py` to generate `<timestamp>-<live|pts>-esoui_globals_missing_in_api_doc.lua`.
2. **Feed into Add-on Code Checker (`ESOUI_AddonCodeChecker`)**
   - Copy or reference the generated Lua stub file as `eso_undocumented_globals.lua` in `ESOUI_AddonCodeChecker/`.
   - Run `python esoui_codecheck.py` (or `esoui_codecheck.cmd`) to validate add-on uploads against the live API, dependency versions, XML schemas, and best practices.

---

## Requirements

- **Python 3.10+**
- Extracted ESO `EsoUI` source files & `ESOUIDocumentation.txt` (local paths configurable in each tool)
- Optional packages for `ESOUI_AddonCodeChecker`: `lxml` (for XSD validation) and `ollama` (for local AI code review)
