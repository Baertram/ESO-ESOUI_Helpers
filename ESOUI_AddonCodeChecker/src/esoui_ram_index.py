"""
In-Memory ESO-API-Indexierung, undocumented globals und Dependency-Globals-Resolver.
"""

import os
import re
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
ESOUI_RAM_DICTIONARY = {}
ESOUI_UNDOCUMENTED_SET = set()
ESOUI_INDEX_BUILT = False


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
                    if cleaned_line == "h2. UI XML Layout":
                        break
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
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                cleaned_line = line.strip()
                                if cleaned_line:
                                    for w in set(broad_extractor.findall(cleaned_line)):
                                        if len(w) >= 3 and w not in ESOUI_RAM_DICTIONARY:
                                            ESOUI_RAM_DICTIONARY[w] = f"ESOUI Source ({file}): {cleaned_line}"
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

    dep_names = []
    if active_extract_dir and os.path.exists(active_extract_dir):
        for root, _, files in os.walk(active_extract_dir):
            for f in files:
                if f.lower().endswith(('.addon', '.txt')):
                    try:
                        with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fh:
                            found_deps, _ = parse_manifest_dependencies(fh.read())
                            for d in found_deps:
                                if d not in dep_names:
                                    dep_names.append(d)
                    except Exception:
                        pass

    all_dep_globals = {}
    for dep in dep_names:
        if dep in DEPENDENCY_GLOBALS_CACHE:
            all_dep_globals.update(DEPENDENCY_GLOBALS_CACHE[dep])
            continue

        dep_globals = {}
        dep_dir = os.path.join(ESO_ADDONS_DIR, dep)
        manifest_path = None
        for ext in ('.addon', '.txt'):
            candidate = os.path.join(dep_dir, dep + ext)
            if os.path.isfile(candidate):
                manifest_path = candidate
                break

        if manifest_path:
            try:
                with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as mf:
                    for raw_line in mf:
                        entry = raw_line.strip()
                        if not entry or entry.startswith('#') or entry.startswith(';') or '$(' in entry:
                            continue
                        rel_file = entry.replace('/', os.sep).replace('\\', os.sep)
                        target_file = os.path.join(dep_dir, rel_file)
                        if os.path.isfile(target_file):
                            rel_display = f"/live/AddOns/{dep}/{entry.replace('\\', '/')}"
                            with open(target_file, 'r', encoding='utf-8', errors='ignore') as tf:
                                file_text = tf.read()
                            if target_file.lower().endswith('.lua'):
                                dep_globals.update(extract_lua_globals_fn(file_text, rel_display))
                            elif target_file.lower().endswith('.xml'):
                                for xm in re.finditer(r'\bname\s*=\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']', file_text):
                                    g_name = xm.group(1)
                                    if g_name not in dep_globals:
                                        line_no = file_text.count('\n', 0, xm.start(1)) + 1
                                        dep_globals[g_name] = f"{rel_display}:{line_no}"
            except Exception:
                pass

        DEPENDENCY_GLOBALS_CACHE[dep] = dep_globals
        all_dep_globals.update(dep_globals)

    return all_dep_globals
