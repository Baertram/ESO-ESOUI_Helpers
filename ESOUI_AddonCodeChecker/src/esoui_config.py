"""
Globale Konfiguration, Pfade, Datei-Whitelists und Terminal-Helfer für esoui_codecheck.
"""

import os
import sys
import shutil
import textwrap

DEBUG_MODE = "--debug" in [arg.lower() for arg in sys.argv[1:]]

# ==============================================================================
# 1. GLOBAL CONFIGURATION & PATHS
# ==============================================================================
USER_HOME = os.path.expanduser("~")
BASE_FOLDER = os.path.join(USER_HOME, "Downloads", "ESOUI_AddonCodeChecker")
ZIP_FOLDER = os.path.join(BASE_FOLDER, "Zips")
EXTRACT_FOLDER = os.path.join(BASE_FOLDER, "Tmp")
REPORTS_BASE_DIR = os.path.join(BASE_FOLDER, "_Reports")

ALLOWED_EXTENSIONS = {'.txt', '.addon', '.lua', '.xml', '.dds', '.md', '.license', '.bbcode'}
ALLOWED_DOC_STEMS = {'readme', 'license', 'licence', 'copying', 'copyright', 'changelog', 'changes'}
BLOCKED_EXECUTABLE_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.ps1', '.vbs', '.vbe', '.js', '.jse',
    '.wsf', '.wsh', '.py', '.pyw', '.sh', '.bash', '.zsh', '.msi', '.msp',
    '.dll', '.sys', '.drv', '.ocx', '.cpl', '.scr', '.pif', '.dmg', '.pkg',
    '.app', '.command', '.jar', '.apk', '.elf', '.bin', '.run', '.reg'
}
FORBIDDEN_KEYWORDS = {'.github', '.vs', '.idea', '.git'}
FORBIDDEN_OS_JUNK_NAMES = {"__macosx", "thumbs.db", "desktop.ini", ".ds_store"}
EXCLUDED_DEPENDENCY_ADDON_FOLDERS = {"DumpVars"}
# Relative paths or fnmatch wildcard patterns inside ESO_ADDONS_DIR to skip during dependency scanning
EXCLUDED_DEPENDENCY_FILES = {
    "/TamrielTradeCentre/PriceTable*.lua",
}
LUA_STD_LIBS = {
    "string", "table", "math", "pairs", "ipairs", "next", "select", "unpack",
    "type", "tostring", "tonumber", "pcall", "xpcall", "error", "assert",
    "setmetatable", "getmetatable", "rawget", "rawset", "rawequal"
}

# Local ESO reference sources used to build the fast RAM lookup dictionary
ESO_LIVE_SOURCE_DIR = r"Q:\Tools\!Spiele\TESO\EsoUI\esoui_src\live\esoui"
ESO_API_DOC_FILE = r"Q:\Tools\!Spiele\TESO\EsoUI\esoui_src\live\ESOUIDocumentation.txt"
ESO_EXTRA_GLOBALS_FILE = r"Q:\Tools\!Spiele\TESO\EsoUI\!!Parser\eso-api_base_Manual_NonGenerated.lua"

# Relative paths resolve against the project root (parent of src/)
ESO_UNDOCUMENTED_GLOBALS_FILE = "eso_undocumented_globals.lua"
ESO_XML_SCHEMA_FILE = r"_XSD\esoui_gui_xml.xsd"
ESO_BINDINGS_SCHEMA_FILE = r"_XSD\esobindings.xsd"

ESO_ADDONS_DIR = os.path.join(os.path.expanduser("~"), "Documents", "Elder Scrolls Online", "live", "AddOns")

# Authorized domains and MMOUI/ESOUI limits
ALLOWED_DOWNLOAD_DOMAINS = {"esoui.com", "://esoui.com", "mmoui.com"}
ESOUI_LATEST_MAX_ITEMS = 200
ESOUI_BATCH_CHUNK_SIZE = 10
# Safe character limit for a single ESOUI / MMOUI vBulletin add-on comment
ESOUI_COMMENT_MAX_CHARS = 9999


_ESOUI_BASE = "https://" + "www.esoui.com"
_ESOUI_WIKI_BASE = "https://" + "wiki.esoui.com"
ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX = _ESOUI_BASE + "/downloads/info"
ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX = _ESOUI_BASE + "/downloads/dl"
ESOUI_UPLOAD_RULES_URL = _ESOUI_BASE + "/forums/showthread.php?t=10790"
ESOUI_WIKI_EVENT_FILTERS_URL = _ESOUI_WIKI_BASE + "/AddFilterForEvent#Filter_Types"


# Local Ollama model configuration
OLLAMA_HOST = "http://localhost:11434"
MODEL_NAME = "qwen2.5-coder:14b"
AI_NUM_CTX = 32768
AI_TIMEOUT_SECONDS = 60

if os.name == "nt":
    os.system("")


class C:
    """ANSI color codes for clean console hierarchy."""
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
    """Resolves a config file path; relative paths are resolved against the project root directory."""
    if not file_setting or not isinstance(file_setting, str):
        return None
    if os.path.isabs(file_setting):
        return file_setting
    return os.path.join(get_project_root_dir(), file_setting)


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

