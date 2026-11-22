"""
Statische Python-Codeanalyse für ESO Lua-, Manifest- (.addon/.txt) und XML-Dateien.
"""

import json
import os
import re
import subprocess
import urllib.request
from collections import defaultdict
from datetime import datetime


def _fetch_esoui_wiki_text(url, accept_header="text/html,application/json,*/*;q=0.8", timeout_sec=6):
    """Fetches a page/API response from ://esoui.com via urllib with automatic curl fallback on HTTP 403."""
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": accept_header})
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        res = subprocess.run(
            ["curl", "-fsSL", "--max-time", str(timeout_sec + 2), "-A", ua, "-H", f"Accept: {accept_header}", url],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            check=True,
        )
        return res.stdout

from src.esoui_config import (
    C,
    ESOUI_WIKI_EVENT_FILTERS_URL,
    ESOUI_WIKI_LGB_EVENTS_URL,
    ESOUI_WIKI_LGB_PROTOCOLS_URL,
    ESO_BINDINGS_SCHEMA_FILE,
    ESO_XML_SCHEMA_FILE,
    EXTRACT_FOLDER,
    LIBSTUB_EXCLUDED_FUNCTIONS,
    LUA_KEYWORDS,
    LUA_STD_LIBS,
    WIKI_EVENT_FILTERS_FILE,
    WIKI_LGB_IDS_TXT_FILE,
    print_wrapped_tree_item,
    resolve_config_file_path,
)


from src.esoui_ram_index import (
    ESOUI_EVENT_HAS_UNIT_TAG,
    ESOUI_EVENT_PARAM_TYPES,
    ESOUI_GLOBAL_DEFINES,
    ESOUI_RAM_DICTIONARY,
    ESOUI_UNDOCUMENTED_SET,
    build_esoui_index_once,
    collect_dependency_globals,
    extract_resolved_xml_control_names,
    extract_virtual_controls_from_lua,
    get_current_api_version,
    is_index_built,
)

try:
    from lxml import etree as lxml_etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    lxml_etree = None

XML_SCHEMA_CACHE = {}
XML_SCHEMA_WARNED = set()

BATCH_LEAK_TRACKER = defaultdict(list)
BATCH_BEST_PRACTICE_TRACKER = defaultdict(list)

WIKI_EVENT_FILTERS_CACHE_FILE = WIKI_EVENT_FILTERS_FILE
_WIKI_EVENT_FILTER_SESSION_LOADED = False
_WIKI_DYNAMIC_EVENT_RULES = {}


# ==============================================================================
# WARTUNGSHINWEIS / HOW TO ADD NEW ESO EVENT FILTERS
# ==============================================================================
# 1. AUTOMATISCHER WIKI-SYNC (1x pro Session):
#    Beim ersten Lua-Check einer Session ruft `_sync_wiki_event_filters_once()`
#    einmalig `ESOUI_WIKI_EVENT_FILTERS_URL` (aus `src/esoui_config.py`) ab,
#    parst die Tabelle `Filter Types` (Spalte 1: REGISTER_FILTER_*, Spalte 2:
#    EVENT_*) und merkt sich neue Zuordnungen für die gesamte Session (sowie
#    als Backup in `Cache/wiki_event_filters_cache.json` für Offline-Läufe).
#
# 2. MANUELLE ERGÄNZUNG (Fallback & präzise Callback-Parameter-Prüfung):
#    Falls ein neues Event im Wiki noch nicht dokumentiert ist oder du eine
#    eigene BBCode-Überschrift (`rule_title`) festlegen möchtest:
#    a) Trage das Event in `EVENT_FILTER_RULES` ein:
#       "<EVENT_NAME>": {
#           "filters": {"<REGISTER_FILTER_1>", "<REGISTER_FILTER_2>"},
#           "rule_title": "Use event filters for <thema> instead of checking code slower in lua",
#       }
#    b) Falls geprüft werden soll, ob der Callback denselben Parameter trotz
#       aktivem Filter noch einmal per `if param == ...` im Lua-Code prüft:
#       Trage in `FILTER_TYPE_PARAM_INDEX` das Tupel
#       ("<EVENT_NAME>", "<REGISTER_FILTER_X>"): <1-basierter Parameter-Index>
#       ein. Den exakten Index findest du in `ESOUIDocumentation.txt` bei der
#       Signatur des Events (Parameter 1 nach `eventCode` = Index 1, z. B. bei
#       `EVENT_INVENTORY_SINGLE_SLOT_UPDATE(eventCode, bagId, slotIndex, ...)`
#       ist `bagId` = 1, `isNewItem` = 3, `inventoryUpdateReason` = 5).
#    c) Hinweis zu generischen Wiki-Regeln:
#       - "Any event with a unitTag argument" -> wird automatisch über
#         `ESOUI_EVENT_HAS_UNIT_TAG` aus `ESOUIDocumentation.txt` erkannt.
#       - "Any" (`REGISTER_FILTER_IS_IN_GAMEPAD_PREFERRED_MODE`) -> wird über
#         `ESOUI_EVENT_HAS_GAMEPAD_MODE` aus `ESOUIDocumentation.txt` erkannt.
# ==============================================================================
EVENT_FILTER_RULES = {
    "EVENT_ABILITY_COOLDOWN_UPDATED": {
        "filters": {"REGISTER_FILTER_ABILITY_ID"},
        "rule_title": "Use event filters for ability cooldowns instead of checking code slower in lua",
    },
    "EVENT_COMBAT_EVENT": {
        "filters": {
            "REGISTER_FILTER_ABILITY_ID",
            "REGISTER_FILTER_COMBAT_RESULT",
            "REGISTER_FILTER_IS_ERROR",
            "REGISTER_FILTER_POWER_TYPE",
            "REGISTER_FILTER_SOURCE_COMBAT_UNIT_TYPE",
            "REGISTER_FILTER_TARGET_COMBAT_UNIT_TYPE",
            "REGISTER_FILTER_VIBRATION_FILTER",
        },
        "rule_title": "Use event filters for combat instead of checking code slower in lua",
    },
    "EVENT_EFFECT_CHANGED": {
        "filters": {
            "REGISTER_FILTER_ABILITY_ID",
            "REGISTER_FILTER_SOURCE_COMBAT_UNIT_TYPE",
            "REGISTER_FILTER_UNIT_TAG",
            "REGISTER_FILTER_UNIT_TAG_PREFIX",
        },
        "rule_title": "Use event filters for effect changes instead of checking code slower in lua",
    },
    "EVENT_INVENTORY_SINGLE_SLOT_UPDATE": {
        "filters": {
            "REGISTER_FILTER_BAG_ID",
            "REGISTER_FILTER_INVENTORY_UPDATE_REASON",
            "REGISTER_FILTER_IS_NEW_ITEM",
        },
        "rule_title": "Use event filters for inventory items instead of checking code slower in lua",
    },
    "EVENT_POWER_UPDATE": {
        "filters": {
            "REGISTER_FILTER_POWER_TYPE",
            "REGISTER_FILTER_UNIT_TAG",
            "REGISTER_FILTER_UNIT_TAG_PREFIX",
        },
        "rule_title": "Use event filters for power updates instead of checking code slower in lua",
    },
    "EVENT_INTERFACE_SETTING_CHANGED": {
        "filters": {"REGISTER_FILTER_SETTING_SYSTEM_TYPE"},
        "rule_title": "Use event filters for interface settings instead of checking code slower in lua",
    },
}

FILTER_TYPE_PARAM_INDEX = {
    ("EVENT_INVENTORY_SINGLE_SLOT_UPDATE", "REGISTER_FILTER_BAG_ID"): 1,
    ("EVENT_INVENTORY_SINGLE_SLOT_UPDATE", "REGISTER_FILTER_IS_NEW_ITEM"): 3,
    ("EVENT_INVENTORY_SINGLE_SLOT_UPDATE", "REGISTER_FILTER_INVENTORY_UPDATE_REASON"): 5,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_COMBAT_RESULT"): 1,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_IS_ERROR"): 2,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_POWER_TYPE"): 11,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_SOURCE_COMBAT_UNIT_TYPE"): 8,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_TARGET_COMBAT_UNIT_TYPE"): 10,
    ("EVENT_COMBAT_EVENT", "REGISTER_FILTER_ABILITY_ID"): 16,
    ("EVENT_EFFECT_CHANGED", "REGISTER_FILTER_UNIT_TAG"): 6,
    ("EVENT_EFFECT_CHANGED", "REGISTER_FILTER_UNIT_TAG_PREFIX"): 6,
    ("EVENT_EFFECT_CHANGED", "REGISTER_FILTER_SOURCE_COMBAT_UNIT_TYPE"): 13,
    ("EVENT_EFFECT_CHANGED", "REGISTER_FILTER_ABILITY_ID"): 15,
    ("EVENT_POWER_UPDATE", "REGISTER_FILTER_UNIT_TAG"): 1,
    ("EVENT_POWER_UPDATE", "REGISTER_FILTER_UNIT_TAG_PREFIX"): 1,
    ("EVENT_POWER_UPDATE", "REGISTER_FILTER_POWER_TYPE"): 3,
    ("EVENT_ABILITY_COOLDOWN_UPDATED", "REGISTER_FILTER_ABILITY_ID"): 1,
    ("EVENT_INTERFACE_SETTING_CHANGED", "REGISTER_FILTER_SETTING_SYSTEM_TYPE"): 1,
}


def _parse_wiki_event_filter_html(html_text):
    """Parst REGISTER_FILTER_* -> EVENT_* Zuordnungen aus der ESOUI-Wiki-Tabelle."""
    parsed = defaultdict(set)
    for row_html in re.findall(r"<tr\b[^>]*>(.*?)</tr>", html_text, flags=re.DOTALL | re.IGNORECASE):
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", row_html, flags=re.DOTALL | re.IGNORECASE)
        if len(cells) < 2:
            continue
        col1 = re.sub(r"<[^>]+>", " ", cells[0]).strip()
        col2 = re.sub(r"<[^>]+>", " ", cells[1]).strip()
        f_match = re.search(r"\b(REGISTER_FILTER_[A-Z0-9_]+)\b", col1)
        if not f_match:
            continue
        filter_const = f_match.group(1)
        if filter_const in ("REGISTER_FILTER_INVALID", "REGISTER_FILTER_IS_IN_GAMEPAD_PREFERRED_MODE"):
            continue
        for ev_name in re.findall(r"\b(EVENT_[A-Z0-9_]+)\b", col2):
            parsed[ev_name].add(filter_const)
    return {ev: sorted(flts) for ev, flts in parsed.items()}



def _sync_wiki_event_filters_once():
    """Lädt die ESOUI-Wiki-Filtertabelle 1x pro Session (mit lokalem Disk-Fallback)."""
    global _WIKI_EVENT_FILTER_SESSION_LOADED
    if _WIKI_EVENT_FILTER_SESSION_LOADED:
        return
    _WIKI_EVENT_FILTER_SESSION_LOADED = True

    fetch_url = next(iter(ESOUI_WIKI_EVENT_FILTERS_URL.split("#", 1)))
    mapping = {}
    try:
        html_body = _fetch_esoui_wiki_text(fetch_url, accept_header="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", timeout_sec=5)
        mapping = _parse_wiki_event_filter_html(html_body)

        if mapping:
            try:
                os.makedirs(os.path.dirname(WIKI_EVENT_FILTERS_CACHE_FILE), exist_ok=True)
                with open(WIKI_EVENT_FILTERS_CACHE_FILE, "w", encoding="utf-8") as cf:
                    json.dump(mapping, cf, indent=2, sort_keys=True)
            except OSError:
                pass
    except Exception:
        if os.path.isfile(WIKI_EVENT_FILTERS_CACHE_FILE):
            try:
                with open(WIKI_EVENT_FILTERS_CACHE_FILE, "r", encoding="utf-8") as cf:
                    loaded = json.load(cf)
                if isinstance(loaded, dict):
                    mapping = loaded
            except Exception:
                pass

    for ev_name, flt_list in mapping.items():
        if not isinstance(flt_list, list) or not flt_list:
            continue
        cleaned_flts = [
            f for f in flt_list
            if f not in ("REGISTER_FILTER_INVALID", "REGISTER_FILTER_IS_IN_GAMEPAD_PREFERRED_MODE")
        ]
        if not cleaned_flts:
            continue
        if ev_name in EVENT_FILTER_RULES:
            EVENT_FILTER_RULES[ev_name]["filters"].update(cleaned_flts)
        else:
            topic = ev_name.removeprefix("EVENT_").replace("_", " ").lower()
            _WIKI_DYNAMIC_EVENT_RULES[ev_name] = {
                "filters": set(cleaned_flts),
                "rule_title": f"Use event filters for {topic} instead of checking code slower in lua",
            }


WIKI_LGB_IDS_RAW_TXT_FILE = WIKI_LGB_IDS_TXT_FILE
_WIKI_LGB_SESSION_LOADED = False
_WIKI_LGB_CACHE = {"protocols": {}, "events": {}}
_WIKI_LGB_FETCH_ERROR = None

def get_wiki_lgb_fetch_error():
    """Returns '[Error] Access to ESOUI Wiki LibGroupBroadcast failed' if live wiki fetch failed, else None."""
    return _WIKI_LGB_FETCH_ERROR



def _parse_wiki_lgb_ids_html(html_text):
    """Parst Protocols- und Events-Tabellen (id -> addon/reservation, inkl. ID-Ranges) von LibGroupBroadcast_IDs."""
    protocols = {}
    events = {}
    current_kind = None
    for token in re.findall(r"(<h[1-6]\b[^>]*>.*?</h[1-6]>|<tr\b[^>]*>.*?</tr>)", html_text, flags=re.DOTALL | re.IGNORECASE):
        if token.lower().startswith("<h"):
            plain_h = re.sub(r"<[^>]+>", " ", token).strip().lower()
            if "protocol" in plain_h:
                current_kind = "protocols"
            elif "event" in plain_h:
                current_kind = "events"
            continue
        cells = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", token, flags=re.DOTALL | re.IGNORECASE)
        if not cells:
            continue
        cleaned_cells = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip() for c in cells]
        col0 = cleaned_cells[0]
        id_range = []
        addon_info = ""

        range_col0_m = re.match(r"^(\d+)\s*-\s*(\d+)$", col0)
        inline_range_m = re.match(r"^(\d+)\s*-\s*(\d+)\s+(.+)$", col0)
        inline_single_m = re.match(r"^(\d+)\s+(.+)$", col0)

        if col0.isdigit():
            id_range = [int(col0)]
            if len(cleaned_cells) >= 4 and cleaned_cells[3]:
                addon_info = cleaned_cells[3]
            elif len(cleaned_cells) >= 2 and cleaned_cells[1]:
                addon_info = cleaned_cells[1]
        elif range_col0_m:
            lo, hi = int(range_col0_m.group(1)), int(range_col0_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            if len(cleaned_cells) >= 4 and cleaned_cells[3]:
                addon_info = cleaned_cells[3]
            elif len(cleaned_cells) >= 2 and cleaned_cells[1]:
                addon_info = cleaned_cells[1]
        elif inline_range_m:
            lo, hi = int(inline_range_m.group(1)), int(inline_range_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            addon_info = inline_range_m.group(3).strip()
        elif inline_single_m:
            id_range = [int(inline_single_m.group(1))]
            addon_info = inline_single_m.group(2).strip()

        if not id_range or not addon_info:
            continue

        target_map = events if current_kind == "events" else protocols
        for nid in id_range:
            if current_kind in ("protocols", "events"):
                target_map[nid] = addon_info
            else:
                if nid not in protocols:
                    protocols[nid] = addon_info
                else:
                    events[nid] = addon_info
    return {"protocols": protocols, "events": events}



def _parse_wiki_lgb_ids_wikitext(wikitext):
    """Parst MediaWiki-Wikitext von LibGroupBroadcast_IDs zeilenweise (CRLF-sicher, inkl. colspan & ID-Ranges)."""
    protocols = {}
    events = {}
    current_kind = None
    cells = []

    def _pick_addon_from_cells(cell_list):
        c3 = next(iter(cell_list[3:4]), "")
        c1 = next(iter(cell_list[1:2]), "")
        if c3 and c3 != "-" and c3.lower() != "work in progress":
            return c3
        if c1 and c1 != "-":
            return c1
        return ""

    def _flush_row(row_cells, kind):
        if not row_cells or kind not in ("protocols", "events"):
            return
        col0 = next(iter(row_cells), "")
        id_range = []
        addon_info = ""

        range_col0_m = re.match(r"^(\d+)\s*-\s*(\d+)$", col0)
        inline_range_m = re.match(r"^(\d+)\s*-\s*(\d+)\s+(.+)$", col0)
        inline_single_m = re.match(r"^(\d+)\s+(.+)$", col0)

        if col0.isdigit():
            id_range = [int(col0)]
            addon_info = _pick_addon_from_cells(row_cells)
        elif range_col0_m:
            lo, hi = int(range_col0_m.group(1)), int(range_col0_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            addon_info = _pick_addon_from_cells(row_cells)
        elif inline_range_m:
            lo, hi = int(inline_range_m.group(1)), int(inline_range_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            addon_info = inline_range_m.group(3).strip()
        elif inline_single_m:
            id_range = [int(inline_single_m.group(1))]
            addon_info = inline_single_m.group(2).strip()

        if not id_range or not addon_info or addon_info == "-":
            return

        target_map = events if kind == "events" else protocols
        for nid in id_range:
            target_map[nid] = addon_info

    for raw_ln in wikitext.splitlines():
        s = raw_ln.strip()
        if not s:
            continue
        hm = re.match(r"^==+\s*([^=]+?)\s*==+", s)
        if hm:
            _flush_row(cells, current_kind)
            cells = []
            h_low = hm.group(1).strip().lower()
            if "handler" in h_low:
                current_kind = None
            elif "protocol" in h_low:
                current_kind = "protocols"
            elif "event" in h_low:
                current_kind = "events"
            continue

        if s.startswith("|-") or s.startswith("|}") or s.startswith("{|"):
            _flush_row(cells, current_kind)
            cells = []
            continue

        if current_kind not in ("protocols", "events") or not s.startswith("|"):
            continue

        row_body = s[1:]
        for part in row_body.split("||"):
            if "|" in part and re.match(r"^\s*(?:colspan|rowspan|style|class|align)\b", part, flags=re.IGNORECASE):
                part = part.split("|", 1)[-1]
            clean_cell = re.sub(r"'{2,}", "", part)
            clean_cell = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", clean_cell)
            clean_cell = re.sub(r"\[\[([^\]]+)\]\]", r"\1", clean_cell)
            clean_cell = re.sub(r"<[^>]+>", " ", clean_cell)
            clean_cell = re.sub(r"\s+", " ", clean_cell).strip()
            cells.append(clean_cell)

    _flush_row(cells, current_kind)
    return {"protocols": protocols, "events": events}



def _parse_wiki_lgb_ids_plain_table(raw_text):

    """Parst kopierte Wiki-Tabellen (Tab-getrennt oder '200 reserved for ...') als Fallback."""
    protocols = {}
    events = {}
    current_kind = None
    for raw_ln in raw_text.splitlines():
        line = raw_ln.strip()
        if not line:
            continue
        low = line.lower()
        if "protocol" in low and not line[0].isdigit():
            current_kind = "protocols"
            continue
        if ("custom event" in low or "event id" in low or low == "events") and not line[0].isdigit():
            current_kind = "events"
            continue

        parts = [p.strip() for p in line.split("\t") if p.strip()]
        col0 = parts[0] if parts else line
        id_range = []
        addon_info = ""

        range_m = re.match(r"^(\d+)\s*-\s*(\d+)$", col0)
        inline_range_m = re.match(r"^(\d+)\s*-\s*(\d+)\s+(.+)$", line)
        inline_single_m = re.match(r"^(\d+)\s+(.+)$", line)

        if col0.isdigit():
            id_range = [int(col0)]
            if len(parts) >= 4 and parts[3] != "-":
                addon_info = parts[3]
            elif len(parts) >= 2 and parts[1] != "-":
                addon_info = parts[1]
        elif range_m:
            lo, hi = int(range_m.group(1)), int(range_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            if len(parts) >= 4 and parts[3] != "-":
                addon_info = parts[3]
            elif len(parts) >= 2 and parts[1] != "-":
                addon_info = parts[1]
        elif inline_range_m:
            lo, hi = int(inline_range_m.group(1)), int(inline_range_m.group(2))
            if 0 <= lo <= hi <= 2048:
                id_range = list(range(lo, hi + 1))
            addon_info = inline_range_m.group(3).strip()
        elif inline_single_m:
            id_range = [int(inline_single_m.group(1))]
            addon_info = inline_single_m.group(2).strip()

        if not id_range or not addon_info or addon_info == "-":
            continue

        target_map = events if current_kind == "events" else protocols
        for nid in id_range:
            if current_kind in ("protocols", "events"):
                target_map[nid] = addon_info
            else:
                if nid not in protocols:
                    protocols[nid] = addon_info
                else:
                    events[nid] = addon_info

    return {"protocols": protocols, "events": events}


def _sync_wiki_lgb_ids_once():
    """Lädt LibGroupBroadcast Protocol- & Event-IDs 1x pro Session mit Fallback auf WIKI_LGB_IDS_TXT_FILE."""
    global _WIKI_LGB_SESSION_LOADED, _WIKI_LGB_FETCH_ERROR
    if _WIKI_LGB_SESSION_LOADED:
        return
    _WIKI_LGB_SESSION_LOADED = True

    base_page_url = next(iter(ESOUI_WIKI_LGB_PROTOCOLS_URL.split("#", 1)))
    wiki_root = base_page_url.rsplit("/", 1)[0]
    api_url = f"{wiki_root}/api.php?action=parse&page=LibGroupBroadcast_IDs&prop=wikitext&format=json"

    parsed_data = {}
    try:
        raw_json = _fetch_esoui_wiki_text(api_url, accept_header="application/json,*/*;q=0.8", timeout_sec=6)
        payload = json.loads(raw_json)
        wikitext = ((payload.get("parse") or {}).get("wikitext") or {}).get("*") or ""
        if wikitext:
            parsed_data = _parse_wiki_lgb_ids_wikitext(wikitext)
    except Exception:
        pass

    if not parsed_data.get("protocols") and not parsed_data.get("events"):
        try:
            html_body = _fetch_esoui_wiki_text(base_page_url, accept_header="text/html,application/xhtml+xml,*/*;q=0.8", timeout_sec=6)
            parsed_data = _parse_wiki_lgb_ids_html(html_body)
        except Exception:
            pass

    if parsed_data.get("protocols") or parsed_data.get("events"):
        _WIKI_LGB_FETCH_ERROR = None
    else:
        _WIKI_LGB_FETCH_ERROR = "[Error] Access to ESOUI Wiki LibGroupBroadcast failed"
        print(f"    │     {C.RED}{_WIKI_LGB_FETCH_ERROR}{C.RESET}")

        txt_path = resolve_config_file_path(WIKI_LGB_IDS_RAW_TXT_FILE) or WIKI_LGB_IDS_RAW_TXT_FILE
        if os.path.isfile(txt_path):
            try:
                with open(txt_path, "r", encoding="utf-8", errors="ignore") as tf:
                    local_txt = tf.read()
                parsed_data = _parse_wiki_lgb_ids_wikitext(local_txt)
                if not parsed_data.get("protocols") and not parsed_data.get("events"):
                    parsed_data = _parse_wiki_lgb_ids_plain_table(local_txt)
            except Exception:
                pass

    _WIKI_LGB_CACHE["protocols"] = dict(parsed_data.get("protocols") or {})
    _WIKI_LGB_CACHE["events"] = dict(parsed_data.get("events") or {})


def _check_lua_libgroupbroadcast_ids(file_name, content, active_extract_dir, addon_ctx, lua_issues):
    """Prüft DeclareProtocol- und DeclareCustomEvent-IDs gegen das ESOUI-Wiki, wenn LibGroupBroadcast genutzt wird."""
    clean_code = strip_lua_comments_preserve_lines(content)
    if "LibGroupBroadcast" not in clean_code and "DeclareProtocol" not in clean_code and "DeclareCustomEvent" not in clean_code:
        return

    # Addon-Namen & Dependencies aus den Manifesten ermitteln
    addon_names_lower = set()
    has_lgb_dep = "LibGroupBroadcast" in clean_code
    if active_extract_dir and os.path.isdir(active_extract_dir):
        for m_file in (addon_ctx.get("root_addon_manifests") or []) + (addon_ctx.get("root_txt_manifests") or []):
            addon_names_lower.add(os.path.splitext(m_file)[0].lower())
        for root, _, files in os.walk(active_extract_dir):
            for fn in files:
                if fn.lower().endswith((".addon", ".txt")):
                    try:
                        with open(os.path.join(root, fn), "r", encoding="utf-8", errors="ignore") as mf:
                            mf_txt = mf.read()
                        if re.search(r"^\s*##\s*(?:Title|AddOnVersion)\s*:", mf_txt, flags=re.MULTILINE | re.IGNORECASE):
                            addon_names_lower.add(os.path.splitext(fn)[0].lower())
                            if re.search(r"^\s*##\s*(?:Optional|PC|Console)?DependsOn\s*:.*\bLibGroupBroadcast\b", mf_txt, flags=re.MULTILINE | re.IGNORECASE):
                                has_lgb_dep = True
                    except Exception:
                        pass

    if not addon_names_lower:
        parts = file_name.replace("\\", "/").split("/")
        if len(parts) > 1:
            addon_names_lower.add(parts[0].lower())

    if not has_lgb_dep:
        return

    # Numerische Konstanten im gesamten Addon sammeln (z. B. local PROTOCOL_ID = 200)
    num_consts = {}
    if active_extract_dir and os.path.isdir(active_extract_dir):
        for root, _, files in os.walk(active_extract_dir):
            for fn in files:
                if fn.lower().endswith(".lua"):
                    try:
                        with open(os.path.join(root, fn), "r", encoding="utf-8", errors="ignore") as lf:
                            c_txt = strip_lua_comments_preserve_lines(lf.read())
                        for cm in re.finditer(r"\b(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\b", c_txt):
                            num_consts[cm.group(1)] = int(cm.group(2))
                    except Exception:
                        pass
    for cm in re.finditer(r"\b(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(\d+)\b", clean_code):
        num_consts[cm.group(1)] = int(cm.group(2))

    lgb_aliases = {"LibGroupBroadcast"}
    for am in re.finditer(r"\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*LibGroupBroadcast\b", clean_code):
        lgb_aliases.add(am.group(1))

    handler_vars = set()
    for alias in lgb_aliases:
        for hm in re.finditer(r"\b(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*" + re.escape(alias) + r"\s*:\s*RegisterHandler\s*\(", clean_code):
            handler_vars.add(hm.group(1))

    if not handler_vars:
        return

    def _resolve_id_expr(expr):
        s = expr.strip()
        if s.isdigit():
            return int(s)
        return num_consts.get(s)

    protocols_found = []
    events_found = []
    for h_var in handler_vars:
        for pm in re.finditer(r"\b" + re.escape(h_var) + r"\s*:\s*DeclareProtocol\s*\(", clean_code):
            args_raw, _ = _extract_balanced_call_args(clean_code, pm.end() - 1)
            if args_raw:
                args = _split_top_level_lua_args(args_raw)
                if args:
                    pid = _resolve_id_expr(args[0])
                    if pid is not None:
                        ln = clean_code.count("\n", 0, pm.start()) + 1
                        protocols_found.append((ln, pid))
        for em in re.finditer(r"\b" + re.escape(h_var) + r"\s*:\s*DeclareCustomEvent\s*\(", clean_code):
            args_raw, _ = _extract_balanced_call_args(clean_code, em.end() - 1)
            if args_raw:
                args = _split_top_level_lua_args(args_raw)
                if args:
                    eid = _resolve_id_expr(args[0])
                    if eid is not None:
                        ln = clean_code.count("\n", 0, em.start()) + 1
                        events_found.append((ln, eid))


    if not protocols_found and not events_found:
        return

    _sync_wiki_lgb_ids_once()
    wiki_protos = _WIKI_LGB_CACHE.get("protocols") or {}
    wiki_events = _WIKI_LGB_CACHE.get("events") or {}

    def _is_owner_match(wiki_addon):
        if not wiki_addon or wiki_addon == "?":
            return False
        w_low = wiki_addon.strip().lower()
        return any(w_low == an or w_low.startswith(an + " ") or an in re.split(r"[^a-z0-9_-]+", w_low) for an in addon_names_lower)

    for ln, pid in sorted(protocols_found, key=lambda x: x):
        p_wiki = wiki_protos.get(pid, "?")
        if not _is_owner_match(p_wiki):
            desc = f"Protocol ID {pid} (Wiki AddOn: {p_wiki})"
            lua_issues.append(f"LibGroupBroadcast Protocoll [{pid}] conflict (line {ln}): ({desc})")

    for ln, eid in sorted(events_found, key=lambda x: x):
        e_wiki = wiki_events.get(eid, "?")
        if not _is_owner_match(e_wiki):
            desc = f"Event ID {eid} (Wiki AddOn: {e_wiki})"
            lua_issues.append(f"LibGroupBroadcast Event [{eid}] conflict (line {ln}): ({desc})")
        
def strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False):
    """Single-pass Lua lexer stripping comments and optionally strings while keeping line numbers."""
    if not isinstance(content, str) or not content:
        return ""

    content = content.lstrip("\ufeff")
    out = []
    n = len(content)
    i = 0

    def _match_long_bracket(pos):
        if pos >= n or content[pos] != '[':
            return None
        j = pos + 1
        while j < n and content[j] == '=':
            j += 1
        if j < n and content[j] == '[':
            return j - (pos + 1), j + 1
        return None

    while i < n:
        ch = content[i]
        if ch == '-' and i + 1 < n and content[i + 1] == '-':
            lb = _match_long_bracket(i + 2)
            if lb is not None:
                eq_count, body_start = lb
                close_seq = ']' + ('=' * eq_count) + ']'
                end_pos = content.find(close_seq, body_start)
                if end_pos == -1:
                    out.append('\n' * content[i:].count('\n'))
                    break
                end_pos += len(close_seq)
                out.append('\n' * content[i:end_pos].count('\n'))
                i = end_pos
                continue
            nl_pos = content.find('\n', i + 2)
            if nl_pos == -1:
                break
            out.append('\n')
            i = nl_pos + 1
            continue

        if ch == '[':
            lb = _match_long_bracket(i)
            if lb is not None:
                eq_count, body_start = lb
                close_seq = ']' + ('=' * eq_count) + ']'
                end_pos = content.find(close_seq, body_start)
                if end_pos == -1:
                    out.append(content[i:] if keep_strings else ('""' + '\n' * content[i:].count('\n')))
                    break
                end_pos += len(close_seq)
                out.append(content[i:end_pos] if keep_strings else ('""' + '\n' * content[i:end_pos].count('\n')))
                i = end_pos
                continue
        if ch in ('"', "'"):
            quote = ch
            j = i + 1
            while j < n:
                c = content[j]
                if c == '\\':
                    j += 2
                    continue
                if c == quote:
                    j += 1
                    break
                if c == '\n':
                    break
                j += 1
            segment = content[i:j]
            out.append(segment if keep_strings else (quote + quote + '\n' * segment.count('\n')))
            i = j
            continue

        out.append(ch)
        i += 1

    return "".join(out)


def find_uncommented_libstub_hits(content):
    """Returns [(line_no, raw_line), ...] for active LibStub references outside LIBSTUB_EXCLUDED_FUNCTIONS."""
    clean_with_strings = strip_lua_comments_preserve_lines(content)
    code_only = strip_lua_strings_preserve_lines(clean_with_strings)
    raw_lines = content.splitlines()

    excluded_exact = {fn.strip() for fn in LIBSTUB_EXCLUDED_FUNCTIONS if fn and fn.strip()}
    excluded_lower = {fn.lower() for fn in excluded_exact}

    # Resolve local namespace aliases (e.g. local NAME = "LibCodesCommonCode"; local Lib = {}; _G[NAME] = Lib)
    local_str_consts = dict(re.findall(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\']([^"\']+)["\']', clean_with_strings))
    ns_aliases = {}
    for m_g in re.finditer(r'_G\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]\s*=\s*([A-Za-z_][A-Za-z0-9_]*)', clean_with_strings):
        ns_aliases[m_g.group(2)] = m_g.group(1)
    for m_gv in re.finditer(r'_G\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]\s*=\s*([A-Za-z_][A-Za-z0-9_]*)', clean_with_strings):
        if m_gv.group(1) in local_str_consts:
            ns_aliases[m_gv.group(2)] = local_str_consts[m_gv.group(1)]
    for m_la in re.finditer(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)(?!\s*[.:\[(])\b', code_only):
        lhs, rhs = m_la.group(1), m_la.group(2)
        if rhs in ns_aliases:
            ns_aliases[lhs] = ns_aliases[rhs]
        elif rhs not in LUA_KEYWORDS:
            ns_aliases.setdefault(lhs, rhs)

    def _is_excluded_func(full_func_name):
        if not excluded_lower:
            return False
        short_fn = full_func_name.split(".")[-1].split(":")[-1]
        candidates = {full_func_name, short_fn}
        if "." in full_func_name or ":" in full_func_name:
            sep = ":" if ":" in full_func_name else "."
            owner, member = full_func_name.split(sep, 1)
            resolved_owner = ns_aliases.get(owner, owner)
            candidates.add(f"{resolved_owner}.{member}")
            candidates.add(f"{resolved_owner}:{member}")
        return any(c in excluded_exact or c.lower() in excluded_lower for c in candidates)

    hits = []
    rx = re.compile(r'\blibstub\b', flags=re.IGNORECASE)
    fn_def_rx = re.compile(r'\b(?:local\s+)?function\s+([A-Za-z_][A-Za-z0-9_.:]*)\s*\(')
    token_rx = re.compile(r'\b(function|if|for|while|repeat|do)\b|\b(end|until)\b')
    block_stack = []

    for idx, line in enumerate(code_only.splitlines(), 1):
        fn_m = fn_def_rx.search(line)
        fn_name_on_line = fn_m.group(1) if fn_m else None
        norm_line = re.sub(r'\b(?:for|while)\b[^;\n]*?\bdo\b', 'for', line)

        tokens = list(token_rx.finditer(norm_line))
        # Check LibStub either inside an already-excluded function or on the excluded function header itself
        in_excluded_fn = any(is_excl for _, is_excl in block_stack) or (
            fn_name_on_line is not None and _is_excluded_func(fn_name_on_line)
        )
        if not in_excluded_fn and rx.search(line):
            orig = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
            hits.append((idx, orig))

        first_fn_consumed = False
        for tm in tokens:
            b_open, b_close = tm.groups()
            if b_open:
                if b_open == "function" and not first_fn_consumed and fn_name_on_line is not None:
                    first_fn_consumed = True
                    block_stack.append(("function", _is_excluded_func(fn_name_on_line)))
                else:
                    block_stack.append((b_open, False))
            elif b_close and block_stack:
                block_stack.pop()

    return hits

def check_for_uncommented_libstub(content):
    return bool(find_uncommented_libstub_hits(content))


def strip_lua_comments_preserve_lines(content):
    return strip_lua_comments_and_strings_preserve_lines(content, keep_strings=True)


def strip_lua_strings_preserve_lines(content):
    return strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)
_PUBLIC_API_FUNC_PREFIXES = (
    "get", "set", "is", "has", "can", "does", "should",
    "toggle", "enable", "disable", "register", "unregister",
    "add", "remove", "create", "delete", "clear", "reset",
    "refresh", "update", "open", "close", "show", "hide",
)

_NON_FUNC_RHS_TOKENS = {
    "nil", "true", "false", "and", "or", "not", "end",
    "function", "if", "then", "else", "elseif", "for", "while", "do", "return",
}


def _is_public_api_method_name(member_name):
    """Returns True if member_name starts with an API verb in CamelCase or snake_case (e.g. getData, GetData, get_data)."""
    if not member_name or len(member_name) < 3:
        return False
    low = member_name.lower()
    for pref in _PUBLIC_API_FUNC_PREFIXES:
        if low.startswith(pref) and len(member_name) > len(pref):
            next_ch = member_name[len(pref)]
            if next_ch.isupper() or next_ch == "_":
                return True
    return False


def _detect_public_api_functions_on_globals(lua_texts_by_rel_path, all_global_tables):
    """Detects whether any global addon table exposes API-prefixed methods (direct def, local alias ref, or table literal)."""
    if not all_global_tables:
        return False
    gt_alt = "|".join(re.escape(gt) for gt in sorted(all_global_tables, key=len, reverse=True) if gt)
    if not gt_alt:
        return False

    rx_direct_def = re.compile(rf'\bfunction\s+(?:{gt_alt})\s*[.:]\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(')
    rx_member_assign = re.compile(
        rf'\b(?:{gt_alt})(?:\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)|\s*\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\])\s*=\s*(?:(function)\b|([A-Za-z_][A-Za-z0-9_.:]*))'
    )
    rx_table_init = re.compile(rf'(?<!local\s)\b(?:{gt_alt})\s*=\s*\{{')
    rx_field_assign = re.compile(
        r'(?:(?<!\[)\b([A-Za-z_][A-Za-z0-9_]*)|\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\])\s*=\s*(?:(function)\b|([A-Za-z_][A-Za-z0-9_.:]*))'
    )

    for rel_path, lua_clean in lua_texts_by_rel_path:
        rel_parts = [p.lower() for p in rel_path.replace("\\", "/").split("/")]
        if any(p in ("lib", "libs", "libraries") for p in rel_parts):
            continue
        lua_no_str = strip_lua_strings_preserve_lines(lua_clean)

        for m in rx_direct_def.finditer(lua_no_str):
            if _is_public_api_method_name(m.group(1)):
                return True

        for m in rx_member_assign.finditer(lua_clean):
            mem_name = m.group(1) or m.group(2)
            is_fn_lit = bool(m.group(3))
            rhs_ident = m.group(4) or ""
            if not _is_public_api_method_name(mem_name):
                continue
            if is_fn_lit or (rhs_ident and rhs_ident not in _NON_FUNC_RHS_TOKENS):
                return True

        for tm in rx_table_init.finditer(lua_clean):
            brace_pos = tm.end() - 1
            depth = 0
            in_q = None
            esc = False
            end_brace = -1
            for idx in range(brace_pos, len(lua_clean)):
                ch = lua_clean[idx]
                if in_q:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == in_q:
                        in_q = None
                    continue
                if ch in ('"', "'"):
                    in_q = ch
                elif ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end_brace = idx
                        break
            if end_brace > brace_pos:
                tbl_body = lua_clean[brace_pos + 1:end_brace]
                for fm in rx_field_assign.finditer(tbl_body):
                    f_name = fm.group(1) or fm.group(2)
                    is_fn_lit = bool(fm.group(3))
                    rhs_ident = fm.group(4) or ""
                    if not _is_public_api_method_name(f_name):
                        continue
                    if is_fn_lit or (rhs_ident and rhs_ident not in _NON_FUNC_RHS_TOKENS):
                        return True

    return False


def collect_addon_context(extract_dir):
    """Collects Bindings.xml presence, XML content, global tables, SavedVariables, and manifests."""
    has_bindings_xml = False
    is_library = False
    xml_combined_parts = []
    all_global_tables = set()
    dynamic_globals = set()
    saved_variables = set()
    root_addon_manifests = []
    root_txt_manifests = []

    if extract_dir and os.path.exists(extract_dir):
        top_entries = os.listdir(extract_dir)
        top_dirs = [d for d in top_entries if os.path.isdir(os.path.join(extract_dir, d))]
        top_files = [f for f in top_entries if os.path.isfile(os.path.join(extract_dir, f))]
        manifest_root_dir = os.path.join(extract_dir, next(iter(top_dirs))) if (len(top_dirs) == 1 and not top_files) else extract_dir

        for f in os.listdir(manifest_root_dir):
            full_p = os.path.join(manifest_root_dir, f)
            if os.path.isfile(full_p):
                low = f.lower()
                if low.endswith(".addon"):
                    root_addon_manifests.append(f)
                elif low.endswith(".txt"):
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as mf:
                            head_text = mf.read(2048)
                        if re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', head_text, flags=re.MULTILINE | re.IGNORECASE):
                            root_txt_manifests.append(f)
                    except Exception:
                        pass

        bundled_sub_addons = set()
        global_tables_by_file = defaultdict(set)
        lua_texts_for_dyn_g = []
        lua_file_total = 0
        own_lua_file_total = 0
        for root, _, files in os.walk(extract_dir):
            rel_dir_parts = [p.lower() for p in os.path.relpath(root, extract_dir).replace("\\", "/").split("/") if p and p != "."]
            in_libs_subdir = any(p in ("lib", "libs", "libraries") for p in rel_dir_parts)
            for f in files:
                lower_f = f.lower()
                full_path = os.path.join(root, f)
                if lower_f.endswith((".addon", ".txt")):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as sub_mf:
                            sub_text = sub_mf.read()
                        if re.search(r"^\s*##\s*(?:Title|AddOnVersion)\s*:", sub_text, flags=re.MULTILINE | re.IGNORECASE):
                            bundled_sub_addons.add(os.path.splitext(f)[0].lower())
                            if re.search(r"^\s*##\s*IsLibrary\s*:\s*true\b", sub_text, flags=re.MULTILINE | re.IGNORECASE):
                                is_library = True
                            for m_line in sub_text.splitlines():
                                sv_match = re.match(r"^\s*##\s*SavedVariables\s*:\s*(.+)$", m_line.strip(), flags=re.IGNORECASE)
                                if sv_match:
                                    sv_rhs = re.split(r"[#;]", sv_match.group(1), maxsplit=1)[0]
                                    for sv_name in re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", sv_rhs):
                                        saved_variables.add(sv_name)
                    except Exception:
                        pass
                if f.lower() == "bindings.xml":
                    has_bindings_xml = True
                if lower_f.endswith(".xml"):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as xf:
                            raw_xml = xf.read()
                        clean_xml = re.sub(r'<!--.*?-->', '', raw_xml, flags=re.DOTALL)
                        xml_combined_parts.append(clean_xml)
                        for ctrl_name, _ in extract_resolved_xml_control_names(clean_xml):
                            dynamic_globals.add(ctrl_name)
                        for m_ctrl in re.finditer(r'\bname\s*=\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']', clean_xml):
                            dynamic_globals.add(m_ctrl.group(1))
                    except Exception:
                        pass
                elif lower_f.endswith(".lua"):
                    lua_file_total += 1
                    if not in_libs_subdir:
                        own_lua_file_total += 1
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as lf:
                            raw_lua_txt = lf.read()
                        rel_f_norm = os.path.relpath(full_path, extract_dir).replace("\\", "/")
                        lua_clean = strip_lua_comments_preserve_lines(raw_lua_txt)
                        lua_no_str = strip_lua_strings_preserve_lines(lua_clean)
                        lua_texts_for_dyn_g.append((rel_f_norm, lua_clean))
                        file_locals = _collect_lua_local_identifiers(lua_no_str)
                        line_scopes = _build_line_local_scopes(lua_no_str)
                        top_level_local_tables = set()
                        block_stack = []
                        in_loop_header = False
                        brace_depth = 0
                        tok_rx = re.compile(r'\b(function|if|for|while|repeat|do|end|until)\b')
                        for ln_no, code_ln in enumerate(lua_no_str.splitlines(), 1):
                            if brace_depth == 0 and not block_stack:
                                m_loc_tbl = re.match(r'^\s*local\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\{', code_ln)
                                if m_loc_tbl:
                                    top_level_local_tables.add(m_loc_tbl.group(1))
                                m_tbl = re.match(
                                    r'^\s*(?!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:\{|\1\s*or\s*\{|([A-Za-z_][A-Za-z0-9_]*)\s*$)',
                                    code_ln,
                                )
                                if m_tbl:
                                    m_name = m_tbl.group(1)
                                    rhs_ident = m_tbl.group(2)
                                    scoped_locals = line_scopes[ln_no - 1] if (ln_no - 1) < len(line_scopes) else set()
                                    is_valid_rhs = (rhs_ident is None) or (rhs_ident in file_locals or rhs_ident in scoped_locals)
                                    if is_valid_rhs and m_name not in file_locals and m_name not in scoped_locals and m_name not in ESOUI_GLOBAL_DEFINES:
                                        all_global_tables.add(m_name)
                                        global_tables_by_file[rel_f_norm].add(f"{ln_no}: {m_name}")
                            elif brace_depth == 0 and top_level_local_tables:
                                m_eof_export = re.match(
                                    r'^\s*(?!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_]*)\s*$',
                                    code_ln,
                                )
                                if m_eof_export and m_eof_export.group(2) in top_level_local_tables:
                                    m_name = m_eof_export.group(1)
                                    if m_name not in file_locals and m_name not in ESOUI_GLOBAL_DEFINES:
                                        all_global_tables.add(m_name)
                                        global_tables_by_file[rel_f_norm].add(f"{ln_no}: {m_name}")
                            brace_depth = max(0, brace_depth + code_ln.count("{") - code_ln.count("}"))
                            for tm in tok_rx.finditer(code_ln):
                                kw = tm.group(1)
                                if kw in ("for", "while"):
                                    block_stack.append("loop")
                                    in_loop_header = True
                                elif kw == "do":
                                    if in_loop_header:
                                        in_loop_header = False
                                    else:
                                        block_stack.append("do")
                                elif kw == "repeat":
                                    block_stack.append("repeat")
                                elif kw in ("function", "if"):
                                    block_stack.append(kw)
                                elif kw == "until":
                                    while block_stack:
                                        if block_stack.pop() == "repeat":
                                            break
                                elif kw == "end" and block_stack:
                                    if block_stack[-1] == "loop":
                                        in_loop_header = False
                                    block_stack.pop()
                        for m_g in re.finditer(r'_G\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]\s*=', lua_clean):
                            g_name = m_g.group(1)
                            ln_no = lua_clean.count("\n", 0, m_g.start(1)) + 1
                            all_global_tables.add(g_name)
                            global_tables_by_file[rel_f_norm].add(f"{ln_no}: {g_name}")
                        rel_f = os.path.relpath(full_path, extract_dir).replace("\\", "/")
                        file_defined_globals = extract_globals_from_lua_source(raw_lua_txt, rel_f)
                        dynamic_globals.update(file_defined_globals.keys())
                        for v_ctrl, _ in extract_virtual_controls_from_lua(raw_lua_txt):
                            dynamic_globals.add(v_ctrl)
                    except Exception:
                        pass

        dyn_wrapper_funcs = {}
        func_def_rx = re.compile(r'\b(?:local\s+)?function\s+([A-Za-z_][A-Za-z0-9_.:]*)\s*\(([^)]*)\)')
        for _, l_txt in lua_texts_for_dyn_g:
            for fm in func_def_rx.finditer(l_txt):
                fn_name = fm.group(1)
                params = [p.strip() for p in fm.group(2).split(",") if p.strip()]
                _, fn_body = _extract_lua_function_body_from_offset(l_txt, fm.start())
                for p_idx, p_name in enumerate(params):
                    if re.search(r'\b_G\[\s*' + re.escape(p_name) + r'\s*\]\s*=', fn_body):
                        dyn_wrapper_funcs[fn_name] = p_idx
                        dyn_wrapper_funcs[fn_name.split(".")[-1].split(":")[-1]] = p_idx
                        break

        for rel_f_norm, l_txt in lua_texts_for_dyn_g:
            for fn_name, p_idx in dyn_wrapper_funcs.items():
                call_rx = re.compile(r'\b' + re.escape(fn_name) + r'\s*\(')
                for cm in call_rx.finditer(l_txt):
                    args_raw, _ = _extract_balanced_call_args(l_txt, cm.end() - 1)
                    if args_raw:
                        args = _split_top_level_lua_args(args_raw)
                        if p_idx < len(args):
                            str_m = re.match(r'^["\']([A-Za-z_][A-Za-z0-9_]*)["\']$', args[p_idx].strip())
                            if str_m:
                                w_name = str_m.group(1)
                                ln_no = l_txt.count("\n", 0, cm.start()) + 1
                                all_global_tables.add(w_name)
                                global_tables_by_file[rel_f_norm].add(f"{ln_no}: {w_name}")

        for m_file in root_addon_manifests + root_txt_manifests:
            m_path = os.path.join(manifest_root_dir, m_file)
            try:
                with open(m_path, "r", encoding="utf-8", errors="ignore") as mf:
                    for m_line in mf:
                        sv_match = re.match(r'^\s*##\s*SavedVariables\s*:\s*(.+)$', m_line.strip(), flags=re.IGNORECASE)
                        if sv_match:
                            for sv_name in sv_match.group(1).split():
                                if sv_name:
                                    saved_variables.add(sv_name.strip())
            except Exception:
                pass

    has_public_api_functions = (
        _detect_public_api_functions_on_globals(lua_texts_for_dyn_g, all_global_tables)
        if extract_dir and os.path.exists(extract_dir)
        else False
    )

    return {
        "has_bindings_xml": has_bindings_xml,
        "is_library": is_library,
        "has_public_api_functions": has_public_api_functions,
        "lua_file_count": lua_file_total if extract_dir and os.path.exists(extract_dir) else 0,
        "own_lua_file_count": own_lua_file_total if extract_dir and os.path.exists(extract_dir) else 0,
        "xml_content": "\n".join(xml_combined_parts),
        "all_global_tables": all_global_tables,
        "dynamic_globals": dynamic_globals,
        "saved_variables": saved_variables,
        "root_addon_manifests": root_addon_manifests,
        "root_txt_manifests": root_txt_manifests,
        "bundled_sub_addons": bundled_sub_addons,
        "global_tables_by_file": dict(global_tables_by_file),
    }
def _collect_lua_local_identifiers(code_only):
    """Collects local variables, function parameters, and loop variables in a Lua file."""
    file_locals = set(re.findall(r'\blocal\s+function\s+([A-Za-z_][A-Za-z0-9_]*)', code_only))
    for decl in re.findall(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)', code_only):
        for name in decl.split(","):
            clean_n = name.strip()
            if clean_n and clean_n != "function":
                file_locals.add(clean_n)
    for param_list in re.findall(r'\bfunction(?:\s+[A-Za-z_][A-Za-z0-9_.:]*)?\s*\(([^)]*)\)', code_only):
        for param in param_list.split(","):
            clean_p = param.strip()
            if clean_p and clean_p != "...":
                file_locals.add(clean_p)
    for loop_vars in re.findall(r'\bfor\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)\s+(?:in|=)', code_only):
        for lv in loop_vars.split(","):
            clean_lv = lv.strip()
            if clean_lv:
                file_locals.add(clean_lv)
    return file_locals


def find_repeated_globals_in_lua(content, raw_lines, all_addon_globals, ram_dict, undoc_set, std_libs):
    """Detects globals referenced >= 2 times in a file without a local alias."""
    code_only = strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)
    lines = code_only.splitlines()
    file_locals = _collect_lua_local_identifiers(code_only)
    file_hits = defaultdict(list)
    ident_pat = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')

    for idx, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if not stripped_line or re.match(r'^local\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*[A-Za-z_][A-Za-z0-9_]*\s*$', stripped_line):
            continue
        for match in ident_pat.finditer(line):
            word = match.group(1)
            if len(word) < 3 or word in LUA_KEYWORDS or word in file_locals:
                continue
            start_pos, end_pos = match.span()
            prefix = line[:start_pos].rstrip()
            suffix = line[end_pos:].lstrip()
            if prefix.endswith((".", ":")) or (suffix.startswith("=") and not suffix.startswith("==")):
                continue
            if not (word in all_addon_globals or word in ram_dict or word in undoc_set or word in std_libs):
                continue
            orig_line = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
            file_hits[word].append((idx, orig_line))

    primary_findings = []
    minor_stdlib_findings = []
    for var_name in sorted(file_hits.keys()):
        hits = file_hits[var_name]
        if len(hits) >= 2:
            unique_lines = []
            seen_ln = set()
            for ln, txt in hits:
                if ln not in seen_ln:
                    seen_ln.add(ln)
                    unique_lines.append((ln, txt))
            formatted_hits = [f"    {var_name}:{ln} --{txt}" for ln, txt in unique_lines]
            if var_name in std_libs:
                minor_stdlib_findings.append(
                    f"[Minor] Lua Standard Global '{var_name}' is accessed {len(hits)} times without a local reference:\n"
                    + "\n".join(formatted_hits)
                )
            else:
                primary_findings.append(
                    f"Best Practice Violation: Global '{var_name}' is used {len(hits)} times in this file without a local reference:\n"
                    + "\n".join(formatted_hits)
                )
    return primary_findings, minor_stdlib_findings
def _split_top_level_lua_args(arg_str):
    """Splits a Lua argument list on top-level commas, respecting (), {}, [], and quotes."""
    args = []
    depth_p = depth_b = depth_s = 0
    in_quote = None
    esc = False
    curr = []
    for ch in arg_str:
        if in_quote:
            curr.append(ch)
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
            curr.append(ch)
        elif ch == "(":
            depth_p += 1
            curr.append(ch)
        elif ch == ")":
            depth_p = max(0, depth_p - 1)
            curr.append(ch)
        elif ch == "{":
            depth_b += 1
            curr.append(ch)
        elif ch == "}":
            depth_b = max(0, depth_b - 1)
            curr.append(ch)
        elif ch == "[":
            depth_s += 1
            curr.append(ch)
        elif ch == "]":
            depth_s = max(0, depth_s - 1)
            curr.append(ch)
        elif ch == "," and depth_p == 0 and depth_b == 0 and depth_s == 0:
            args.append("".join(curr).strip())
            curr = []
        else:
            curr.append(ch)
    if curr:
        args.append("".join(curr).strip())
    return args


def _extract_balanced_call_args(text, open_paren_pos):
    """Returns (args_substring, close_paren_pos) starting at '(' or (None, -1)."""
    n = len(text)
    if open_paren_pos >= n or text[open_paren_pos] != "(":
        return None, -1
    depth = 0
    in_quote = None
    esc = False
    for idx in range(open_paren_pos, n):
        ch = text[idx]
        if in_quote:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == in_quote:
                in_quote = None
            continue
        if ch in ('"', "'"):
            in_quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren_pos + 1:idx], idx
    return None, -1


def _extract_lua_function_body_from_offset(text, func_start_pos):
    """Extracts (params_list, body_text) for a Lua function starting at 'function'."""
    paren_pos = text.find("(", func_start_pos)
    if paren_pos == -1:
        return [], ""
    params_raw, close_paren = _extract_balanced_call_args(text, paren_pos)
    if params_raw is None:
        return [], ""
    params = [p.strip() for p in params_raw.split(",") if p.strip()]
    token_rx = re.compile(r"\b(function|if|for|while|repeat|end|until)\b")
    depth = 1
    body_start = close_paren + 1
    for tm in token_rx.finditer(text, body_start):
        tok = tm.group(1)
        if tok in ("function", "if", "for", "while", "repeat"):
            depth += 1
        elif tok in ("end", "until"):
            depth -= 1
            if depth == 0:
                return params, text[body_start:tm.start()]
    return params, text[body_start:]
def _get_event_filter_spec(event_name):
    """Returns (allowed_filter_types_set, rule_title) for filterable ESO events or (None, None)."""
    _sync_wiki_event_filters_once()
    if event_name in EVENT_FILTER_RULES:
        spec = EVENT_FILTER_RULES[event_name]
        return set(spec["filters"]), spec["rule_title"]
    if event_name in _WIKI_DYNAMIC_EVENT_RULES:
        spec = _WIKI_DYNAMIC_EVENT_RULES[event_name]
        return set(spec["filters"]), spec["rule_title"]

    if event_name in ESOUI_EVENT_HAS_UNIT_TAG:
        return (
            {"REGISTER_FILTER_UNIT_TAG", "REGISTER_FILTER_UNIT_TAG_PREFIX"},
            "Use event filters for unit tags instead of checking code slower in lua",
        )
    return None, None



def _check_lua_event_filters(content, raw_lines, lua_issues):
    """
    Prüft RegisterForEvent-Aufrufe für filterbare ESO-Events:
      1) Wurde kein passendes AddFilterForEvent für das Event genutzt -> Critical Violation.
      2) Wurde AddFilterForEvent genutzt, prüft aber der Callback denselben Parameter erneut im Lua-Code -> Critical Violation.
    """
    if not is_index_built():
        build_esoui_index_once()

    clean_code = strip_lua_comments_preserve_lines(content)
    reg_rx = re.compile(r'(?:[A-Za-z_][A-Za-z0-9_.:]*\s*:\s*)?RegisterForEvent\s*\(')
    flt_rx = re.compile(r'(?:[A-Za-z_][A-Za-z0-9_.:]*\s*:\s*)?AddFilterForEvent\s*\(')

    func_bodies = {}
    for fm in re.finditer(r'\b(?:local\s+)?function\s+([A-Za-z_][A-Za-z0-9_.:]*)\s*\(', clean_code):
        full_fn = fm.group(1)
        params, body = _extract_lua_function_body_from_offset(clean_code, fm.start())
        func_bodies[full_fn] = (params, body)
        func_bodies[full_fn.split(".")[-1].split(":")[-1]] = (params, body)

    filters_by_event = defaultdict(list)
    for m in flt_rx.finditer(clean_code):
        args_raw, _ = _extract_balanced_call_args(clean_code, m.end() - 1)
        if not args_raw:
            continue
        args = _split_top_level_lua_args(args_raw)
        if len(args) < 4:
            continue
        handle_expr, ev_name = args[0], args[1]
        if not ev_name.startswith("EVENT_"):
            continue
        pairs = []
        for idx_p in range(2, len(args) - 1, 2):
            f_type = args[idx_p].strip()
            f_val = args[idx_p + 1].strip()
            if f_type.startswith("REGISTER_FILTER_"):
                pairs.append((f_type, f_val))
        if pairs:
            filters_by_event[ev_name].append((handle_expr, pairs))

    for m in reg_rx.finditer(clean_code):
        args_raw, _ = _extract_balanced_call_args(clean_code, m.end() - 1)
        if not args_raw:
            continue
        args = _split_top_level_lua_args(args_raw)
        if len(args) < 3:
            continue
        handle_expr, ev_name, cb_expr = args[0], args[1], args[2]
        allowed_filters, rule_title = _get_event_filter_spec(ev_name)
        if not allowed_filters:
            continue

        line_no = clean_code.count("\n", 0, m.start()) + 1
        orig_line = raw_lines[line_no - 1].strip() if (line_no - 1) < len(raw_lines) else ""
        ev_filters = filters_by_event.get(ev_name, [])
        matching_handles = [
            pairs for h_expr, pairs in ev_filters
            if h_expr == handle_expr or any(ft in allowed_filters for ft, _ in pairs)
        ]

        cb_params, cb_body = [], ""
        if cb_expr.startswith("function"):
            fn_offset = clean_code.find("function", m.end())
            if fn_offset != -1:
                cb_params, cb_body = _extract_lua_function_body_from_offset(clean_code, fn_offset)
        else:
            cb_key = cb_expr.strip()
            if cb_key in func_bodies:
                cb_params, cb_body = func_bodies[cb_key]
            elif cb_key.split(".")[-1].split(":")[-1] in func_bodies:
                cb_params, cb_body = func_bodies[cb_key.split(".")[-1].split(":")[-1]]

        if not matching_handles:
            if allowed_filters and allowed_filters <= {"REGISTER_FILTER_UNIT_TAG", "REGISTER_FILTER_UNIT_TAG_PREFIX"}:
                sig = ESOUI_EVENT_PARAM_TYPES.get(ev_name, [])
                unit_param_indices = [
                    s_idx for s_idx, (s_type, s_name) in enumerate(sig, 1)
                    if "unittag" in s_name.lower() or "unittag" in s_type.lower()
                ]
                if unit_param_indices:
                    uses_unit_tag_arg = any(
                        p_idx < len(cb_params) and cb_params[p_idx] and cb_params[p_idx] != "_"
                        for p_idx in unit_param_indices
                    )
                    if not uses_unit_tag_arg:
                        continue
            lua_issues.append(f"{rule_title}: {ev_name} (line {line_no}) ({orig_line})")
            continue
        if not cb_params or not cb_body:
            continue

        applied_filter_types = {ft for pairs in matching_handles for ft, _ in pairs}

        for pairs in matching_handles:
            for f_type, f_val in pairs:
                p_idx = FILTER_TYPE_PARAM_INDEX.get((ev_name, f_type))
                if p_idx is None:
                    sig = ESOUI_EVENT_PARAM_TYPES.get(ev_name, [])
                    for s_idx, (s_type, s_name) in enumerate(sig, 1):
                        if f_type in ("REGISTER_FILTER_UNIT_TAG", "REGISTER_FILTER_UNIT_TAG_PREFIX") and (
                            "unittag" in s_name.lower() or "unittag" in s_type.lower()
                        ):
                            p_idx = s_idx
                            break
                if p_idx is not None and p_idx < len(cb_params):
                    param_var = cb_params[p_idx]
                    if param_var and param_var != "_" and re.search(
                        r'\bif\b[^;\n]*\b' + re.escape(param_var) + r'\b\s*(?:==|~=)', cb_body
                    ):
                        lua_issues.append(
                            f"{rule_title}: {ev_name} (line {line_no}) "
                            f"({orig_line} -- redundant '{param_var}' check in callback despite {f_type}={f_val})"
                        )

        if (
            {"REGISTER_FILTER_UNIT_TAG", "REGISTER_FILTER_UNIT_TAG_PREFIX"} & allowed_filters
            and not ({"REGISTER_FILTER_UNIT_TAG", "REGISTER_FILTER_UNIT_TAG_PREFIX"} & applied_filter_types)
        ):
            sig = ESOUI_EVENT_PARAM_TYPES.get(ev_name, [])
            unit_p_idx = None
            for s_idx, (s_type, s_name) in enumerate(sig, 1):
                if "unittag" in s_name.lower() or "unittag" in s_type.lower():
                    unit_p_idx = s_idx
                    break
            if unit_p_idx is not None and unit_p_idx < len(cb_params):
                u_var = cb_params[unit_p_idx]
                if u_var and u_var != "_":
                    esc_u = re.escape(u_var)
                    has_prefix_match = bool(
                        re.search(
                            rf'\b(?:{esc_u}\s*:\s*(?:match|find)|(?:string\.(?:match|find)|zo_strfind)\s*\(\s*{esc_u}\b)',
                            cb_body,
                        )
                    )
                    has_exact_eq = bool(
                        re.search(
                            rf'(?:\b{esc_u}\s*(?:==|~=)\s*["\'][^"\']+["\']|["\'][^"\']+["\']\s*(?:==|~=)\s*\b{esc_u}\b)',
                            cb_body,
                        )
                    )
                    if has_prefix_match:
                        lua_issues.append(
                            f"{rule_title}: {ev_name} (line {line_no}) "
                            f"({orig_line} -- Use REGISTER_FILTER_UNIT_TAG_PREFIX instead of filtering '{u_var}' in Lua)"
                        )
                    elif has_exact_eq:
                        lua_issues.append(
                            f"{rule_title}: {ev_name} (line {line_no}) "
                            f"({orig_line} -- Use REGISTER_FILTER_UNIT_TAG instead of checking '{u_var}' in Lua)"
                        )

def _check_lua_ai_slop_patterns(content, raw_lines):
    """Detects defensive pcall() and unnecessary 'if ESO_GLOBAL then' existence checks."""
    if not is_index_built():
        build_esoui_index_once()

    code_only = strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)
    lines = code_only.splitlines()
    file_locals = _collect_lua_local_identifiers(code_only)

    pcall_hits = []
    exists_hits = []
    pcall_pat = re.compile(r'(?<![A-Za-z0-9_.:])\bpcall\s*\(')
    if_exists_pat = re.compile(
        r'\b(?:if|elseif)\s+(?:type\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*(?:==|~=)\s*["\'](?:nil|function|table)["\']|([A-Za-z_][A-Za-z0-9_]*)\s*(?:~= nil)?)\s*then\b'
    )

    for idx, line in enumerate(lines, 1):
        orig = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
        for _ in pcall_pat.finditer(line):
            pcall_hits.append((idx, orig))
        for m in if_exists_pat.finditer(line):
            ident = m.group(1) or m.group(2)
            if not ident or len(ident) < 3 or ident in file_locals or not ident.isupper():
                continue
            if ident in ESOUI_RAM_DICTIONARY or ident in ESOUI_UNDOCUMENTED_SET:
                exists_hits.append((idx, ident, orig))

    if not pcall_hits and not exists_hits:
        return ""

    report_lines = ["\n[REVIEW POTENTIAL AI CODE]"]
    if pcall_hits:
        report_lines.append(f"pcall usage: {len(pcall_hits)} times. Please review if pcall is really needed, else remove and directly call code")
        for ln, orig in pcall_hits:
            report_lines.append(f"  - {ln}: --{orig}")
    if exists_hits:
        report_lines.append(f"Unnecessary 'exists' checks: {len(exists_hits)} times")
        for ln, ident, orig in exists_hits:
            report_lines.append(f"  - {ln} ({ident}): --{orig}")
    return "\n".join(report_lines)


def _check_lua_deprecated_savedvars(comment_free_lua, raw_lines, lua_issues):
    pattern = re.compile(r'ZO_SavedVars\s*:\s*NewCharacterNameSettings\b')
    for idx, line in enumerate(comment_free_lua.splitlines(), 1):
        if pattern.search(line):
            orig = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
            lua_issues.append(
                f"Deprecated SavedVars API at line {idx}: Use 'ZO_SavedVars:NewCharacterIdSettings' instead of 'NewCharacterNameSettings' (--{orig})."
            )


def _build_line_local_scopes(code_only):
    """
    Computes per-line active sets of valid local variables, loop variables,
    and function parameters in the enclosing lexical scope.
    """
    lines = code_only.splitlines()
    active_scopes = [set()]
    line_scopes = []
    block_rx = re.compile(r'\b(function|if|for|while|repeat|do)\b|\b(end|until)\b')

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("local function "):
            m_lf = re.match(r'^local\s+function\s+([A-Za-z_][A-Za-z0-9_]*)', stripped)
            if m_lf:
                active_scopes[-1].add(m_lf.group(1))

        for m_fn in re.finditer(r'\bfunction(?:\s+[A-Za-z_][A-Za-z0-9_.:]*)?\s*\(([^)]*)\)', line):
            params = {p.strip() for p in m_fn.group(1).split(",") if p.strip() and p.strip() != "..."}
            active_scopes.append(params)

        m_for = re.match(r'^for\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)\s+(?:in|=)\b', stripped)
        if m_for:
            fvars = {v.strip() for v in m_for.group(1).split(",") if v.strip()}
            active_scopes.append(fvars)

        line_scopes.append(set().union(*active_scopes))

        for loc_m in re.finditer(
            r'\blocal\s+(?!function\b)([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)',
            stripped,
        ):
            for v in loc_m.group(1).split(","):
                clean_v = v.strip()
                if clean_v:
                    active_scopes[-1].add(clean_v)
                    line_scopes[-1].add(clean_v)
        for bm in block_rx.finditer(line):
            b_open, b_close = bm.groups()
            if b_open in ("if", "while", "repeat", "do"):
                active_scopes.append(set())
            elif b_close in ("end", "until") and len(active_scopes) > 1:
                active_scopes.pop()

    return line_scopes


def _check_lua_global_variable_leaks(content, raw_lines, addon_ctx, lua_issues, move_to_table_hits=None):
    """
    Detects global variable assignments (missing 'local') anywhere in a Lua file,
    accurately ignoring table constructor fields while still catching global leaks inside table callbacks.
    """
    if not is_index_built():
        build_esoui_index_once()

    code_only = strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)
    lines = code_only.splitlines()
    line_local_scopes = _build_line_local_scopes(code_only)

    global_tables = set(addon_ctx.get("all_global_tables", set()))
    table_prefixes = tuple(f"{gt}_" for gt in global_tables if gt)

    allowed_globals = (
        global_tables
        | set(addon_ctx.get("saved_variables", set()))
        | set(ESOUI_GLOBAL_DEFINES)
        | set(ESOUI_RAM_DICTIONARY.keys())
        | ESOUI_UNDOCUMENTED_SET
        | LUA_STD_LIBS
    )

    scope_stack = []
    token_rx = re.compile(
        r'(\{)|(\})|\b(function|if|for|while|repeat|do)\b|\b(end|until)\b|(?<![A-Za-z0-9_.:])([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)'
    )

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        is_local_stmt = stripped.startswith("local ")
        scoped_locals = line_local_scopes[idx - 1] if idx - 1 < len(line_local_scopes) else set()
        line_for_tokens = re.sub(r'\b(for|while)\b([^;\n]*?)\bdo\b', lambda mm: f"{mm.group(1)}{mm.group(2)}  ", line)

        for m in token_rx.finditer(line_for_tokens):
            g_open_brace, g_close_brace, g_block_open, g_block_close, var_name = m.groups()
            if g_open_brace:
                scope_stack.append("table")
            elif g_close_brace:
                if scope_stack and scope_stack[-1] == "table":
                    scope_stack.pop()
            elif g_block_open:
                scope_stack.append("block")
            elif g_block_close:
                if scope_stack and scope_stack[-1] == "block":
                    scope_stack.pop()
            elif var_name and not is_local_stmt:
                if scope_stack and scope_stack[-1] == "table":
                    continue
                if var_name in LUA_KEYWORDS or var_name in scoped_locals or var_name in allowed_globals:
                    continue

                prefix = line[:m.start(5)].rstrip()
                if prefix.endswith((".", ":", "[", "{", ",")) or re.search(r'\bfor$', prefix):
                    continue
                if re.search(r'\blocal\s+(?:[A-Za-z_][A-Za-z0-9_]*\s*,\s*)*$', prefix):
                    continue
                if stripped.endswith(","):
                    continue

                orig = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
                if table_prefixes and var_name.startswith(table_prefixes) and move_to_table_hits is not None:
                    move_to_table_hits.append((idx, orig))
                else:
                    lua_issues.append(
                        f"Global Variable Pollution (missing 'local' for '{var_name}') (line {idx}): (-- {orig})"
                    )
def _check_lua_startup_chat_spam(comment_free_lua, raw_lines, lua_suggestions, addon_ctx=None):
    """Detects unconditional chat output inside EVENT_ADD_ON_LOADED / EVENT_PLAYER_ACTIVATED handlers."""
    code_no_strings = strip_lua_strings_preserve_lines(comment_free_lua)
    clean_lines = code_no_strings.splitlines()

    sv_identifiers = set(addon_ctx.get("saved_variables", set())) if addon_ctx else set()
    for m in re.finditer(r'([A-Za-z_][A-Za-z0-9_.]*)\s*=\s*ZO_SavedVars\s*:\s*New\w*\s*\(', code_no_strings):
        sv_identifiers.add(m.group(1))
        sv_identifiers.add(m.group(1).split(".")[-1])

    for _ in range(2):
        for m in re.finditer(r'\b(?:local\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([A-Za-z_][A-Za-z0-9_.]*)', code_no_strings):
            lhs, rhs = m.group(1), m.group(2)
            if rhs in sv_identifiers or rhs.split(".")[-1] in sv_identifiers:
                sv_identifiers.add(lhs)

    chat_call_pat = re.compile(r'(?<![A-Za-z0-9_.:])(?:d|CHAT_SYSTEM\s*:\s*AddMessage)\s*\(')
    reg_pat = re.compile(r'RegisterForEvent\s*\([^,]+,\s*(?:EVENT_ADD_ON_LOADED|EVENT_PLAYER_ACTIVATED)\s*,\s*([A-Za-z_][A-Za-z0-9_.:]*|function\b)')
    func_def_header_pat = re.compile(r'\bfunction\s+([A-Za-z_][A-Za-z0-9_.:]*)\s*\(')
    func_call_pat = re.compile(r'\b([A-Za-z_][A-Za-z0-9_.:]*)\s*\(')
    token_pat = re.compile(r'\b(function|if|for|while|repeat|end|until)\b')

    func_defs_by_short = defaultdict(list)
    for idx, line in enumerate(clean_lines, 1):
        fm = func_def_header_pat.search(line)
        if fm:
            func_defs_by_short[fm.group(1).split(".")[-1].split(":")[-1]].append(idx)

    callback_names = set()
    inline_event_lines = []
    for idx, line in enumerate(clean_lines, 1):
        for m in reg_pat.finditer(line):
            target = m.group(1)
            if target == "function":
                inline_event_lines.append(idx)
            else:
                callback_names.add(target.split(".")[-1].split(":")[-1])

    def _is_opt_in_if_condition(if_line_text):
        cond_match = re.search(r'\bif\b(.*?)\bthen\b', if_line_text)
        if not cond_match:
            return False
        cond = cond_match.group(1).strip()
        if re.match(r'^addOnName\s*(?:==|~=)', cond, flags=re.IGNORECASE):
            return False
        if any(sv in cond for sv in sv_identifiers if sv):
            return True
        if re.search(r'\b(?:savedVars|savedVariables|settings|db|sv)\.[A-Za-z_][A-Za-z0-9_]*', cond, flags=re.IGNORECASE):
            return True
        return bool(re.search(r'\b(?:showLoadedMessage|showStartup|chatOutput|announce|verbose|debugMode)\b', cond, flags=re.IGNORECASE))

    def _scan_function_from_line(start_idx, visited_starts, depth_level=0):
        if start_idx in visited_starts or depth_level > 2:
            return []
        visited_starts.add(start_idx)
        block_stack = []
        opened = False
        hits = []
        called_funcs = []

        for ln in range(start_idx, len(clean_lines) + 1):
            cline = clean_lines[ln - 1]
            has_opt_in_guard = any(tok == "if" and is_opt for tok, is_opt in block_stack)
            if not has_opt_in_guard and chat_call_pat.search(cline):
                orig = raw_lines[ln - 1].strip() if (ln - 1) < len(raw_lines) else ""
                hits.append((ln, orig))
            if ln > start_idx:
                for cm in func_call_pat.finditer(cline):
                    callee_short = cm.group(1).split(".")[-1].split(":")[-1]
                    if callee_short in func_defs_by_short:
                        called_funcs.append(callee_short)
            for tm in token_pat.finditer(cline):
                tok = tm.group(1)
                if tok == "if":
                    block_stack.append(("if", _is_opt_in_if_condition(cline)))
                    opened = True
                elif tok in ("function", "for", "while", "repeat"):
                    block_stack.append((tok, False))
                    opened = True
                elif tok in ("end", "until") and block_stack:
                    block_stack.pop()
            if opened and not block_stack:
                break

        for callee in called_funcs:
            for target_ln in func_defs_by_short.get(callee, []):
                hits.extend(_scan_function_from_line(target_ln, visited_starts, depth_level + 1))
        return hits

    spam_hits = []
    seen_lines = set()
    visited_func_starts = set()
    for start_ln in inline_event_lines:
        for ln, orig in _scan_function_from_line(start_ln, visited_func_starts):
            if ln not in seen_lines:
                seen_lines.add(ln)
                spam_hits.append((ln, orig))
    for cb_name in callback_names:
        for start_ln in func_defs_by_short.get(cb_name, []):
            for ln, orig in _scan_function_from_line(start_ln, visited_func_starts):
                if ln not in seen_lines:
                    seen_lines.add(ln)
                    spam_hits.append((ln, orig))

    if spam_hits:
        spam_hits.sort(key=lambda x: x)
        formatted = "\n".join([f"    {ln}: --{orig}" for ln, orig in spam_hits])
        lua_suggestions.append(
            "Startup Chat Spam Detected: Remove \"Addon loaded\" chat message and use LibDebugLogger for debug output, "
            "or make the loaded messages opt-in for the interested-in users (via slash_command and/or settings menu):\n"
            + formatted
        )
def _check_lua_global_tables_and_locals(comment_free_lua, raw_lines, clean_lines_list, lua_file_count, addon_ctx, lua_issues, dep_globals_set=None, file_name=""):
    """Checks global table pollution, multiple global tables, global functions, and local aliases."""
    lua_suggestions = []
    has_bindings_xml = addon_ctx["has_bindings_xml"]
    combined_xml_content = addon_ctx["xml_content"]
    all_addon_globals = set(dep_globals_set or set())

    if not is_index_built():
        build_esoui_index_once()

    if len(addon_ctx["all_global_tables"]) > 1:
        norm_fn = file_name.replace("\\", "/")
        raw_file_tbls = (addon_ctx.get("global_tables_by_file") or {}).get(norm_fn, set())
        if raw_file_tbls:
            sorted_globals = ", ".join(sorted(addon_ctx["all_global_tables"]))
            file_tbls = sorted(
                raw_file_tbls,
                key=lambda s: (int(s.split(":", 1)[0]) if ":" in s and s.split(":", 1)[0].isdigit() else 0, s),
            )
            detail_suffix = f" ({', '.join(file_tbls)})"
            lua_issues.append(
                f"Multiple Global Addon Tables: Found {len(addon_ctx['all_global_tables'])} global tables across the addon ({sorted_globals}). "
                f"Only ONE global table per addon is allowed; attach sub-tables to your main addon table instead!{detail_suffix}"
            )
    func_def_rx = re.compile(r'^(?!local\s)function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')
    for idx, c_line in enumerate(clean_lines_list, 1):
        fm = func_def_rx.match(c_line)
        if not fm:
            continue
        g_func = fm.group(1)
        if g_func not in ESOUI_RAM_DICTIONARY and g_func not in ESOUI_UNDOCUMENTED_SET:
            if not re.search(r'\blocal\s+' + re.escape(g_func) + r'\b', comment_free_lua):
                orig = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
                lua_issues.append(
                    f"Global Function Pollution (leaked into _G) (line {idx}): "
                    f"Keep '{g_func}()' local or attach it to your single addon table (-- {orig})"
                )

    is_library_addon = bool(addon_ctx.get("is_library"))
    lua_no_str_local = strip_lua_strings_preserve_lines(comment_free_lua)
    declared_file_locals = _collect_lua_local_identifiers(lua_no_str_local)
    raw_table_matches = re.findall(
        r'^(?<!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:\{|\1\s*or\s*\{|[A-Za-z_][A-Za-z0-9_]*\s*$)',
        lua_no_str_local,
        flags=re.MULTILINE,
    )
    global_table_matches = [
        m for m in dict.fromkeys(raw_table_matches)
        if m not in declared_file_locals and m not in ESOUI_GLOBAL_DEFINES
    ]

    addon_anchors = set()
    for mf in (addon_ctx.get("root_addon_manifests") or []) + (addon_ctx.get("root_txt_manifests") or []):
        clean_a = re.sub(r"[^a-z0-9]", "", os.path.splitext(os.path.basename(mf))[0].lower())
        if len(clean_a) >= 4:
            addon_anchors.add(clean_a)
            stripped_digits = re.sub(r"\d+$", "", clean_a)
            if len(stripped_digits) >= 4:
                addon_anchors.add(stripped_digits)
    if not addon_anchors and file_name:
        first_seg = next(iter(file_name.replace("\\", "/").split("/")), "")
        clean_seg = re.sub(r"[^a-z0-9]", "", os.path.splitext(first_seg)[0].lower())
        if len(clean_seg) >= 4:
            addon_anchors.add(clean_seg)

    aliased_globals_in_file = set()
    polluted_globals_in_file = set()
    for g_table in global_table_matches:
        used_in_xml = bool(re.search(r'\b' + re.escape(g_table) + r'\b', combined_xml_content))
        is_legitimate_global = is_library_addon or (lua_file_count > 1) or has_bindings_xml or used_in_xml

        def_ln = 1
        orig_def = ""
        tbl_def_rx = re.compile(r'^\s*(?!local\s)' + re.escape(g_table) + r'\s*=')
        for idx_d, c_ln in enumerate(clean_lines_list, 1):
            if tbl_def_rx.match(c_ln):
                def_ln = idx_d
                orig_def = raw_lines[idx_d - 1].strip() if (idx_d - 1) < len(raw_lines) else ""
                break

        norm_gt = re.sub(r"[^a-z0-9]", "", g_table.lower())
        has_addon_anchor = (not addon_anchors) or any(anc in norm_gt for anc in addon_anchors)
        if len(g_table) < 6 or len(norm_gt) < 6 or not has_addon_anchor:
            lua_issues.append(
                f"Non-unique / too short global variable '{g_table}' (line {def_ln}): (-- {orig_def})"
            )

        alias_match = re.search(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*' + re.escape(g_table) + r'(?!\s*[.:\[(])\b', lua_no_str_local)
        local_alias = alias_match.group(1) if alias_match else None
        if local_alias:
            aliased_globals_in_file.add(g_table)

        direct_usage_lines = []
        member_access_pattern = re.compile(r'\b' + re.escape(g_table) + r'(?:\.[A-Za-z_][A-Za-z0-9_]*|:[A-Za-z_][A-Za-z0-9_]*|\[)')
        for idx, c_line in enumerate(clean_lines_list, 1):
            if member_access_pattern.search(strip_lua_strings_preserve_lines(c_line)):
                orig_line = raw_lines[idx - 1].strip() if (idx - 1) < len(raw_lines) else ""
                direct_usage_lines.append((idx, orig_line))

        if not is_legitimate_global:
            polluted_globals_in_file.add(g_table)
            if not any(f"(missing 'local' for '{g_table}')" in iss for iss in lua_issues):
                def_ln = 1
                orig_def = ""
                tbl_def_rx = re.compile(r'^\s*(?!local\s)' + re.escape(g_table) + r'\s*=')
                for idx_d, c_ln in enumerate(clean_lines_list, 1):
                    if tbl_def_rx.match(c_ln):
                        def_ln = idx_d
                        orig_def = raw_lines[idx_d - 1].strip() if (idx_d - 1) < len(raw_lines) else ""
                        break
                lua_issues.append(
                    f"Global Variable Pollution (missing 'local' for '{g_table}') (line {def_ln}): (-- {orig_def})"
                )
        elif local_alias and direct_usage_lines:
            formatted_hits = [f"    {g_table}:{line_no} --{orig_line}" for line_no, orig_line in direct_usage_lines]
            lua_suggestions.append(
                f"Best Practice Violation: Global table '{g_table}' has local alias '{local_alias}', "
                f"but '{g_table}' is still accessed directly {len(direct_usage_lines)} time(s) instead of using '{local_alias}':\n"
                + "\n".join(formatted_hits)
            )

    # Check all legitimate addon/library global tables for a missing local pointer in this file
    candidate_addon_tables = sorted(
        (set(addon_ctx.get("all_global_tables") or set()) | set(global_table_matches)) - polluted_globals_in_file
    )
    no_str_lines = lua_no_str_local.splitlines()
    for g_table in candidate_addon_tables:
        used_in_xml = bool(re.search(r'\b' + re.escape(g_table) + r'\b', combined_xml_content))
        if not (is_library_addon or (lua_file_count > 1) or has_bindings_xml or used_in_xml):
            continue
        if re.search(r'\blocal\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*' + re.escape(g_table) + r'(?!\s*[.:\[(])\b', lua_no_str_local):
            continue
        def_rx = re.compile(r'^\s*(?!local\s)' + re.escape(g_table) + r'\s*=(?!=)')
        ref_rx = re.compile(r'\b' + re.escape(g_table) + r'\b')
        usage_lines = []
        for idx, s_line in enumerate(no_str_lines, 1):
            if def_rx.match(s_line):
                occ = len(ref_rx.findall(s_line))
                if occ > 1 and not re.match(r'^\s*' + re.escape(g_table) + r'\s*=\s*' + re.escape(g_table) + r'\s*or\s*\{', s_line):
                    usage_lines.append(idx)
            elif ref_rx.search(s_line):
                usage_lines.append(idx)
        if usage_lines:
            lines_fmt = ", ".join(str(ln) for ln in usage_lines)
            lua_suggestions.append(f"Missing local reference to global addon table '{g_table}' (lines {lines_fmt})")

    primary_rep, minor_rep = find_repeated_globals_in_lua(
        "\n".join(raw_lines), raw_lines, all_addon_globals, ESOUI_RAM_DICTIONARY, ESOUI_UNDOCUMENTED_SET, LUA_STD_LIBS
    )
    for finding in primary_rep:
        if not any(f"Global '{ag}'" in finding for ag in aliased_globals_in_file):
            lua_suggestions.append(finding)
    lua_suggestions.extend(minor_rep)
    return lua_suggestions


def extract_globals_from_lua_source(lua_code, rel_display_path):
    """Extracts global identifiers (including dynamic _G[var] string table constants) from a Lua file."""
    exposed = {}
    clean_lua = strip_lua_comments_preserve_lines(lua_code)
    local_strings = dict(re.findall(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\']([^"\']+)["\']', clean_lua))
    has_dyn_g = bool(re.search(r'\b_G\s*\[[^\]]+\]\s*=', clean_lua))

    def _record(name, char_pos):
        if name not in exposed:
            exposed[name] = f"{rel_display_path}:{clean_lua.count(chr(10), 0, char_pos) + 1}"

    for m in re.finditer(r'^\s*(?!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=[^=]', clean_lua, flags=re.MULTILINE):
        _record(m.group(1), m.start(1))
    for m in re.finditer(r'^\s*(?!local\s)function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', clean_lua, flags=re.MULTILINE):
        _record(m.group(1), m.start(1))
    for m in re.finditer(r'_G\[\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']\s*\]\s*=', clean_lua):
        _record(m.group(1), m.start(1))
    for m in re.finditer(r'_G\[\s*([A-Za-z_][A-Za-z0-9_]*)\s*\]\s*=', clean_lua):
        if m.group(1) in local_strings:
            _record(local_strings[m.group(1)], m.start(1))
    for sm in re.finditer(r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']', clean_lua):
        s_ident = sm.group(1)
        if has_dyn_g or re.match(r'^[A-Z][A-Z0-9_]{2,}$', s_ident):
            _record(s_ident, sm.start(1))
    if has_dyn_g:
        for km in re.finditer(r'(?<![A-Za-z0-9_.:])\b([A-Z][A-Z0-9_]{2,})\b\s*=(?!=)', clean_lua):
            _record(km.group(1), km.start(1))
    return exposed
def analyze_lua_file(file_name, content, active_extract_dir, addon_ctx):
    """Runs all static checks on a single Lua source file and queues unverified globals for AI."""
    lua_file_count = int(addon_ctx.get("own_lua_file_count") or addon_ctx.get("lua_file_count") or 0)
    if lua_file_count == 0 and os.path.exists(active_extract_dir):
        lua_file_count = sum(
            1 for root, _, files in os.walk(active_extract_dir)
            if not any(p in ("lib", "libs", "libraries") for p in os.path.relpath(root, active_extract_dir).replace("\\", "/").lower().split("/"))
            for f in files if f.lower().endswith('.lua')
        )

    if "dep_globals_map" not in addon_ctx:
        addon_ctx["dep_globals_map"] = collect_dependency_globals(
            active_extract_dir, extract_globals_from_lua_source, current_addon_id=addon_ctx.get("current_addon_id")
        )
    dep_globals_map = addon_ctx["dep_globals_map"]
    dep_globals_set = set(dep_globals_map.keys())

    lua_issues = []
    for ln_no, orig_line in find_uncommented_libstub_hits(content):
        lua_issues.append(
            f"Deprecated LibStub Usage (obsolete since Summerset) (line {ln_no}): (-- {orig_line})"
        )
    comment_free_lua = strip_lua_comments_preserve_lines(content)
    raw_lines = content.splitlines()
    clean_lines_list = comment_free_lua.splitlines()

    move_to_table_hits = []
    _check_lua_deprecated_savedvars(comment_free_lua, raw_lines, lua_issues)
    _check_lua_event_filters(content, raw_lines, lua_issues)
    _check_lua_libgroupbroadcast_ids(file_name, content, active_extract_dir, addon_ctx, lua_issues)
    _check_lua_global_variable_leaks(content, raw_lines, addon_ctx, lua_issues, move_to_table_hits=move_to_table_hits)
    lua_suggestions = _check_lua_global_tables_and_locals(
        comment_free_lua, raw_lines, clean_lines_list, lua_file_count, addon_ctx, lua_issues, dep_globals_set=dep_globals_set, file_name=file_name
    )
    if move_to_table_hits:
        formatted_mtt = "\n".join(f"    {ln}: --{orig}" for ln, orig in move_to_table_hits)
        lua_suggestions.append(
            "Move to your global addon table instead:\n" + formatted_mtt
        )

    # Disabled for now due to false-positives on valid error/status notices during load:
    # _check_lua_startup_chat_spam(comment_free_lua, raw_lines, lua_suggestions, addon_ctx)
    ai_slop_block = _check_lua_ai_slop_patterns(content, raw_lines)

    if lua_issues:
        print(f"    ├── {C.RED}[FAIL]{C.RESET} Static rule violations detected ({len(lua_issues)}):")
        summary_reasons = []
        for issue in lua_issues:
            short_reason = next(iter(issue.split(":", 1))).strip()
            if short_reason not in summary_reasons:
                summary_reasons.append(short_reason)
        for s in lua_suggestions:
            if "without a local reference" in s and "Multiple access to same global variable without local reference" not in summary_reasons:
                summary_reasons.append("Multiple access to same global variable without local reference")
            elif "Startup Chat Spam" in s and "Startup chat spam detected" not in summary_reasons:
                summary_reasons.append("Startup chat spam detected")
        for reason in summary_reasons:
            print_wrapped_tree_item(f"- {reason}", color=C.RED)
        print(f"    └── {C.RED}See report for full line-by-line details.{C.RESET}")
        issues_str = "\n".join(["  - " + issue for issue in lua_issues])
        sugg_str = "\n".join(["  - " + s for s in lua_suggestions]) if lua_suggestions else "None"
        return "[STATUS] FAIL\n[CRITICAL VIOLATIONS]\n" + issues_str + "\n[BEST PRACTICE SUGGESTIONS]\n" + sugg_str + ai_slop_block

    clean_code_for_words = strip_lua_strings_preserve_lines(comment_free_lua)
    flattened_content = re.sub(r'\s+', ' ', clean_code_for_words)
    table_keys_to_ignore = set()
    for block in re.findall(r'\{([^{}]+)\}', flattened_content):
        table_keys_to_ignore.update(re.findall(r'(?<!\[)\b([A-Za-z_][A-Za-z0-9_]*)\b\s*=', block))

    local_defs = _collect_lua_local_identifiers(clean_code_for_words)
    all_words = set(re.findall(r'(?<![.:])\b([A-Za-z_][A-Za-z0-9_]*)\b', clean_code_for_words))
    words_to_check = all_words - LUA_KEYWORDS - table_keys_to_ignore - local_defs

    parts_or_stem = file_name.replace("\\", "/").split("/") if ("\\" in file_name or "/" in file_name) else os.path.splitext(file_name)
    addon_main_namespace = next(iter(parts_or_stem))
    blessed_keywords = {str(addon_main_namespace)} | addon_ctx["all_global_tables"] | addon_ctx.get("dynamic_globals", set())

    candidate_unknowns = []
    cross_ref_start = datetime.now()
    for word in words_to_check:
        if word not in ESOUI_RAM_DICTIONARY and word not in blessed_keywords:
            if len(word) >= 3 and (word.startswith(("Get", "Set", "Is", "ZO_")) or word.isupper()):
                candidate_unknowns.append(word)

    duration_ms = (datetime.now() - cross_ref_start).total_seconds() * 1000
    print(f"    ├── {C.CYAN}Instant RAM Lookup finished in {C.MAGENTA}{duration_ms:.2f} ms{C.CYAN}.{C.RESET}")

    unverified_identifiers = []
    if candidate_unknowns:
        candidate_unknowns.sort()
        print(f"    ├── {C.YELLOW}Unknown globals detected:{C.RESET} {', '.join(candidate_unknowns)}")
        print(f"    │     {C.CYAN}Searching in ESO AddOns folder for Dependency defined globals...{C.RESET}")
        for word in candidate_unknowns:
            if word in dep_globals_map:
                print(f"    │     {C.GREEN}[OK]{C.RESET}  {word} -> {dep_globals_map[word]}")
            else:
                print(f"    │     {C.RED}[NOK]{C.RESET} {word} -> Not found in dependencies")
                unverified_identifiers.append(word)

    if not unverified_identifiers:
        if lua_suggestions:
            print(f"    ├── {C.WHITE}{len(lua_suggestions)}{C.CYAN} best practice suggestions added to report{C.RESET}")
            print(f"    └── {C.GREEN}[PASS]{C.RESET} Static check passed.")
            return "[STATUS] PASS\n[CRITICAL VIOLATIONS] None\n[BEST PRACTICE SUGGESTIONS]\n" + "\n".join(["  - " + s for s in lua_suggestions]) + ai_slop_block
        if ai_slop_block:
            print(f"    ├── {C.CYAN}Potential AI code hints added to report{C.RESET}")
        print(f"    └── {C.GREEN}[PASS]{C.RESET} Static check passed.")
        return "[STATUS] PASS" + ai_slop_block

    unverified_identifiers.sort()
    print(f"    └── {C.BLUE}[QUEUE FOR AI]{C.RESET} {C.CYAN}Unverified globals: {', '.join(unverified_identifiers[:15])}{C.RESET}")
    BATCH_LEAK_TRACKER[file_name] = list(unverified_identifiers)
    if lua_suggestions:
        BATCH_BEST_PRACTICE_TRACKER[file_name] = list(lua_suggestions)
    if ai_slop_block:
        BATCH_BEST_PRACTICE_TRACKER[file_name].append(ai_slop_block.lstrip("\n"))

    clean_lines = [line for line in content.splitlines() if line.strip() and not line.strip().startswith("--")]
    pre_notes = ("=== LOCAL BEST PRACTICE FINDINGS ===\n" + "\n".join(lua_suggestions) + "\n\n") if lua_suggestions else ""
    return pre_notes + "=== UNVERIFIED GLOBALS ===\n" + ", ".join(unverified_identifiers) + "\n\n" + "\n".join(clean_lines)
