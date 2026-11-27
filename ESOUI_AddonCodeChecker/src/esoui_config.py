"""
Globale Konfiguration, Pfade, Datei-Whitelists und Terminal-Helfer für esoui_codecheck.
"""

import os
import re
import sys
import shutil
import textwrap

# Enable verbose debug logging when '--debug' is passed on the command line
DEBUG_MODE = "--debug" in [arg.lower() for arg in sys.argv[1:]]

# ==============================================================================
# 1. GLOBAL CONFIGURATION & PATHS
# ==============================================================================
USER_HOME = os.path.expanduser("~")
BASE_FOLDER = os.path.join(USER_HOME, "Downloads", "ESOUI_AddonCodeChecker")
ZIP_FOLDER = os.path.join(BASE_FOLDER, "Zips")          # Downloaded and local ZIP archives grouped by YYMMDD
EXTRACT_FOLDER = os.path.join(BASE_FOLDER, "Tmp")       # Temporary extraction workspace wiped after each addon
REPORTS_BASE_DIR = os.path.join(BASE_FOLDER, "_Reports")  # Generated BBCode report .txt files grouped by YYMMDD

# Allowed documentation, addon asset, and blocked executable file extensions in ZIP archives
ALLOWED_DOC_EXTENSIONS = {'.md', '.license', '.bbcode', '.log'}
ALLOWED_EXTENSIONS = {'.txt', '.addon', '.lua', '.xml', '.dds', '.slug', '.font', '.str', '.dat', '.lang'} | ALLOWED_DOC_EXTENSIONS
# Allowed top-level directory prefixes for unofficial ESO language patches (must lie at ZIP root)
ALLOWED_LANGUAGE_PATCH_ROOT_PREFIXES = ("esoui/lang/", "gamedata/lang/")
ALLOWED_DOC_STEMS = {'readme', 'license', 'licence', 'copying', 'copyright', 'changelog', 'changes', 'change'}
BLOCKED_EXECUTABLE_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.ps1', '.vbs', '.vbe', '.js', '.jse',
    '.wsf', '.wsh', '.py', '.pyw', '.sh', '.bash', '.zsh', '.msi', '.msp',
    '.dll', '.sys', '.drv', '.ocx', '.cpl', '.scr', '.pif', '.dmg', '.pkg',
    '.app', '.command', '.jar', '.apk', '.elf', '.bin', '.run', '.reg'
}

# Hidden/IDE folders, OS metadata junk, and dependency scan exclusion rules
FORBIDDEN_KEYWORDS = {'.github', '.vs', '.idea', '.git'}
FORBIDDEN_OS_JUNK_NAMES = {"__macosx", "thumbs.db", "desktop.ini", ".ds_store"}
EXCLUDED_DEPENDENCY_ADDON_FOLDERS = {"DumpVars"}
# Add-on titles / IDs (lowercase) whose embedded sub-libraries must NEVER be resolved as dependencies for other add-ons
EXCLUDED_EMBEDDED_DEPENDENCY_ADDONS = frozenset({
    "fcoaccessibility",
    "3586",
})
# Relative paths or fnmatch wildcard patterns inside ESO_ADDONS_DIR to skip during dependency scanning
EXCLUDED_DEPENDENCY_FILES = {
    "/TamrielTradeCentre/PriceTable*.lua",
}

# Built-in Lua standard libraries, reserved keywords, and non-language 2-letter file stems
LUA_STD_LIBS = {
    "string", "table", "math", "pairs", "ipairs", "next", "select", "unpack",
    "type", "tostring", "tonumber", "pcall", "xpcall", "error", "assert",
    "setmetatable", "getmetatable", "rawget", "rawset", "rawequal"
}
LUA_KEYWORDS = {
    "local", "function", "if", "end", "then", "return", "else", "elseif",
    "for", "in", "pairs", "ipairs", "true", "false", "nil", "and", "or",
    "not", "while", "repeat", "until", "break", "do", "self", "_"
}
NON_LANG_TWO_LETTER_STEMS = {"ui", "db", "sv", "io", "id", "os", "pc", "ps", "xb"}

# Generic words in add-on/manifest names that alone are too weak to prove global/SavedVariables uniqueness
GENERIC_ADDON_NAME_WORDS = frozenset({
    "addon", "addons", "tracker", "helper", "helpers", "manager", "utils", "utility",
    "system", "menu", "panel", "window", "frame", "timer", "timers", "alert", "alerts",
    "buff", "debuff", "buffs", "debuffs", "saved", "vars", "savedvars", "config",
    "settings", "options", "core", "main", "data", "info", "list", "bar", "bars",
    "icon", "icons", "hud", "gui", "lib", "library", "mod", "plugin", "tool", "tools",
})


def extract_addon_anchor_tokens(raw_name):
    """Extracts normalized full-name and distinctive word/CamelCase anchor tokens (>= 5 chars) from an add-on name."""
    anchors = set()
    if not raw_name:
        return anchors
    text = str(raw_name).strip()
    clean_full = re.sub(r"[^a-z0-9]", "", text.lower())
    if len(clean_full) >= 4:
        anchors.add(clean_full)
        stripped_digits = re.sub(r"\d+$", "", clean_full)
        if len(stripped_digits) >= 4:
            anchors.add(stripped_digits)

    # Split on delimiters (_ - space .) and CamelCase boundaries
    camel_split = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    camel_split = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", camel_split)
    for part in re.split(r"[^A-Za-z0-9]+", camel_split):
        low_p = part.lower()
        if len(low_p) >= 5 and not low_p.isdigit() and low_p not in GENERIC_ADDON_NAME_WORDS:
            anchors.add(low_p)
            p_no_digits = re.sub(r"\d+$", "", low_p)
            if len(p_no_digits) >= 5 and p_no_digits not in GENERIC_ADDON_NAME_WORDS:
                anchors.add(p_no_digits)
    return anchors

# Function names (e.g. 'GetLibAddonMenu' or 'LibCodesCommonCode.GetLibAddonMenu') where legacy LibStub checks are allowed
LIBSTUB_EXCLUDED_FUNCTIONS = {
    "GetLibAddonMenu",
    "LibCodesCommonCode.GetLibAddonMenu",
}

# Local ESO reference sources used to build the fast RAM lookup dictionary
ESO_LIVE_SOURCE_DIR = r"Q:\Tools\!Spiele\TESO\EsoUI\esoui_src\live\esoui"
ESO_API_DOC_FILE = r"Q:\Tools\!Spiele\TESO\EsoUI\esoui_src\live\ESOUIDocumentation.txt"
ESO_EXTRA_GLOBALS_FILE = r"Q:\Tools\!Spiele\TESO\EsoUI\!!Parser\eso-api_base_Manual_NonGenerated.lua"

# Relative input assets resolved against the project root (parent of src/)
ADD_INPUT_DIR = "add_input"
ESO_UNDOCUMENTED_GLOBALS_FILE = os.path.join(ADD_INPUT_DIR, "eso_undocumented_globals.lua")
ESO_XML_SCHEMA_FILE = os.path.join(ADD_INPUT_DIR, "_XSD", "esoui_gui_xml.xsd")
ESO_BINDINGS_SCHEMA_FILE = os.path.join(ADD_INPUT_DIR, "_XSD", "esobindings.xsd")
WIKI_EVENT_FILTERS_FILE = os.path.join(ADD_INPUT_DIR, "wiki_event_filters.json")
WIKI_LGB_IDS_TXT_FILE = os.path.join(ADD_INPUT_DIR, "LibGroupBroadcast_IDs.txt")

# Local ESO live AddOns folder and persistent cache paths for dependencies, filelist, and CLI history
ESO_ADDONS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Elder Scrolls Online", "live", "AddOns")
CACHE_DIR = "Cache"
CACHE_ADDONS_DIR = os.path.join(CACHE_DIR, "AddOns")
CACHE_ADDONS_EXTRACTED_DIR = os.path.join(CACHE_ADDONS_DIR, "_extracted")
CMD_HISTORY_FILE = os.path.join(CACHE_DIR, "cmd_history.json")
DEPENDENCY_CACHE_FILE = os.path.join(CACHE_DIR, "dependency_globals_cache.json")

# Case-insensitive directory names inside an add-on that NEVER load on PC clients
PC_IGNORED_SUBDIRS = frozenset({
    "console",
    "xb1",
    "playstation",
    "internal",
    "future",
})

# Authorized domains and MMOUI/ESOUI limits
_DOMAIN_ESOUI = ".".join(["esoui", "com"])
_DOMAIN_ESOUI_WWW = ".".join(["www", "esoui", "com"])
_DOMAIN_ESOUI_WIKI = ".".join(["wiki", "esoui", "com"])
_DOMAIN_MMOUI = ".".join(["mmoui", "com"])
_DOMAIN_MMOUI_API = ".".join(["api", "mmoui", "com"])

ALLOWED_DOWNLOAD_DOMAINS = {_DOMAIN_ESOUI, _DOMAIN_ESOUI_WWW, _DOMAIN_MMOUI}
ESOUI_LATEST_MAX_ITEMS = 200
ESOUI_BATCH_CHUNK_SIZE = 10
# Safe character limit for a single ESOUI / MMOUI vBulletin add-on comment
ESOUI_COMMENT_MAX_CHARS = 9999

# ESOUI, ESOUI Wiki & MMOUI v4 API endpoints
_ESOUI_BASE = "https://" + _DOMAIN_ESOUI_WWW
_ESOUI_WIKI_BASE = "https://" + _DOMAIN_ESOUI_WIKI
ESOUI_WIKI_HOST = _DOMAIN_ESOUI_WIKI
MMOUI_FILELIST_URL = "https://" + _DOMAIN_MMOUI_API + "/v4/game/ESO/filelist.json"
ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX = _ESOUI_BASE + "/downloads/info"
ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX = _ESOUI_BASE + "/downloads/dl"
ESOUI_UPLOAD_RULES_URL = _ESOUI_BASE + "/forums/showthread.php?t=10790"
ESOUI_WIKI_EVENT_FILTERS_URL = _ESOUI_WIKI_BASE + "/AddFilterForEvent#Filter_Types"
ESOUI_WIKI_LGB_EVENTS_URL = _ESOUI_WIKI_BASE + "/LibGroupBroadcast_IDs#Events"
ESOUI_WIKI_LGB_PROTOCOLS_URL = _ESOUI_WIKI_BASE + "/LibGroupBroadcast_IDs#Protocols"
ESOUI_WIKI_LGB_API_URL = _ESOUI_WIKI_BASE + "/api.php?action=parse&page=LibGroupBroadcast_IDs&prop=wikitext&format=json"

# Local Ollama LLM settings
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen2.5-coder:14b"
AI_NUM_CTX = 32768
AI_TIMEOUT_SECONDS = 60
# Enable ANSI escape sequence processing in Windows console hosts
if os.name == "nt":
    os.system("")


class C:
    """ANSI color codes for structured console output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    ORANGE = "\033[38;5;208m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


def get_project_root_dir():
    """Returns the root directory containing esoui_codecheck.py (one level above src/)."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resolve_config_file_path(file_setting):
    """Resolves a config file path against project root (with fallback from add_input/ to legacy root)."""
    if not file_setting or not isinstance(file_setting, str):
        return None
    if os.path.isabs(file_setting):
        return file_setting
    root_dir = get_project_root_dir()
    candidate = os.path.join(root_dir, file_setting)
    if os.path.exists(candidate):
        return candidate
    norm_rel = file_setting.replace("\\", "/")
    prefix = ADD_INPUT_DIR.replace("\\", "/").rstrip("/") + "/"
    if norm_rel.startswith(prefix):
        legacy_candidate = os.path.join(root_dir, norm_rel[len(prefix):].replace("/", os.sep))
        if os.path.exists(legacy_candidate):
            return legacy_candidate
    return candidate


def print_wrapped_tree_item(text, first_prefix="    │     ", next_prefix="    │       ", color=""):
    """Wraps long console messages cleanly to terminal width while keeping tree indentation."""
    term_width = shutil.get_terminal_size((110, 24)).columns
    avail_width = max(40, term_width - len(first_prefix) - 2)
    wrapped_lines = textwrap.wrap(text, width=avail_width) or [text]
    for idx, line in enumerate(wrapped_lines):
        prefix = first_prefix if idx == 0 else next_prefix
        print(f"{prefix}{color}{line}{C.RESET if color else ''}")


def make_clickable_file_link(file_path, color=C.WHITE, display_text=None):
    """Formats a local file path as a clickable OSC 8 terminal hyperlink."""
    abs_path = os.path.abspath(file_path)
    file_uri = "file:///" + abs_path.replace("\\", "/")
    label = display_text if display_text is not None else abs_path
    return f"\033]8;;{file_uri}\033\\{color}\033[4m{label}{C.RESET}\033]8;;\033\\"


def make_clickable_url_link(url, color=C.CYAN, display_text=None):
    """Formats an HTTP/HTTPS URL as a clickable OSC 8 terminal hyperlink."""
    label = display_text if display_text is not None else url
    return f"\033]8;;{url}\033\\{color}\033[4m{label}{C.RESET}\033]8;;\033\\"


def _format_relative_dated_label(file_path, base_dir, icon_prefix):
    """Formats file_path relative to base_dir as '<icon>\\<YYMMDD>\\<filename>' (or '<icon>\\<filename>')."""
    abs_file = os.path.abspath(file_path)
    abs_base = os.path.abspath(base_dir)
    try:
        rel_path = os.path.relpath(abs_file, abs_base)
    except ValueError:
        rel_path = ""
    if rel_path and not rel_path.startswith(".."):
        rel_win = rel_path.replace("/", "\\").lstrip("\\")
        return f"{icon_prefix}\\{rel_win}"
    parent_dir = os.path.basename(os.path.dirname(abs_file))
    base_name = os.path.basename(abs_file)
    if parent_dir and parent_dir.isdigit() and len(parent_dir) == 6:
        return f"{icon_prefix}\\{parent_dir}\\{base_name}"
    return f"{icon_prefix}\\{base_name}"


def format_zip_display_link(zip_path, color=C.WHITE):
    """Formats a ZIP path as a clickable OSC 8 hyperlink labeled '📦\\<YYMMDD>\\<filename.zip>'."""
    label = _format_relative_dated_label(zip_path, ZIP_FOLDER, "\U0001f4e6")
    return make_clickable_file_link(zip_path, color=color, display_text=label)


def format_report_display_link(report_path, color=C.WHITE, custom_label=None):
    """Formats a report path as a clickable OSC 8 hyperlink labeled '📄\\<YYMMDD>\\<report.txt>' (or custom_label)."""
    label = custom_label if custom_label is not None else _format_relative_dated_label(report_path, REPORTS_BASE_DIR, "\U0001f4c4")
    return make_clickable_file_link(report_path, color=color, display_text=label)

