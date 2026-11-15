"""
In-Memory ESO-API-Indexierung, undocumented globals und Dependency-Globals-Resolver.
"""

import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime



from src.esoui_config import (
    C,
    ESO_ADDONS_DIR,
    ESO_API_DOC_FILE,
    ESO_EXTRA_GLOBALS_FILE,
    ESO_LIVE_SOURCE_DIR,
    ESO_UNDOCUMENTED_GLOBALS_FILE,
    resolve_config_file_path,
)

ESO_WORD_CACHE = {}
DEPENDENCY_GLOBALS_CACHE = {}
DEPENDENCY_DISK_CACHE_LOADED = False
DEPENDENCY_CACHE_SCHEMA = 6
DEPENDENCY_CACHE_FILE = os.path.join("Cache", "dependency_globals_cache.json")
LOCAL_ADDONS_MANIFEST_INDEX = None
ESOUI_RAM_DICTIONARY = {}
ESOUI_UNDOCUMENTED_SET = set()
ESOUI_INDEX_BUILT = False


def extract_resolved_xml_control_names(xml_text):
    """
    Resolves hierarchical ESO XML control names including $(parent), $(parentParent),
    $(grandparent), etc. across nested XML tags, returning [(resolved_name, line_no), ...].
    """
    if not xml_text or "name" not in xml_text:
        return []

    clean_xml = re.sub(
        r"<!--.*?-->",
        lambda m: "\n" * m.group(0).count("\n"),
        xml_text,
        flags=re.DOTALL,
    )

    tag_rx = re.compile(r"<(/?)([A-Za-z_][A-Za-z0-9_:-]*)([^<>]*?)(/?)>", flags=re.DOTALL)
    name_attr_rx = re.compile(r'\bname\s*=\s*["\']([^"\']+)["\']')
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

        if not is_self_closing:
            tag_stack.append((tag_name, resolved_name))

    return resolved_list


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


def _compute_dir_fingerprint(dir_path):
    """Computes a fast SHA-256 fingerprint over all relative file paths, sizes, and mtimes in dir_path."""
    if not os.path.isdir(dir_path):
        return None
    hasher = hashlib.sha256()
    entries = []
    for root, dirs, files in os.walk(dir_path):
        dirs.sort()
        for fn in sorted(files):
            full_p = os.path.join(root, fn)
            rel_p = os.path.relpath(full_p, dir_path).replace("\\", "/")
            try:
                st = os.stat(full_p)
                entries.append(f"{rel_p}|{st.st_size}|{st.st_mtime_ns}")
            except OSError:
                entries.append(f"{rel_p}|0|0")
    hasher.update("\n".join(entries).encode("utf-8"))
    return hasher.hexdigest()


def _load_dependency_disk_cache(cache_path=DEPENDENCY_CACHE_FILE):
    """Loads persisted per-addon dependency globals from Cache/dependency_globals_cache.json."""
    global DEPENDENCY_DISK_CACHE_LOADED
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


def _save_dependency_disk_cache(cache_path=DEPENDENCY_CACHE_FILE):
    """Atomically persists DEPENDENCY_GLOBALS_CACHE to Cache/dependency_globals_cache.json."""
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
    """Builds the in-memory lookup dictionary of all valid ESO APIs, globals, and constants."""
    global ESOUI_INDEX_BUILT, ESOUI_UNDOCUMENTED_SET
    if ESOUI_INDEX_BUILT:
        return

    print(f"\n{C.CYAN}[INIT] Building lightning-fast keyword dictionary in RAM...{C.RESET}")
    start_time = datetime.now()
    broad_extractor = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')

    if os.path.exists(ESO_API_DOC_FILE):
        try:
            with open(ESO_API_DOC_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                for line_num, line in enumerate(f, 1):
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
        file_count = 0
        for root, _, files in os.walk(ESO_LIVE_SOURCE_DIR):
            for file in files:
                if file.endswith(('.lua', '.xml')):
                    file_path = os.path.join(root, file)
                    rel_display = os.path.relpath(file_path, ESO_LIVE_SOURCE_DIR).replace("\\", "/")
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            full_content = f.read()
                        for line in full_content.splitlines():
                            cleaned_line = line.strip()
                            if cleaned_line:
                                for w in set(broad_extractor.findall(cleaned_line)):
                                    if len(w) >= 3 and w not in ESOUI_RAM_DICTIONARY:
                                        ESOUI_RAM_DICTIONARY[w] = f"ESOUI Source ({file}): {cleaned_line}"
                        if file.lower().endswith('.lua'):
                            for v_ctrl, line_no in extract_virtual_controls_from_lua(full_content):
                                if v_ctrl not in ESOUI_RAM_DICTIONARY:
                                    ESOUI_RAM_DICTIONARY[v_ctrl] = f"ESOUI Virtual Control ({rel_display}:{line_no})"
                            # Exact ZO_MenuBar button count per file: count ZO_MenuBar_AddButton(...) calls for referenced ZO_*MenuBar controls
                            add_btn_calls = len(re.findall(r'\bZO_MenuBar_AddButton\s*\(', full_content))
                            if add_btn_calls > 0:
                                for mb_name in set(re.findall(r'\b(ZO_[A-Za-z0-9_]+MenuBar)\b', full_content)):
                                    for btn_idx in range(1, add_btn_calls + 1):
                                        btn_name = f"{mb_name}Button{btn_idx}"
                                        if btn_name not in ESOUI_RAM_DICTIONARY:
                                            ESOUI_RAM_DICTIONARY[btn_name] = f"ESOUI MenuBar Button ({rel_display})"

                            # Catch dynamic CreateControlFromVirtual("Prefix", parent, "Tpl", i) -> Prefix1..Prefix10
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
                        elif file.lower().endswith('.xml'):
                            for name_val, line_no in extract_resolved_xml_control_names(full_content):
                                if name_val not in ESOUI_RAM_DICTIONARY:
                                    ESOUI_RAM_DICTIONARY[name_val] = f"ESOUI XML Control ({rel_display}:{line_no})"

                        file_count += 1
                    except Exception:
                        pass
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
    for w in undoc_valid:
        if w not in ESOUI_RAM_DICTIONARY:
            ESOUI_RAM_DICTIONARY[w] = "Undocumented ESO Global: " + w

    # Derive standard ESO C++ enum boundary constants (*_ITERATION_BEGIN/_END, *_MIN_VALUE/_MAX_VALUE)
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
    return ESOUI_INDEX_BUILT


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
    """Extracts DependsOn and OptionalDependsOn entries and flags invalid '>=' in OptionalDependsOn."""
    deps = []
    invalid_optional = []
    for raw_line in manifest_text.splitlines():
        line = raw_line.strip()
        m_dep = re.match(r'^##\s*DependsOn\s*:\s*(.+)$', line, flags=re.IGNORECASE)
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


def collect_dependency_globals(active_extract_dir, extract_lua_globals_fn):
    """Maps dependency globals to '/live/AddOns/<Dep>/<Subdir>/<File>:<Line>' from ESO_ADDONS_DIR."""
    if not ESO_ADDONS_DIR or not os.path.isdir(ESO_ADDONS_DIR):
        return {}

    global LOCAL_ADDONS_MANIFEST_INDEX
    dep_names = []
    checked_addon_names = set()
    if active_extract_dir and os.path.exists(active_extract_dir):
        for root, _, files in os.walk(active_extract_dir):
            for f in files:
                if f.lower().endswith(('.addon', '.txt')):
                    full_mf = os.path.join(root, f)
                    try:
                        with open(full_mf, 'r', encoding='utf-8', errors='ignore') as fh:
                            mf_text = fh.read()
                        if re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', mf_text, flags=re.MULTILINE | re.IGNORECASE):
                            checked_addon_names.add(os.path.splitext(f)[0].lower())
                        found_deps, _ = parse_manifest_dependencies(mf_text)
                        for d in found_deps:
                            if d not in dep_names:
                                dep_names.append(d)
                    except Exception:
                        pass

    if LOCAL_ADDONS_MANIFEST_INDEX is None:
        idx_map = {}
        try:
            for entry_name in os.listdir(ESO_ADDONS_DIR):
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

        # Also check already-cached v4 filelist.json (no network download) for matching installed folders
        try:
            from src.esoui_filelist_search import _DISK_CACHE_FILE
            if os.path.isfile(_DISK_CACHE_FILE):
                with open(_DISK_CACHE_FILE, "r", encoding="utf-8") as jfh:
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
    spinner_frames = ("|", "/", "-", "\\")
    spinner_idx = 0
    scanned_any_file = False
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
        nonlocal cache_dirty
        current_hash = _compute_dir_fingerprint(folder_path)

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

        if manifest_path:
            manifest_basename = os.path.basename(manifest_path)
            try:
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as mf:
                    for m_line_no, raw_line in enumerate(mf, 1):
                        entry = raw_line.lstrip('\ufeff').strip()
                        if not entry:
                            continue
                        sv_match = re.match(
                            r'^##\s*SavedVariables\s*:\s*(.+)$',
                            entry,
                            flags=re.IGNORECASE,
                        )
                        if sv_match:
                            sv_rhs = re.split(r'[#;]', sv_match.group(1), maxsplit=1)[0]
                            for sv_name in re.findall(r'\b([A-Za-z_][A-Za-z0-9_]*)\b', sv_rhs):
                                if sv_name not in dep_globals:
                                    dep_globals[sv_name] = f"/live/AddOns/{folder_label}/{manifest_basename}:{m_line_no}"
                            continue
                        if entry.startswith('#') or entry.startswith(';') or '$(' in entry:
                            continue
                        rel_file = entry.replace('/', os.sep).replace('\\', os.sep)
                        target_file = os.path.join(folder_path, rel_file)
                        if os.path.isfile(target_file):
                            short_rel_display = f"/{folder_label}/{entry.replace('\\', '/')}"
                            rel_display = f"/live/AddOns{short_rel_display}"
                            _update_scan_spinner(short_rel_display)
                            with open(target_file, 'r', encoding='utf-8', errors='ignore') as tf:
                                file_text = tf.read()

                            if target_file.lower().endswith('.lua'):
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

    # 1. Scan declared & reverse dependencies first (highest priority)
    scanned_lowers = set(checked_addon_names)
    for dep in dep_names:
        low_d = dep.lower()
        scanned_lowers.add(low_d)
        if low_d in LOCAL_ADDONS_MANIFEST_INDEX:
            orig_name, dep_dir, _ = LOCAL_ADDONS_MANIFEST_INDEX[low_d]
        else:
            orig_name, dep_dir = dep, os.path.join(ESO_ADDONS_DIR, dep)
        all_dep_globals.update(_get_or_scan_addon_folder(orig_name, dep_dir))

    # 2. Scan all remaining installed folders in ESO_ADDONS_DIR (persisted by directory hash in Cache/dependency_globals_cache.json)
    for low_name, (orig_name, folder_path, _) in sorted(LOCAL_ADDONS_MANIFEST_INDEX.items()):
        if low_name in scanned_lowers:
            continue
        scanned_lowers.add(low_name)
        folder_globals = _get_or_scan_addon_folder(orig_name, folder_path)
        for g_key, g_loc in folder_globals.items():
            if g_key not in all_dep_globals:
                all_dep_globals[g_key] = f"{g_loc} (installed addon)"

    if scanned_any_file:
        sys.stdout.write(f"\r\033[K    │     {C.GREEN}✔{C.RESET} Dependency & AddOns scan complete.\n")
        sys.stdout.flush()

    if cache_dirty:
        _save_dependency_disk_cache()

    return all_dep_globals

