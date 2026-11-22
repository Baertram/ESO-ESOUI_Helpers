"""
In-Memory ESO-API-Indexierung, undocumented globals, Event-Signatur-Parser und Dependency-Globals-Resolver.
"""

import fnmatch
import hashlib
import json
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime

from src.esoui_config import (
    C,
    CACHE_ADDONS_DIR,
    CACHE_ADDONS_EXTRACTED_DIR,
    DEPENDENCY_CACHE_FILE,
    ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX,
    ESO_ADDONS_DIR,
    ESO_API_DOC_FILE,
    ESO_EXTRA_GLOBALS_FILE,
    ESO_LIVE_SOURCE_DIR,
    ESO_UNDOCUMENTED_GLOBALS_FILE,
    EXCLUDED_DEPENDENCY_ADDON_FOLDERS,
    EXCLUDED_DEPENDENCY_FILES,
    PC_IGNORED_SUBDIRS,
    make_clickable_file_link,
    resolve_config_file_path,
)


def _is_pc_ignored_rel_path(rel_path):
    """Returns True if any directory segment in rel_path is Console, XB1, Playstation, Internal, or Future."""
    norm = rel_path.replace("\\", "/").strip("/")
    if not norm:
        return False
    parts = [p.lower() for p in norm.split("/")[:-1] if p]
    return any(seg in PC_IGNORED_SUBDIRS for seg in parts)


def _find_addon_manifest_file(folder_path, expected_stem=None):
    """Finds the primary .addon or .txt manifest inside folder_path."""
    if not folder_path or not os.path.isdir(folder_path):
        return None
    stem = expected_stem or os.path.basename(os.path.normpath(folder_path))
    for ext in (".addon", ".txt"):
        cand = os.path.join(folder_path, stem + ext)
        if os.path.isfile(cand):
            return cand
    for fname in sorted(os.listdir(folder_path)):
        if fname.lower().endswith((".addon", ".txt")):
            cand_p = os.path.join(folder_path, fname)
            if os.path.isfile(cand_p):
                try:
                    with open(cand_p, "r", encoding="utf-8", errors="ignore") as chk_f:
                        head = chk_f.read(2048).lstrip("\ufeff")
                    if re.search(r"^\s*##\s*(?:Title|AddOnVersion)\s*:", head, flags=re.MULTILINE | re.IGNORECASE):
                        return cand_p
                except Exception:
                    pass
    return None


def _read_manifest_version_info(folder_path, expected_stem=None):
    """Reads '## AddOnVersion:' (int) and fallback '## Version:' (str) from an add-on's manifest."""
    mf_path = _find_addon_manifest_file(folder_path, expected_stem=expected_stem)
    if not mf_path:
        return None
    add_on_ver = None
    ver_str = ""
    try:
        with open(mf_path, "r", encoding="utf-8", errors="ignore") as fh:
            for raw_line in fh:
                line = raw_line.lstrip("\ufeff").strip()
                m_av = re.match(r"^##\s*AddOnVersion\s*:\s*(\d+)", line, flags=re.IGNORECASE)
                if m_av and add_on_ver is None:
                    add_on_ver = int(m_av.group(1))
                m_v = re.match(r"^##\s*Version\s*:\s*(.+)$", line, flags=re.IGNORECASE)
                if m_v and not ver_str:
                    ver_str = m_v.group(1).strip()
    except Exception:
        return None
    return {"add_on_version": add_on_ver, "version_str": ver_str, "manifest_path": mf_path}


# Session and disk caches for dependency globals, local AddOns manifests, and ESO API lookup tables
ESO_WORD_CACHE = {}
DEPENDENCY_GLOBALS_CACHE = {}
DEPENDENCY_DISK_CACHE_LOADED = False
DEPENDENCY_CACHE_SCHEMA = 6
LOCAL_ADDONS_MANIFEST_INDEX = None
ESOUI_RAM_DICTIONARY = {}
ESOUI_GLOBAL_DEFINES = set()
ESOUI_UNDOCUMENTED_SET = set()
ESOUI_INDEX_BUILT = False

# Parsed event parameter signatures and capability sets from ESOUIDocumentation.txt
ESOUI_EVENT_PARAM_TYPES = {}
ESOUI_EVENT_HAS_UNIT_TAG = set()
ESOUI_EVENT_HAS_GAMEPAD_MODE = set()
def parse_event_signatures_from_api_doc(lines):
    """
    Parst Event-Signaturen aus ESOUIDocumentation.txt, z. B.:
      * EVENT_UNIT_CREATED (*string* _unitTag_)
      * EVENT_GAMEPAD_PREFERRED_MODE_CHANGED (*bool* _gamepadPreferred_)
    Befuellt ESOUI_EVENT_PARAM_TYPES, ESOUI_EVENT_HAS_UNIT_TAG und ESOUI_EVENT_HAS_GAMEPAD_MODE.
    """
    event_rx = re.compile(r"^\*\s*(EVENT_[A-Z0-9_]+)\s*(?:\(([^)]*)\))?")
    param_rx = re.compile(r"\*([^*]+)\*\s*_([^_]+)_")

    for raw_line in lines:
        s = raw_line.strip()
        if not s.startswith("* EVENT_"):
            continue
        m = event_rx.match(s)
        if not m:
            continue
        ev_name = m.group(1)
        raw_params = m.group(2) or ""
        parsed_params = []
        for pm in param_rx.finditer(raw_params):
            p_type = pm.group(1).strip()
            p_name = pm.group(2).strip()
            parsed_params.append((p_type, p_name))
            low_name = p_name.lower()
            low_type = p_type.lower()
            if "unittag" in low_name or "unittag" in low_type:
                ESOUI_EVENT_HAS_UNIT_TAG.add(ev_name)
            if "gamepadpreferred" in low_name or "showingamepadpreferredmode" in low_name:
                ESOUI_EVENT_HAS_GAMEPAD_MODE.add(ev_name)
        ESOUI_EVENT_PARAM_TYPES[ev_name] = parsed_params


# Memoization table for expanded XML virtual template child suffixes
_XML_TEMPLATE_EXPANSION_MEMO = {}


def extract_resolved_xml_control_names(xml_text, template_children_map=None):
    """
    Resolves hierarchical ESO XML control names including $(parent), $(parentParent),
    $(grandparent), and inherited virtual control children across nested XML tags.
    Returns [(resolved_name, line_no), ...].
    """
    if not xml_text or "name" not in xml_text:
        return []

    clean_xml = re.sub(
        r"<!--.*?-->",
        lambda m: "\n" * m.group(0).count("\n"),
        xml_text,
        flags=re.DOTALL,
    )
    clean_xml = re.sub(
        r"<(On[A-Za-z0-9_]+|UpdateFunction)\b[^/>]*>.*?</\1>",
        lambda m: "\n" * m.group(0).count("\n"),
        clean_xml,
        flags=re.DOTALL,
    )

    tag_rx = re.compile(r"<(/?)([A-Za-z_][A-Za-z0-9_:-]*)([^<>]*?)(/?)>", flags=re.DOTALL)
    name_attr_rx = re.compile(r'\bname\s*=\s*["\']([^"\']+)["\']')
    inherits_attr_rx = re.compile(r'\binherits\s*=\s*["\']([^"\']+)["\']')
    parent_token_rx = re.compile(r"\$\((parent(?:Parent)*|grandparent)\)", flags=re.IGNORECASE)
    tag_stack = []
    resolved_list = []

    def _resolve_placeholders(raw_name):
        if "$(" not in raw_name:
            return raw_name
        ancestors = [r_name for _, r_name in reversed(tag_stack) if r_name]
        if not ancestors:
            return raw_name

        def _repl(match):
            tok = match.group(1).lower()
            if tok == "grandparent":
                idx = 1
            else:
                idx = (len(tok) // 6) - 1
            if 0 <= idx < len(ancestors):
                return ancestors[idx]
            return match.group(0)

        return parent_token_rx.sub(_repl, raw_name)

    def _expand_inherited_suffixes(base_tpl_name, active_stack=None, depth=0):
        if not template_children_map or depth > 4:
            return ()
        if base_tpl_name in _XML_TEMPLATE_EXPANSION_MEMO:
            return _XML_TEMPLATE_EXPANSION_MEMO[base_tpl_name]
        if active_stack is None:
            active_stack = set()
        if base_tpl_name in active_stack:
            return ()
        entry = template_children_map.get(base_tpl_name)
        if not entry:
            return ()
        active_stack.add(base_tpl_name)
        if isinstance(entry, dict):
            result_suffixes = set(entry.get("children") or ())
            for parent_tpl in (entry.get("parents") or ()):
                result_suffixes.update(_expand_inherited_suffixes(parent_tpl, active_stack, depth + 1))
            for sub_prefix, sub_tpl in (entry.get("sub_inherits") or ()):
                if len(result_suffixes) >= 500:
                    break
                for nested_sfx in _expand_inherited_suffixes(sub_tpl, active_stack, depth + 1):
                    result_suffixes.add(f"{sub_prefix}{nested_sfx}")
                    if len(result_suffixes) >= 500:
                        break
            frozen_res = tuple(result_suffixes)
        else:
            frozen_res = tuple(entry)
        active_stack.remove(base_tpl_name)
        _XML_TEMPLATE_EXPANSION_MEMO[base_tpl_name] = frozen_res
        return frozen_res

    for m in tag_rx.finditer(clean_xml):
        is_closing, tag_name, attrs, is_self_closing = m.groups()
        if is_closing:
            for i in range(len(tag_stack) - 1, -1, -1):
                if tag_stack[i][0].lower() == tag_name.lower():
                    del tag_stack[i:]
                    break
            continue
        resolved_name = None
        nm = name_attr_rx.search(attrs)
        if nm:
            candidate = _resolve_placeholders(nm.group(1).strip())
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", candidate):
                resolved_name = candidate
                line_no = clean_xml.count("\n", 0, m.start()) + 1
                resolved_list.append((resolved_name, line_no))
                if template_children_map:
                    inh_m = inherits_attr_rx.search(attrs)
                    if inh_m:
                        for base_tpl in inh_m.group(1).split():
                            for suffix_rel in _expand_inherited_suffixes(base_tpl.strip()):
                                full_inh_name = f"{resolved_name}{suffix_rel}"
                                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", full_inh_name):
                                    resolved_list.append((full_inh_name, line_no))

        if not is_self_closing:
            tag_stack.append((tag_name, resolved_name))

    return resolved_list


def _collect_xml_templates_from_source(x_txt, xml_template_children, inherited_target_names=None):
    """Extracts XML control/template $(parent) child hierarchies and inherits rapidly without backtracking."""
    if not x_txt or ("$(parent)" not in x_txt and "inherits" not in x_txt):
        return
    clean_xml = re.sub(r"<!--.*?-->", "", x_txt, flags=re.DOTALL)
    clean_xml = re.sub(r"<(On[A-Za-z0-9_]+|UpdateFunction)\b[^/>]*>.*?</\1>", "", clean_xml, flags=re.DOTALL)
    tag_rx = re.compile(r"<(/?)([A-Za-z_][A-Za-z0-9_:-]*)([^<>]*?)(/?)>", flags=re.DOTALL)
    name_rx = re.compile(r'\bname\s*=\s*["\']([^"\']+)["\']')
    virtual_rx = re.compile(r'\bvirtual\s*=\s*["\']true["\']', flags=re.IGNORECASE)
    inherits_rx = re.compile(r'\binherits\s*=\s*["\']([^"\']+)["\']')

    active_templates = []
    tag_depth = 0

    for m in tag_rx.finditer(clean_xml):
        is_closing, tag_name, attrs, is_self_closing = m.groups()
        if is_closing:
            tag_depth = max(0, tag_depth - 1)
            while active_templates and active_templates[-1].__getitem__(0) >= tag_depth:
                active_templates.pop()
            for tpl_frame in active_templates:
                rel_stack = tpl_frame.__getitem__(2)
                while rel_stack and rel_stack[-1].__getitem__(0) >= tag_depth:
                    rel_stack.pop()
            continue

        nm = name_rx.search(attrs)
        raw_name = nm.group(1).strip() if nm else ""

        if active_templates and "$(parent)" in raw_name.lower():
            inh_m_child = inherits_rx.search(attrs)
            child_bases = [b.strip() for b in inh_m_child.group(1).split()] if inh_m_child else []
            for _, tpl_name, rel_stack in active_templates:
                parent_prefix = next((p_pfx for _, p_pfx in reversed(rel_stack) if p_pfx is not None), "")
                resolved_rel = re.sub(r"\$\(parent\)", parent_prefix, raw_name, flags=re.IGNORECASE)
                if re.match(r"^[A-Za-z0-9_]+$", resolved_rel):
                    tpl_bucket = xml_template_children.setdefault(tpl_name, {"children": set(), "parents": [], "sub_inherits": []})
                    tpl_bucket["children"].add(resolved_rel)
                    for cb in child_bases:
                        if cb:
                            tpl_bucket.setdefault("sub_inherits", []).append((resolved_rel, cb))
                    if not is_self_closing:
                        rel_stack.append((tag_depth, resolved_rel))

        is_target_tpl = bool(virtual_rx.search(attrs)) or bool(inherited_target_names and raw_name in inherited_target_names)
        if is_target_tpl and raw_name and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", raw_name):
            tpl_entry = xml_template_children.setdefault(raw_name, {"children": set(), "parents": []})
            inh_m = inherits_rx.search(attrs)
            if inh_m:
                for p_tpl in inh_m.group(1).split():
                    p_clean = p_tpl.strip()
                    if p_clean and p_clean not in tpl_entry["parents"]:
                        tpl_entry["parents"].append(p_clean)
            if not is_self_closing:
                active_templates.append((tag_depth, raw_name, [(tag_depth, "")]))

        if not is_self_closing:
            tag_depth += 1
def extract_virtual_controls_from_lua(lua_text, xml_templates_map=None):
    """
    Extracts global control names created via CreateControlFromVirtual("Prefix", parent, "Template", suffix)
    or WINDOW_MANAGER:CreateControlFromVirtual(...), including child $(parent) suffixes if xml_templates_map is provided.
    Returns [(global_name, line_no), ...].
    """
    if not lua_text or "CreateControlFromVirtual" not in lua_text:
        return []

    clean_lua = re.sub(
        r"--\[\[.*?\]\]",
        lambda m: "\n" * m.group(0).count("\n"),
        lua_text,
        flags=re.DOTALL,
    )
    clean_lua = re.sub(r"--.*$", "", clean_lua, flags=re.MULTILINE)

    call_rx = re.compile(
        r"""\bCreateControlFromVirtual\s*\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*,\s*[^,]+,\s*["']([A-Za-z_][A-Za-z0-9_]*)["'](?:\s*,\s*([^)]+))?\)"""
    )

    results = []
    for m in call_rx.finditer(clean_lua):
        base_name, template_name, raw_suffix = m.group(1), m.group(2), (m.group(3) or "").strip()
        line_no = clean_lua.count("\n", 0, m.start()) + 1

        suffixes = []
        if not raw_suffix:
            suffixes.append("")
        elif re.match(r"^\d+$", raw_suffix):
            suffixes.append(raw_suffix)
        else:
            str_m = re.match(r"""^["']([A-Za-z0-9_]*)["']$""", raw_suffix)
            if str_m:
                suffixes.append(str_m.group(1))
            else:
                suffixes.append("")

        for sfx in suffixes:
            full_ctrl = f"{base_name}{sfx}"
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", full_ctrl):
                results.append((full_ctrl, line_no))
                if xml_templates_map and template_name in xml_templates_map:
                    for child_rel in xml_templates_map[template_name]:
                        results.append((f"{full_ctrl}{child_rel}", line_no))

    return results


def _is_excluded_dependency_file(short_rel_display):
    """Checks whether '/<AddonFolder>/<SubPath>' matches any pattern in EXCLUDED_DEPENDENCY_FILES."""
    if not EXCLUDED_DEPENDENCY_FILES:
        return False
    norm_target = "/" + short_rel_display.replace("\\", "/").lstrip("/").lower()
    for raw_pat in EXCLUDED_DEPENDENCY_FILES:
        if not raw_pat or not isinstance(raw_pat, str):
            continue
        norm_pat = "/" + raw_pat.strip().replace("\\", "/").lstrip("/").lower()
        if fnmatch.fnmatch(norm_target, norm_pat):
            return True
    return False


def _compute_dir_fingerprint(dir_path, addon_folder_label=None):
    """Computes a fast SHA-256 fingerprint over all non-excluded relative file paths, sizes, and mtimes."""
    if not os.path.isdir(dir_path):
        return None
    hasher = hashlib.sha256()
    entries = []
    for root, dirs, files in os.walk(dir_path):
        dirs[:] = sorted(d for d in dirs if d.lower() not in PC_IGNORED_SUBDIRS)
        for fn in sorted(files):
            full_p = os.path.join(root, fn)
            rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
            if _is_pc_ignored_rel_path(rel_p):
                continue
            if addon_folder_label and _is_excluded_dependency_file(f"/{addon_folder_label}/{rel_p}"):
                continue
            try:
                st = os.stat(full_p)
                entries.append(f"{rel_p}|{st.st_size}|{st.st_mtime_ns}")
            except OSError:
                entries.append(f"{rel_p}|0|0")
    hasher.update("\n".join(entries).encode("utf-8"))
    return hasher.hexdigest()


def _load_dependency_disk_cache(cache_path=None):
    """Loads persisted per-addon dependency globals from Cache/dependency_globals_cache.json."""
    global DEPENDENCY_DISK_CACHE_LOADED
    if cache_path is None:
        cache_path = DEPENDENCY_CACHE_FILE
    if DEPENDENCY_DISK_CACHE_LOADED:
        return
    DEPENDENCY_DISK_CACHE_LOADED = True

    if not os.path.isfile(cache_path):
        return
    try:
        with open(cache_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            for dep_name, entry in data.items():
                if (
                    isinstance(entry, dict)
                    and entry.get("schema") == DEPENDENCY_CACHE_SCHEMA
                    and isinstance(entry.get("globals"), dict)
                ):
                    DEPENDENCY_GLOBALS_CACHE[dep_name] = {
                        "schema": DEPENDENCY_CACHE_SCHEMA,
                        "hash": entry.get("hash"),
                        "globals": entry["globals"],
                    }
    except (OSError, json.JSONDecodeError):
        pass
def _save_dependency_disk_cache(cache_path=None):
    """Atomically persists DEPENDENCY_GLOBALS_CACHE to Cache/dependency_globals_cache.json."""
    if cache_path is None:
        cache_path = DEPENDENCY_CACHE_FILE
    try:
        parent = os.path.dirname(cache_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp_path = cache_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(DEPENDENCY_GLOBALS_CACHE, fh, indent=2, ensure_ascii=False)
        os.replace(tmp_path, cache_path)
    except OSError:
        pass


def parse_undocumented_globals_lines(lines):
    """
    Parses undocumented ESO globals from Lua lines while skipping false-positives
    listed between '-- 8. Variables to check' and '-- 9. Other Undocumented Variables'.
    """
    valid_globals = set()
    skipped_cat8 = set()
    in_category_8 = False
    entry_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=')

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("-- 8."):
            in_category_8 = True
            continue
        if stripped.startswith("-- 9."):
            in_category_8 = False
            continue
        if stripped.startswith("--"):
            continue
        match = entry_pattern.match(stripped)
        if match:
            var_name = str(match.group(1))
            if len(var_name) >= 3:
                if in_category_8:
                    skipped_cat8.add(var_name)
                else:
                    valid_globals.add(var_name)
    return valid_globals, skipped_cat8


def load_undocumented_globals(file_setting):
    """Loads undocumented ESO globals from disk; skips gracefully with a log message if missing."""
    resolved_path = resolve_config_file_path(file_setting)
    if not resolved_path or not os.path.exists(resolved_path):
        print(f"{C.CYAN}       [INFO] Undocumented globals file not found, skipping: {resolved_path}{C.RESET}")
        return set(), set()
    try:
        with open(resolved_path, 'r', encoding='utf-8', errors='ignore') as f:
            valid_globals, skipped_cat8 = parse_undocumented_globals_lines(f)
        print(
            f"{C.CYAN}       Loaded {C.WHITE}{len(valid_globals)}{C.CYAN} undocumented ESO globals "
            f"(skipped {C.WHITE}{len(skipped_cat8)}{C.CYAN} false-positives from category \"8\").{C.RESET}"
        )
        return valid_globals, skipped_cat8
    except Exception as e:
        print(f"{C.RED}       Error reading undocumented globals file: {str(e)}{C.RESET}")
        return set(), set()


def build_esoui_index_once():
    """Builds the in-memory lookup dictionary of all valid ESO APIs, globals, constants, and event signatures."""
    global ESOUI_INDEX_BUILT, ESOUI_UNDOCUMENTED_SET
    if ESOUI_INDEX_BUILT:
        return

    print(f"\n{C.CYAN}[INIT] Building lightning-fast keyword dictionary in RAM...{C.RESET}")
    start_time = datetime.now()
    broad_extractor = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')
    top_global_func_rx = re.compile(r'^function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')
    top_global_var_rx = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)')

    if os.path.exists(ESO_API_DOC_FILE):
        try:
            with open(ESO_API_DOC_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                doc_lines = f.readlines()
            parse_event_signatures_from_api_doc(doc_lines)
            for line_num, line in enumerate(doc_lines, 1):
                cleaned_line = line.strip()
                if not cleaned_line or cleaned_line.startswith(("h1.", "h2.", "h3.", "h4.", "h5.", "h6.", "**")):
                    continue

                if cleaned_line.startswith("*"):
                    raw_entry = cleaned_line.lstrip("*").strip()
                    if "(" in raw_entry:
                        raw_string = next(iter(raw_entry.split("(", 1))).strip()
                    else:
                        parts = raw_entry.split()
                        raw_string = next(iter(parts)).strip() if parts else raw_entry
                    clean_match = broad_extractor.search(raw_string)
                    if clean_match:
                        api_name = str(clean_match.group(1)).strip()
                        if len(api_name) >= 3 and api_name not in ESOUI_RAM_DICTIONARY:
                            ESOUI_RAM_DICTIONARY[api_name] = f"API Documentation line {line_num}: {cleaned_line}"
        except Exception as e:
            print(f"{C.RED}       Error indexing API doc: {str(e)}{C.RESET}")
    if os.path.exists(ESO_LIVE_SOURCE_DIR):
        t_phase = datetime.now()
        file_count = 0
        xml_template_children = {}
        all_source_files = []
        xml_texts_cache = []
        inherited_target_names = set()
        inherits_scan_rx = re.compile(r'\binherits\s*=\s*["\']([^"\']+)["\']')
        for root, _, files in os.walk(ESO_LIVE_SOURCE_DIR):
            for file in sorted(files):
                if file.endswith(('.lua', '.xml')):
                    full_p = os.path.join(root, file)
                    all_source_files.append(full_p)
                    if file.lower().endswith('.xml'):
                        try:
                            with open(full_p, 'r', encoding='utf-8', errors='ignore') as xf:
                                x_txt = xf.read()
                            xml_texts_cache.append(x_txt)
                            for im in inherits_scan_rx.finditer(x_txt):
                                for inh_tok in im.group(1).split():
                                    if inh_tok.strip():
                                        inherited_target_names.add(inh_tok.strip())
                        except Exception:
                            pass
        for x_txt in xml_texts_cache:
            try:
                _collect_xml_templates_from_source(x_txt, xml_template_children, inherited_target_names)
            except Exception:
                pass

        _XML_TEMPLATE_EXPANSION_MEMO.clear()
        t_phase = datetime.now()

        module_menu_bars = {}
        module_lua_btn_counts = {}

        def _feature_stem(filename):
            stem = os.path.splitext(filename)[0].lower()
            stem = re.sub(r'_(?:keyboard|gamepad|shared)$', '', stem)
            return stem

        for file_path in all_source_files:
            t_file_start = datetime.now()
            file = os.path.basename(file_path)
            rel_display = os.path.relpath(file_path, ESO_LIVE_SOURCE_DIR).replace("\\", "/")
            feat_key = _feature_stem(file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    full_content = f.read()
                for line in full_content.splitlines():
                    cleaned_line = line.strip()
                    if cleaned_line:
                        if file.lower().endswith('.lua'):
                            m_gfn = top_global_func_rx.match(cleaned_line)
                            if m_gfn:
                                ESOUI_GLOBAL_DEFINES.add(m_gfn.group(1))
                            m_gvar = top_global_var_rx.match(cleaned_line)
                            if m_gvar:
                                ESOUI_GLOBAL_DEFINES.add(m_gvar.group(1))
                        for w in set(broad_extractor.findall(cleaned_line)):
                            if len(w) >= 3 and w not in ESOUI_RAM_DICTIONARY:
                                ESOUI_RAM_DICTIONARY[w] = f"ESOUI Source ({file}): {cleaned_line}"
                if file.lower().endswith('.xml'):
                    for name_val, line_no in extract_resolved_xml_control_names(full_content, xml_template_children):
                        if name_val not in ESOUI_RAM_DICTIONARY:
                            ESOUI_RAM_DICTIONARY[name_val] = f"ESOUI XML Control ({rel_display}:{line_no})"
                        if name_val.endswith("MenuBar") and name_val.startswith("ZO_"):
                            module_menu_bars.setdefault(feat_key, set()).add(name_val)
                elif file.lower().endswith('.lua'):
                    for v_ctrl, line_no in extract_virtual_controls_from_lua(full_content):
                        if v_ctrl not in ESOUI_RAM_DICTIONARY:
                            ESOUI_RAM_DICTIONARY[v_ctrl] = f"ESOUI Virtual Control ({rel_display}:{line_no})"
                    for mb_lit in re.findall(r'\b(ZO_[A-Za-z0-9_]+MenuBar)\b', full_content):
                        module_menu_bars.setdefault(feat_key, set()).add(mb_lit)

                    add_btn_calls = len(re.findall(r'\bZO_MenuBar_AddButton\s*\(', full_content))
                    descriptor_entries = len(re.findall(r'\bdescriptor\s*=', full_content))
                    tab_filter_entries = len(re.findall(r'\bCreateNewTabFilterData\s*\(', full_content))
                    file_btn_count = max(add_btn_calls, descriptor_entries, tab_filter_entries)
                    if file_btn_count > 0:
                        prev_cnt = module_lua_btn_counts.get(feat_key, 0)
                        if file_btn_count > prev_cnt:
                            module_lua_btn_counts[feat_key] = file_btn_count
                    for dyn_m in re.finditer(
                        r"""\bCreateControlFromVirtual\s*\(\s*["']([A-Za-z_][A-Za-z0-9_]*)["']\s*,\s*[^,]+,\s*["'][A-Za-z_][A-Za-z0-9_]*["']\s*,\s*[A-Za-z_][A-Za-z0-9_]*\s*\)""",
                        full_content,
                    ):
                        base_p = dyn_m.group(1)
                        ln_no = full_content.count("\n", 0, dyn_m.start()) + 1
                        for idx_num in range(1, 11):
                            cand_ctrl = f"{base_p}{idx_num}"
                            if cand_ctrl not in ESOUI_RAM_DICTIONARY:
                                ESOUI_RAM_DICTIONARY[cand_ctrl] = f"ESOUI Virtual Control ({rel_display}:{ln_no})"

                file_count += 1
            except Exception:
                pass
        for feat_key, mb_names in module_menu_bars.items():
            exact_btn_count = module_lua_btn_counts.get(feat_key, 0)
            if exact_btn_count > 0:
                for mb_name in mb_names:
                    for btn_idx in range(1, exact_btn_count + 1):
                        btn_name = f"{mb_name}Button{btn_idx}"
                        if btn_name not in ESOUI_RAM_DICTIONARY:
                            ESOUI_RAM_DICTIONARY[btn_name] = f"ESOUI MenuBar Button ({mb_name})"

        print(f"{C.CYAN}       Indexed {C.WHITE}{file_count}{C.CYAN} source files into keyword mapping.{C.RESET}")

    if os.path.exists(ESO_EXTRA_GLOBALS_FILE):
        try:
            with open(ESO_EXTRA_GLOBALS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                extra_content = f.read()
            for w in set(broad_extractor.findall(extra_content)):
                if len(w) >= 3 and w not in ESOUI_RAM_DICTIONARY:
                    ESOUI_RAM_DICTIONARY[w] = "Custom IDE Global File: " + w
            print(f"{C.CYAN}       Successfully synced your personal IDE completion globals into RAM!{C.RESET}")
        except Exception as e:
            print(f"{C.RED}       Error indexing custom global file: {str(e)}{C.RESET}")

    undoc_valid, _ = load_undocumented_globals(ESO_UNDOCUMENTED_GLOBALS_FILE)
    ESOUI_UNDOCUMENTED_SET.update(undoc_valid)
    ESOUI_GLOBAL_DEFINES.update(undoc_valid)
    for w in undoc_valid:
        if w not in ESOUI_RAM_DICTIONARY:
            ESOUI_RAM_DICTIONARY[w] = "Undocumented ESO Global: " + w

    enum_prefixes = {
        k.split("_", 1)[0]
        for k in list(ESOUI_RAM_DICTIONARY.keys())
        if "_" in k and k.isupper()
    }
    for ep in enum_prefixes:
        for suffix in ("_ITERATION_BEGIN", "_ITERATION_END", "_MIN_VALUE", "_MAX_VALUE"):
            bound_const = f"{ep}{suffix}"
            if bound_const not in ESOUI_RAM_DICTIONARY:
                ESOUI_RAM_DICTIONARY[bound_const] = "ESO C++ Enum Boundary Constant: " + bound_const

    duration = (datetime.now() - start_time).total_seconds()
    print(f"{C.CYAN}-> Indexing finished in {C.MAGENTA}{duration:.2f} seconds{C.CYAN}. All future lookups run in NANOSECONDS!{C.RESET}\n")
    ESOUI_INDEX_BUILT = True


def is_index_built():
    """Returns True once build_esoui_index_once() has populated ESOUI_RAM_DICTIONARY."""
    return ESOUI_INDEX_BUILT


def reset_dependency_globals_cache():
    """Clears the in-memory dependency & local AddOns globals cache."""
    global DEPENDENCY_DISK_CACHE_LOADED, LOCAL_ADDONS_MANIFEST_INDEX
    DEPENDENCY_GLOBALS_CACHE.clear()
    DEPENDENCY_DISK_CACHE_LOADED = False
    LOCAL_ADDONS_MANIFEST_INDEX = None


def get_current_api_version():
    """Reads the current live APIVersion number from the top of ESOUIDocumentation.txt."""
    if os.path.exists(ESO_API_DOC_FILE):
        try:
            with open(ESO_API_DOC_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for _ in range(5):
                    line = f.readline()
                    if not line:
                        break
                    match = re.search(r"API Version\s+(\d+)", line)
                    if match:
                        return match.group(1)
        except Exception as e:
            print(f"{C.RED}-> Error reading current API version from doc: {str(e)}{C.RESET}")
    return None
def parse_manifest_dependencies(manifest_text):
    """Extracts DependsOn, PCDependsOn, and OptionalDependsOn entries (ignores ConsoleDependsOn)."""
    deps = []
    invalid_optional = []
    for raw_line in manifest_text.splitlines():
        line = raw_line.strip()
        m_dep = re.match(r'^##\s*(?:PC)?DependsOn\s*:\s*(.+)$', line, flags=re.IGNORECASE)
        if m_dep:
            for token in m_dep.group(1).split():
                clean_name = next(iter(token.split(">="))).strip()
                if clean_name and clean_name not in deps:
                    deps.append(clean_name)
        m_opt = re.match(r'^##\s*OptionalDependsOn\s*:\s*(.+)$', line, flags=re.IGNORECASE)
        if m_opt:
            for token in m_opt.group(1).split():
                if ">=" in token:
                    invalid_optional.append(token)
                clean_name = next(iter(token.split(">="))).strip()
                if clean_name and clean_name not in deps:
                    deps.append(clean_name)
    return deps, invalid_optional


def _is_extracted_cache_up_to_date(target_dir, pkg_info):
    """Checks if target_dir in Cache/AddOns/_extracted already matches the online version."""
    if not os.path.isdir(target_dir):
        return False
    from src.esoui_filelist_search import compare_version_values

    local_info = _read_manifest_version_info(target_dir)
    if not local_info:
        return False
    rem_av = pkg_info.get("add_on_version")
    loc_av = local_info.get("add_on_version")
    if rem_av is not None and loc_av is not None:
        return loc_av >= rem_av
    rem_vs = pkg_info.get("version_str") or ""
    loc_vs = local_info.get("version_str") or ""
    if rem_vs and loc_vs:
        return compare_version_values(loc_vs, rem_vs) >= 0
    return True


def _ensure_cached_dependency_addon(dep_name, pkg_info, reason_text):
    """
    Ensures the up-to-date dependency ZIP is downloaded to Cache/AddOns/ (overwriting existing ZIPs)
    and extracted 1:1 to Cache/AddOns/_extracted/<top_dir> (deleting existing target dir first).
    Returns the resolved folder path to scan, or None on failure.
    """
    sub_rel = pkg_info.get("sub_path") or dep_name
    extracted_target_dir = os.path.join(CACHE_ADDONS_EXTRACTED_DIR, *sub_rel.split("/"))
    online_ver_disp = (
        f"AddOnVersion {pkg_info['add_on_version']}"
        if pkg_info.get("add_on_version") is not None
        else f"Version {pkg_info.get('version_str') or 'unknown'}"
    )

    if _is_extracted_cache_up_to_date(extracted_target_dir, pkg_info):
        dir_link = make_clickable_file_link(extracted_target_dir, color=C.CYAN)
        print(
            f"    │     {C.YELLOW}⚠ Dependency '{C.WHITE}{dep_name}{C.YELLOW}' ({reason_text}):{C.RESET} "
            f"Loading cached {C.GREEN}{online_ver_disp}{C.RESET} from {dir_link}"
        )
        return extracted_target_dir

    addon_id = pkg_info["addon_id"]
    dl_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"
    print(
        f"    │     {C.YELLOW}⚠ Dependency '{C.WHITE}{dep_name}{C.YELLOW}' ({reason_text}):{C.RESET} "
        f"Downloading latest {C.GREEN}{online_ver_disp}{C.RESET} (ESOUI ID {addon_id})..."
    )

    from src.esoui_download_io import download_zip

    os.makedirs(CACHE_ADDONS_DIR, exist_ok=True)
    tmp_dl_root = os.path.join(CACHE_ADDONS_DIR, "_tmp_dl")
    downloaded_path, zip_filename = download_zip(dl_url, tmp_dl_root, force_download=True)
    if not downloaded_path or not zip_filename or not os.path.isfile(downloaded_path):
        print(f"    │       {C.RED}✖ Failed to download dependency '{dep_name}' (ID {addon_id}).{C.RESET}")
        return None

    final_zip_path = os.path.join(CACHE_ADDONS_DIR, zip_filename)
    try:
        if os.path.isfile(final_zip_path):
            os.remove(final_zip_path)
        shutil.move(downloaded_path, final_zip_path)
        shutil.rmtree(tmp_dl_root, ignore_errors=True)
    except OSError as exc:
        print(f"    │       {C.RED}✖ Failed to store cached ZIP '{final_zip_path}': {exc}{C.RESET}")
        return None
    os.makedirs(CACHE_ADDONS_EXTRACTED_DIR, exist_ok=True)
    try:
        with zipfile.ZipFile(final_zip_path, "r") as zf:
            top_dirs = {
                member.replace("\\", "/").split("/", 1).__getitem__(0)
                for member in zf.namelist()
                if member.strip() and not member.startswith("__MACOSX")
            }
            for td in sorted(top_dirs):
                existing_extracted = os.path.join(CACHE_ADDONS_EXTRACTED_DIR, td)
                if os.path.isdir(existing_extracted):
                    shutil.rmtree(existing_extracted, ignore_errors=True)
                elif os.path.isfile(existing_extracted):
                    os.remove(existing_extracted)
            zf.extractall(CACHE_ADDONS_EXTRACTED_DIR)
    except Exception as exc:
        print(f"    │       {C.RED}✖ Failed to extract '{zip_filename}': {exc}{C.RESET}")
        return None

    final_scan_dir = extracted_target_dir if os.path.isdir(extracted_target_dir) else os.path.join(CACHE_ADDONS_EXTRACTED_DIR, dep_name)
    zip_link = make_clickable_file_link(final_zip_path, color=C.WHITE, display_text=zip_filename)
    dir_link = make_clickable_file_link(final_scan_dir, color=C.CYAN)
    print(
        f"    │       {C.GREEN}✔ Cached {online_ver_disp}{C.RESET} | ZIP: {zip_link} | Extracted: {dir_link}"
    )
    return final_scan_dir if os.path.isdir(final_scan_dir) else None


def collect_dependency_globals(active_extract_dir, extract_lua_globals_fn, current_addon_id=None):
    """
    Scans declared dependencies (local AddOns + auto-cached ESOUI dependencies) and installed
    AddOns to map all external global identifiers to '/live/AddOns/<Dep>/<File>:<Line>'.
    """
    if not ESO_ADDONS_DIR or not os.path.isdir(ESO_ADDONS_DIR):
        return {}

    global LOCAL_ADDONS_MANIFEST_INDEX
    dep_names = []
    checked_addon_names = set()
    bundled_sub_dirs = {}
    if active_extract_dir and os.path.exists(active_extract_dir):
        for root, _, files in os.walk(active_extract_dir):
            for f in files:
                if f.lower().endswith(('.addon', '.txt')):
                    full_mf = os.path.join(root, f)
                    try:
                        with open(full_mf, 'r', encoding='utf-8', errors='ignore') as fh:
                            mf_text = fh.read()
                        if re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', mf_text, flags=re.MULTILINE | re.IGNORECASE):
                            stem_name, _ = os.path.splitext(f)
                            checked_addon_names.add(stem_name.lower())
                            bundled_sub_dirs[stem_name.lower()] = (stem_name, root)
                        found_deps, _ = parse_manifest_dependencies(mf_text)
                        for d in found_deps:
                            if d not in dep_names:
                                dep_names.append(d)
                    except Exception:
                        pass

    excluded_folders_lower = {f.strip().lower() for f in EXCLUDED_DEPENDENCY_ADDON_FOLDERS if f and f.strip()}

    if LOCAL_ADDONS_MANIFEST_INDEX is None:
        idx_map = {}
        try:
            for entry_name in os.listdir(ESO_ADDONS_DIR):
                if entry_name.lower() in excluded_folders_lower:
                    continue
                full_entry = os.path.join(ESO_ADDONS_DIR, entry_name)
                if not os.path.isdir(full_entry):
                    continue
                rev_deps_lower = set()
                for ext in ('.addon', '.txt'):
                    cand_mf = os.path.join(full_entry, entry_name + ext)
                    if os.path.isfile(cand_mf):
                        try:
                            with open(cand_mf, 'r', encoding='utf-8', errors='ignore') as rmf:
                                rev_deps, _ = parse_manifest_dependencies(rmf.read())
                            rev_deps_lower = {rd.lower() for rd in rev_deps}
                        except Exception:
                            pass
                        break
                idx_map[entry_name.lower()] = (entry_name, full_entry, rev_deps_lower)
        except OSError:
            pass
        LOCAL_ADDONS_MANIFEST_INDEX = idx_map
    addons_dir_map = {k: v[1] for k, v in LOCAL_ADDONS_MANIFEST_INDEX.items()}
    if checked_addon_names:
        for low_name, (orig_name, _, rev_deps_lower) in LOCAL_ADDONS_MANIFEST_INDEX.items():
            if low_name not in checked_addon_names and (rev_deps_lower & checked_addon_names):
                if orig_name not in dep_names:
                    dep_names.append(orig_name)

        try:
            from src.esoui_filelist_search import DEFAULT_CACHE_PATH
            if os.path.isfile(DEFAULT_CACHE_PATH):
                with open(DEFAULT_CACHE_PATH, "r", encoding="utf-8") as jfh:
                    cached_fl = json.load(jfh)
                if isinstance(cached_fl, list):
                    for pkg in cached_fl:
                        for sub in (pkg.get("addons") or []):
                            if not isinstance(sub, dict):
                                continue
                            all_sub_deps = (sub.get("requiredDependencies") or []) + (sub.get("optionalDependencies") or [])
                            sub_dep_names = {re.split(r"[><=]", str(d))[0].strip().lower() for d in all_sub_deps}
                            if sub_dep_names & checked_addon_names:
                                sub_folder = str(sub.get("path") or "").replace("\\", "/").split("/")[0].strip()
                                if sub_folder and sub_folder.lower() in addons_dir_map and sub_folder.lower() not in checked_addon_names:
                                    if sub_folder not in dep_names:
                                        dep_names.append(sub_folder)
        except Exception:
            pass

    _load_dependency_disk_cache()
    all_dep_globals = {}
    cache_dirty = False
    scan_start_time = datetime.now()
    spinner_frames = ("|", "/", "-", "\\")
    spinner_idx = 0
    scanned_any_file = False
    scanned_folders_count = 0
    scanned_txt_manifests_count = 0
    scanned_addon_manifests_count = 0
    scanned_lua_count = 0
    scanned_xml_count = 0
    term_cols = shutil.get_terminal_size((100, 20)).columns

    def _update_scan_spinner(rel_file_display):
        nonlocal spinner_idx, scanned_any_file
        scanned_any_file = True
        frame = spinner_frames[spinner_idx % len(spinner_frames)]
        spinner_idx += 1
        prefix = f"    │     {C.CYAN}{frame}{C.RESET} Scanning: "
        max_path_len = max(20, term_cols - 22)
        disp = rel_file_display if len(rel_file_display) <= max_path_len else "..." + rel_file_display[-(max_path_len - 3):]
        sys.stdout.write(f"\r\033[K{prefix}{C.WHITE}{disp}{C.RESET}")
        sys.stdout.flush()

    def _get_or_scan_addon_folder(folder_label, folder_path):
        nonlocal cache_dirty, scanned_folders_count, scanned_txt_manifests_count, scanned_addon_manifests_count, scanned_lua_count, scanned_xml_count

        current_hash = _compute_dir_fingerprint(folder_path, folder_label)

        cached_entry = DEPENDENCY_GLOBALS_CACHE.get(folder_label)
        if (
            isinstance(cached_entry, dict)
            and cached_entry.get("schema") == DEPENDENCY_CACHE_SCHEMA
            and cached_entry.get("hash") == current_hash
            and isinstance(cached_entry.get("globals"), dict)
        ):
            return cached_entry["globals"]

        dep_globals = {}
        manifest_path = None
        for ext in ('.addon', '.txt'):
            candidate = os.path.join(folder_path, folder_label + ext)
            if os.path.isfile(candidate):
                manifest_path = candidate
                break

        if not manifest_path and os.path.isdir(folder_path):
            for fname in sorted(os.listdir(folder_path)):
                if fname.lower().endswith(('.addon', '.txt')):
                    cand_p = os.path.join(folder_path, fname)
                    if os.path.isfile(cand_p):
                        try:
                            with open(cand_p, 'r', encoding='utf-8', errors='ignore') as chk_f:
                                head = chk_f.read(2048).lstrip('\ufeff')
                            if re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', head, flags=re.MULTILINE | re.IGNORECASE):
                                manifest_path = cand_p
                                break
                        except Exception:
                            pass
        if os.path.isdir(folder_path):
            scanned_folders_count += 1

        if manifest_path:
            manifest_basename = os.path.basename(manifest_path)
            if manifest_basename.lower().endswith(".addon"):
                scanned_addon_manifests_count += 1
            else:
                scanned_txt_manifests_count += 1

            try:
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as mf:
                    for m_line_no, raw_line in enumerate(mf, 1):
                        entry = raw_line.lstrip('\ufeff').strip()
                        if not entry:
                            continue
                        sv_match = re.match(r'^##\s*SavedVariables\s*:\s*(.+)$', entry, flags=re.IGNORECASE)
                        if sv_match:
                            sv_rhs = re.split(r'[#;]', sv_match.group(1), maxsplit=1)[0]
                            for sv_name in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', sv_rhs):
                                if sv_name not in dep_globals:
                                    dep_globals[sv_name] = f"/live/AddOns/{folder_label}/{manifest_basename}:{m_line_no}"
                            continue
                        if entry.startswith('#') or entry.startswith(';') or '$(' in entry:
                            continue
                        norm_entry = entry.replace('\\', '/')
                        if _is_pc_ignored_rel_path(norm_entry):
                            continue
                        rel_file = norm_entry.replace('/', os.sep)
                        target_file = os.path.join(folder_path, rel_file)
                        if os.path.isfile(target_file):
                            short_rel_display = f"/{folder_label}/{norm_entry}"
                            if _is_excluded_dependency_file(short_rel_display):
                                continue
                            is_cached_src = os.path.abspath(folder_path).startswith(os.path.abspath(CACHE_ADDONS_EXTRACTED_DIR))
                            rel_display = f"/Cache/AddOns/_extracted{short_rel_display}" if is_cached_src else f"/live/AddOns{short_rel_display}"

                            _update_scan_spinner(short_rel_display)

                            with open(target_file, 'r', encoding='utf-8', errors='ignore') as tf:
                                file_text = tf.read()

                            if target_file.lower().endswith('.lua'):
                                scanned_lua_count += 1
                                dep_globals.update(extract_lua_globals_fn(file_text, rel_display))
                                for v_ctrl, line_no in extract_virtual_controls_from_lua(file_text):
                                    if v_ctrl not in dep_globals:
                                        dep_globals[v_ctrl] = f"{rel_display}:{line_no}"
                                no_comments = re.sub(r'--\[\[.*?\]\]', lambda m: '\n' * m.group(0).count('\n'), file_text, flags=re.DOTALL)
                                no_comments = re.sub(r'--.*$', '', no_comments, flags=re.MULTILINE)
                                has_dyn_g = bool(re.search(r'\b_G\s*\[[^\]]+\]\s*=', no_comments))
                                for sm in re.finditer(r'["\']([A-Za-z_][A-Za-z0-9_]*)["\']', no_comments):
                                    s_ident = sm.group(1)
                                    if s_ident not in dep_globals and (has_dyn_g or re.match(r'^[A-Z][A-Z0-9_]{2,}$', s_ident)):
                                        line_no = no_comments.count('\n', 0, sm.start(1)) + 1
                                        dep_globals[s_ident] = f"{rel_display}:{line_no}"
                                if has_dyn_g:
                                    for km in re.finditer(r'(?<![A-Za-z0-9_.:])\b([A-Z][A-Z0-9_]{2,})\b\s*=(?!=)', no_comments):
                                        k_ident = km.group(1)
                                        if k_ident not in dep_globals:
                                            line_no = no_comments.count('\n', 0, km.start(1)) + 1
                                            dep_globals[k_ident] = f"{rel_display}:{line_no}"
                            elif target_file.lower().endswith('.xml'):
                                scanned_xml_count += 1
                                for g_name, line_no in extract_resolved_xml_control_names(file_text):
                                    if g_name not in dep_globals:
                                        dep_globals[g_name] = f"{rel_display}:{line_no}"
            except Exception:
                pass

        DEPENDENCY_GLOBALS_CACHE[folder_label] = {
            "schema": DEPENDENCY_CACHE_SCHEMA,
            "hash": current_hash,
            "globals": dep_globals,
        }
        cache_dirty = True
        return dep_globals

    from src.esoui_filelist_search import compare_version_values, resolve_dependency_online_package

    cur_id_str = str(current_addon_id).strip() if current_addon_id is not None else ""
    scanned_lowers = set(checked_addon_names) | excluded_folders_lower
    for dep in dep_names:
        low_d = dep.lower()
        if low_d in excluded_folders_lower:
            continue
        scanned_lowers.add(low_d)
        if low_d in bundled_sub_dirs:
            b_name, b_dir = bundled_sub_dirs[low_d]
            all_dep_globals.update(_get_or_scan_addon_folder(f"bundled:{b_name}", b_dir))
            continue

        if low_d in LOCAL_ADDONS_MANIFEST_INDEX:
            orig_name, dep_dir, _ = LOCAL_ADDONS_MANIFEST_INDEX[low_d]
        else:
            orig_name, dep_dir = dep, os.path.join(ESO_ADDONS_DIR, dep)

        online_pkg = resolve_dependency_online_package(orig_name)
        use_cached_dir = None
        if online_pkg and (not cur_id_str or str(online_pkg.get("addon_id") or "").strip() != cur_id_str):
            if not os.path.isdir(dep_dir):
                use_cached_dir = _ensure_cached_dependency_addon(orig_name, online_pkg, "not installed in live/AddOns")
            else:
                loc_ver = _read_manifest_version_info(dep_dir, expected_stem=orig_name)
                rem_av = online_pkg.get("add_on_version")
                loc_av = loc_ver.get("add_on_version") if loc_ver else None
                is_outdated = False
                reason_msg = ""
                if rem_av is not None and loc_av is not None and loc_av < rem_av:
                    is_outdated = True
                    reason_msg = f"local AddOnVersion {loc_av} < online {rem_av}"
                elif rem_av is None and loc_ver:
                    rem_vs = online_pkg.get("version_str") or ""
                    loc_vs = loc_ver.get("version_str") or ""
                    if rem_vs and loc_vs and compare_version_values(loc_vs, rem_vs) < 0:
                        is_outdated = True
                        reason_msg = f"local Version '{loc_vs}' < online '{rem_vs}'"
                if is_outdated:
                    use_cached_dir = _ensure_cached_dependency_addon(orig_name, online_pkg, reason_msg)

        scan_target_dir = use_cached_dir if use_cached_dir else dep_dir
        scan_cache_key = f"cache:{orig_name}" if use_cached_dir else orig_name
        all_dep_globals.update(_get_or_scan_addon_folder(scan_cache_key, scan_target_dir))

    for low_name, (orig_name, folder_path, _) in sorted(LOCAL_ADDONS_MANIFEST_INDEX.items()):
        if low_name in scanned_lowers:
            continue
        scanned_lowers.add(low_name)
        folder_globals = _get_or_scan_addon_folder(orig_name, folder_path)
        for g_key, g_loc in folder_globals.items():
            if g_key not in all_dep_globals:
                all_dep_globals[g_key] = f"{g_loc} (installed addon)"

    if scanned_any_file:
        scan_elapsed = (datetime.now() - scan_start_time).total_seconds()
        sys.stdout.write(
            f"\r\033[K    │     {C.GREEN}✔{C.RESET} Dependency & AddOns scan completed in {C.MAGENTA}{scan_elapsed:.2f}{C.RESET} seconds.\n"
            f"    │       {C.CYAN}Scanned {C.WHITE}{scanned_folders_count}{C.CYAN} add-on folder(s): "
            f"{C.WHITE}{scanned_txt_manifests_count}{C.CYAN} .txt, "
            f"{C.WHITE}{scanned_addon_manifests_count}{C.CYAN} .addon, "
            f"{C.WHITE}{scanned_lua_count}{C.CYAN} .lua, "
            f"{C.WHITE}{scanned_xml_count}{C.CYAN} .xml.{C.RESET}\n"
        )
        sys.stdout.flush()

    if cache_dirty:
        _save_dependency_disk_cache()

    return all_dep_globals
