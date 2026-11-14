# -*- coding: utf-8 -*-
"""
================================================================================
ESOUI Global Variables Reference Analyzer
================================================================================
By: Baertram, 2026-11-10
This script performs static code analysis on the EsoUI source codebase (The Elder
Scrolls Online UI). It compares global variables utilized within the Lua source 
code against the official API documentation (ESOUIDocumentation.txt) and codebase
assignments to precisely isolate and categorize undocumented native triangulation
variables and constants injected from the C++ game engine core.

Operational Workflow:
Phase 1: Pre-scans all legitimate global definitions, ZO_CreateStringId calls,
         and XML UI controls/fonts across the codebase.
Phase 2: Executes token-synchronized reference checks respecting complete
         file-level locals, hierarchical block scopes, and balanced signatures.
================================================================================
"""

import os
import re
import json
import time
import sys
from datetime import datetime

# ==============================================================================
# CONFIGURATION / PATHS (Adjust the directories here as needed)
# ==============================================================================
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
# ==============================================================================

LUA_51_KEYWORDS = {
    "and", "break", "do", "else", "elseif", "end", "false", "for", "function",
    "if", "in", "local", "nil", "not", "or", "repeat", "return", "then", "true",
    "until", "while"
}

LUA_STANDARD_GLOBALS = {
    "assert", "collectgarbage", "dofile", "error", "getfenv", "getmetatable",
    "ipairs", "load", "loadfile", "loadstring", "next", "pairs", "pcall", "print",
    "rawequal", "rawget", "rawset", "select", "setfenv", "setmetatable", "tonumber",
    "tostring", "type", "unpack", "xpcall", "_G", "_VERSION",
    "coroutine", "module", "require", "string", "table", "math", "io", "os", "debug"
}

ESO_IMPLICIT_LOCALS = {
    "self", "control", "data", "selected", "activated", "enabled", "active",
    "i", "j", "k", "v", "key", "value", "name", "choice", "button", "eventCode",
    "GuiRoot", "SOUNDS", "EVENT_MANAGER", "CALLBACK_MANAGER", "SYSTEMS"
}

DEBUG_FILE_HANDLE = None


def log_debug(message, console_only=False, file_only=False):
    """Manages time-stamped routing of all log and debug outputs."""
    global DEBUG_FILE_HANDLE
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    formatted_msg = f"[{timestamp}] {message}"
    
    if console_only:
        print(message)
        return
    if DEBUG_FILE_HANDLE:
        DEBUG_FILE_HANDLE.write(formatted_msg + "\n")
    if not file_only:
        if not any(x in message for x in ["[DEBUG-SCAN]", "Line ", "Try Path", "Asset file", "[/esoui/", "[APIVERSION]", "- Found global variables"]):
            print(message)


def parse_api_documentation(doc_path, is_debug):
    """Parses ESOUIDocumentation.txt to extract documented API globals."""
    if not os.path.exists(doc_path):
        log_debug(f"[DEBUG-API] file not found at: {doc_path}")
        return None, set()
    
    api_version = None
    defined_globals = set()
    with open(doc_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if "API Version" in line:
                match = re.search(r'API Version\s+(\d+)', line)
                if match:
                    api_version = match.group(1)
            if line.startswith('* '):
                item = line.replace('* ', '').strip()
                name_match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)', item)
                if name_match:
                    defined_globals.add(name_match.group(1))
    return api_version, defined_globals
def resolve_loading_order(base_dir, is_debug):
    """Resolves exact topological loading order via Depth-First Search (DFS)."""
    manifest_raw_pools = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.txt') and file != FILENAME_ESOUI_API:
                name_str, _ = os.path.splitext(file)
                manifest_raw_pools[name_str.lower()] = {
                    'filename': str(file),
                    'pure_name': str(name_str),
                    'root_path': root,
                    'absolute_path': os.path.join(root, file)
                }

    processed_graph = {}
    for m_key, info in manifest_raw_pools.items():
        depends = []
        listed_files = []
        with open(info['absolute_path'], 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_str = line.strip().replace('\r', '')
                if not line_str or line_str.startswith('#'):
                    continue
                if line_str.startswith('## DependsOn:') or line_str.startswith('## PCDependsOn:'):
                    clean_tokens = line_str.replace('## DependsOn:', '').replace('## PCDependsOn:', '').strip().split()
                    for token in clean_tokens:
                        dep_clean = token.replace('ZO_', '').lower()
                        if dep_clean in manifest_raw_pools:
                            depends.append(dep_clean)
                elif line_str.startswith('## ConsoleDependsOn:'):
                    continue
                else:
                    clean_asset_line = line_str.replace('\\', '/')
                    asset_path_a = os.path.normpath(os.path.join(info['root_path'], clean_asset_line))
                    asset_path_b = os.path.normpath(os.path.join(base_dir, clean_asset_line))
                    if os.path.exists(asset_path_a):
                        listed_files.append(asset_path_a)
                    elif os.path.exists(asset_path_b):
                        listed_files.append(asset_path_b)
                        
        processed_graph[m_key] = {
            'original_name': str(info['pure_name']),
            'depends': depends,
            'files': listed_files
        }

    visited = {}
    order = []
    def dfs(node):
        if node in visited:
            return
        visited[node] = 1
        if node in processed_graph:
            for dep in processed_graph[node]['depends']:
                dfs(dep)
        visited[node] = 2
        order.append(node)

    for m in sorted(processed_graph.keys()):
        if m not in visited:
            dfs(m)
    return order, processed_graph


def clean_full_lua_content(content):
    """
    Replaces comments, string literals, and macros with spaces of identical length.
    Preserves exact line counts AND exact column indices for raw line highlighting.
    """
    def space_repl(match):
        text = match.group(0)
        return "".join("\n" if ch == "\n" else " " for ch in text)

    content = re.sub(r'--\[\[.*?\]\]', space_repl, content, flags=re.DOTALL)
    content = re.sub(r'(?<!-)\[\[.*?\]\]', space_repl, content, flags=re.DOTALL)
    
    lines = content.splitlines()
    cleaned_lines = []
    for line in lines:
        line = re.sub(r'--.*$', space_repl, line)
        line = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', space_repl, line)
        line = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", space_repl, line)
        line = re.sub(r'\$\([a-zA-Z0-9_]+\)', space_repl, line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def extract_xml_defined_globals(xml_content):
    """Extracts global UI control and font names defined via name='...' in XML files."""
    xml_globals = set()
    clean_xml = re.sub(r'<!--.*?-->', '', xml_content, flags=re.DOTALL)
    for match in re.finditer(r'\bname\s*=\s*["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']', clean_xml):
        xml_globals.add(match.group(1))
    return xml_globals
def extract_all_function_parameters_from_text(cleaned_content):
    """
    Extracts all named and anonymous function parameters across the entire cleaned
    Lua file using balanced parenthesis scanning without line-window limits.
    """
    params = set()
    if not isinstance(cleaned_content, str):
        cleaned_content = str(cleaned_content)
        
    content_len = len(cleaned_content)
    for m in re.finditer(r'\bfunction\b\s*(?:[a-zA-Z_][a-zA-Z0-9_.:]*)?\s*\(', cleaned_content):
        pos = m.end()
        depth = 1
        buf = []
        while pos < content_len and depth > 0:
            ch = cleaned_content[pos]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            if depth == 1:
                buf.append(ch)
            pos += 1
            
        raw_param_str = "".join(buf)
        for p in raw_param_str.split(','):
            p_clean = p.strip()
            if p_clean and p_clean != "..." and re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', p_clean):
                params.add(p_clean)
    return params


def extract_multiline_function_params(cleaned_lines, start_idx):
    """Extracts parameters from single-line or multi-line function signatures using parenthesis balance."""
    params = set()
    if start_idx >= len(cleaned_lines) or not re.search(r'\bfunction\b', cleaned_lines[start_idx]):
        return params
    acc = " ".join(cleaned_lines[start_idx:min(start_idx + 40, len(cleaned_lines))])
    for m in re.finditer(r'\bfunction\b\s*[a-zA-Z0-9_.:]*\s*\(', acc):
        pos = m.end()
        depth = 1
        buf = []
        while pos < len(acc) and depth > 0:
            ch = acc[pos]
            if ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    break
            if depth == 1:
                buf.append(ch)
            pos += 1
        for p in "".join(buf).split(','):
            p_clean = p.strip()
            if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', p_clean):
                params.add(p_clean)
    return params


def main():
    """Main orchestration entry point."""
    global DEBUG_FILE_HANDLE
    is_debug = "--debug" in sys.argv
    
    print("========================================")
    print("  ESOUI Global Variables Reference Analyzer")
    print("========================================")
    print("Select server scope:\n1) Live\n2) PTS (Public Test Server)")
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        scope, base_doc_path = "live", LIVE_PATH_ESOUI_DOC
        dir_esoui_sources, base_dir_output = LIVE_DIR_ESOUI_SOURCES, LIVE_DIR_OUTPUT
    elif choice == "2":
        scope, base_doc_path = "PTS", PTS_PATH_ESOUI_DOC
        dir_esoui_sources, base_dir_output = PTS_DIR_ESOUI_SOURCES, PTS_DIR_OUTPUT
    else:
        print("[ERROR] Invalid choice. Aborting execution.")
        return

    cache_input = input("Force rebuild manifest cache? (Y/n): ").strip().lower()
    force_rebuild = cache_input != 'n'
    full_doc_path = base_doc_path if base_doc_path.endswith(FILENAME_ESOUI_API) else os.path.join(base_doc_path, FILENAME_ESOUI_API)
    
    now = datetime.now()
    folder_name = now.strftime("%y%m%d_%H%M%S")
    dir_output = os.path.join(base_dir_output, folder_name) if base_dir_output else folder_name
        
    if not os.path.exists(dir_output):
        os.makedirs(dir_output)

    out_filename = f"{folder_name}-{scope.lower()}-esoui_globals_missing_in_api_doc.lua"
    final_output_path = os.path.join(dir_output, out_filename)
    if DIR_CACHE and not os.path.exists(DIR_CACHE):
        os.makedirs(DIR_CACHE)
    cache_filename = f"esoui_manifest_cache_{scope.lower()}.json"
    path_cache_file = os.path.join(DIR_CACHE, cache_filename) if DIR_CACHE else cache_filename

    if is_debug:
        debug_log_filename = f"{folder_name}-{scope.lower()}-debug.log"
        debug_log_path = os.path.join(dir_output, debug_log_filename)
        DEBUG_FILE_HANDLE = open(debug_log_path, 'w', encoding='utf-8')
        log_debug("Found global variables without definition in ESOUI API Documentation and ESOUI Source code\n", file_only=True)
        log_debug(f"[SYSTEM] Selected scope chosen via terminal input: '{scope.upper()}'", file_only=True)

    start_api_time = time.time()
    current_api, doc_globals = parse_api_documentation(full_doc_path, is_debug)
    api_duration = time.time() - start_api_time
    if not current_api:
        print(f"[ERROR] '{full_doc_path}' konnte nicht gelesen werden.")
        if DEBUG_FILE_HANDLE:
            DEBUG_FILE_HANDLE.close()
        return
        
    if is_debug:
        log_debug(f"[APIVERSION] APIversion detected: {current_api}", file_only=True)
        log_debug(f"[SYSTEM] Cache rebuild action evaluation input yielded: '{force_rebuild}'", file_only=True)
        log_debug(f"[SYSTEM] Base input configuration files verified.", file_only=True)

    rebuild_cache = force_rebuild or not os.path.exists(path_cache_file)
    if not rebuild_cache:
        try:
            with open(path_cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                if cached_data.get("api_version") != f"{current_api} ({scope})":
                    rebuild_cache = True
                else:
                    rebuild_cache = False
        except Exception:
            rebuild_cache = True

    if rebuild_cache:
        log_debug(f"[CACHE] Generating pristine internal mapping structure...", file_only=True)
        start_cache_time = time.time()
        load_order, manifest_data = resolve_loading_order(dir_esoui_sources, is_debug)
        cached_data = {
            "api_version": f"{current_api} ({scope})",
            "load_order": load_order,
            "manifest_files": {str(manifest_data[k]['original_name']): manifest_data[k]['files'] for k in load_order}
        }
        with open(path_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, ensure_ascii=False)
        cache_duration = time.time() - start_cache_time
    else:
        log_debug(f"[CACHE] Reusing stable persistent layout file cache structure.", file_only=True)
        load_order, cache_duration = cached_data["load_order"], 0.0

    print(f"APIVersion detected:  {current_api}")
    log_debug("--- RE-EVALUATED DYNAMIC LOADING ORDER ---", console_only=False)
    for idx, k in enumerate(load_order, start=1):
        files_pool = cached_data['manifest_files'].get(k, [])
        lua_count = sum(1 for x in files_pool if x.lower().endswith('.lua'))
        xml_count = sum(1 for x in files_pool if x.lower().endswith('.xml'))
        log_debug(f"[{idx:03d}] {k}.txt -> Assets: {len(files_pool)} ({lua_count} Lua, {xml_count} Xml)", console_only=False)
    log_debug("-------------------------------------------\n", console_only=False)

    scan_source_assets(scope, current_api, doc_globals, cached_data, dir_esoui_sources, dir_output, final_output_path, now, api_duration, cache_duration, is_debug)


def prescan_allowed_definitions(load_order, manifest_files, allowed_globals):
    """Phase 1: Pre-scans XML UI names, ZO_CreateStringId, and Lua globals."""
    xml_defined_globals = set()
    total_xml_scanned = 0
    total_txt_scanned = 0

    for manifest_key in load_order:
        matched_key = next((k for k in manifest_files.keys() if k.lower() == manifest_key.lower()), None)
        if not matched_key:
            continue
        total_txt_scanned += 1
        for file_path in manifest_files.get(matched_key, []):
            lower_path = file_path.lower()
            if lower_path.endswith('.xml'):
                total_xml_scanned += 1
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    xml_defined_globals.update(extract_xml_defined_globals(f.read()))
                continue
            if not lower_path.endswith('.lua'):
                continue
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            
            created_strings = re.findall(r'\bZO_CreateStringId\s*\(\s*["\']([a-zA-Z_][a-zA-Z0-9_]*)["\']', raw_text)
            allowed_globals.update(created_strings)
            
            content = clean_full_lua_content(raw_text)
            global_defs = re.findall(r'(?<!\blocal\s)\b([a-zA-Z_][a-zA-Z0-9_]*)\s*=', content)
            allowed_globals.update(global_defs)
            global_funcs = re.findall(r'(?<!\blocal\s)\bfunction\s+([a-zA-Z_][a-zA-Z0-9_|.:]*)', content)
            allowed_globals.update(global_funcs)
            zo_patterns = re.findall(r'\b([zZ][oO][A-Z_][a-zA-Z0-9_]*)\b', content)
            allowed_globals.update(zo_patterns)

    return xml_defined_globals, total_xml_scanned, total_txt_scanned
def extract_loop_variables(cleaned_line):
    """Extracts loop control variables from 'for ... in' and 'for ... =' statements."""
    loop_vars = set()
    for_in_match = re.search(r'\bfor\s+([a-zA-Z0-9_,\s]+)\s+in\b', cleaned_line)
    if for_in_match:
        for v in for_in_match.group(1).split(','):
            v_clean = v.strip()
            if v_clean and v_clean != "_":
                loop_vars.add(v_clean)
    for_num_match = re.search(r'\bfor\s+([a-zA-Z0-9_,\s]+)\s*=', cleaned_line)
    if for_num_match and not for_in_match:
        for v in for_num_match.group(1).split(','):
            v_clean = v.strip()
            if v_clean and v_clean != "_":
                loop_vars.add(v_clean)
    return loop_vars


def extract_all_file_locals(cleaned_content):
    """Extracts all file-level and block-level local declarations and function parameters across an entire cleaned Lua file."""
    locals_set = set()
    for fn in re.findall(r'\blocal\s+function\s+([a-zA-Z_][a-zA-Z0-9_]*)', cleaned_content):
        locals_set.add(fn)
    for m in re.finditer(r'\blocal\s+(?!function\b)([a-zA-Z_][a-zA-Z0-9_]*(?:\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*)*)', cleaned_content):
        for var in m.group(1).split(','):
            v_clean = var.strip()
            if v_clean:
                locals_set.add(v_clean)
    for line in cleaned_content.splitlines():
        locals_set.update(extract_loop_variables(line))
    locals_set.update(extract_all_function_parameters_from_text(cleaned_content))
    return locals_set


def scan_source_assets(scope, current_api, doc_globals, cached_data, dir_esoui_sources, dir_output, final_output_path, now, api_duration, cache_duration, is_debug):
    """Executes Phase 1 pre-scan and Phase 2 scope-aware reference checks."""
    start_sources_time = time.time()
    load_order = cached_data["load_order"]
    manifest_files = cached_data["manifest_files"]
    allowed_globals = set(doc_globals) | LUA_51_KEYWORDS | LUA_STANDARD_GLOBALS | ESO_IMPLICIT_LOCALS
    reported_globals = set()
    unreferenced_log = []
    total_lua_scanned = 0

    log_debug("[INFO] Phase 1: Pre-scanning codebase (Lua & XML) for legitimate definitions...", console_only=True)
    xml_defined_globals, total_xml_scanned, total_txt_scanned = prescan_allowed_definitions(load_order, manifest_files, allowed_globals)

    log_debug("[INFO] Phase 2: Scanning code for unreferenced variables...", console_only=True)
    if is_debug:
        log_debug("- Found global variables without definition in ESOUI source / no mention in ESOUI API Docs. -", file_only=True)

    for manifest_key in load_order:
        matched_key = next((k for k in manifest_files.keys() if k.lower() == manifest_key.lower()), None)
        if not matched_key:
            continue
        for file_path in manifest_files.get(matched_key, []):
            if not file_path.lower().endswith('.lua'):
                continue
            total_lua_scanned += 1
            raw_rel = os.path.relpath(file_path, dir_esoui_sources).replace('\\', '/')
            clean_display_path = f"/esoui/{raw_rel[6:]}" if raw_rel.lower().startswith("esoui/") else f"/esoui/{raw_rel}"
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_content = f.read()
            cleaned_content = clean_full_lua_content(raw_content)
            raw_lines, cleaned_lines = raw_content.splitlines(), cleaned_content.splitlines()
            all_file_locals = extract_all_file_locals(cleaned_content)
            scope_stack = [set()]
            file_found_globals = []
            
            for line_idx, cleaned_line in enumerate(cleaned_lines):
                if not cleaned_line.strip() or line_idx >= len(raw_lines):
                    continue
                if ":MUST_IMPLEMENT" in cleaned_line:
                    continue

                opens = len(re.findall(r'\b(if|for|while|do|function|repeat)\b', cleaned_line))
                closes = len(re.findall(r'\b(end|until)\b', cleaned_line))
                
                for _ in range(opens):
                    scope_stack.append(set())
                    
                params = extract_multiline_function_params(cleaned_lines, line_idx)
                scope_stack[-1].update(params)
                all_file_locals.update(params)
                active_locals = set(all_file_locals).union(*scope_stack)
                
                for match in re.finditer(r'\b([a-zA-Z_][a-zA-Z0-9_]*)', cleaned_line):
                    var_name = match.group(1)
                    start_pos, end_pos = match.start(), match.end()
                    trailing, leading = cleaned_line[end_pos:].lstrip(), cleaned_line[:start_pos].rstrip()
                    if leading.endswith('.') or leading.endswith(':') or trailing.startswith(':') or trailing.startswith('.') or trailing.startswith('['):
                        continue
                    if trailing.startswith('=') and not leading.endswith('['):
                        continue
                        
                    if var_name not in active_locals and var_name not in allowed_globals:
                        if var_name not in reported_globals:
                            start_col = start_pos + 1
                            highlighted = f"{raw_lines[line_idx][:start_pos]}[[ {var_name} ]]{raw_lines[line_idx][end_pos:]}"
                            unreferenced_log.append((var_name, f"{var_name} = nil --{clean_display_path}:{line_idx + 1}:{start_col} | {highlighted.strip()}"))
                            reported_globals.add(var_name)
                            file_found_globals.append(f"{var_name}:{line_idx + 1}")
                for _ in range(closes):
                    if len(scope_stack) > 1:
                        scope_stack.pop()
            if is_debug and file_found_globals:
                log_debug(f"[{clean_display_path}] {', '.join(file_found_globals)}", file_only=True)

    file_counts = (total_lua_scanned, total_xml_scanned, total_txt_scanned)
    write_final_categorized_reports(scope, current_api, reported_globals, unreferenced_log, xml_defined_globals, file_counts, api_duration, cache_duration, start_sources_time, final_output_path, is_debug)
def write_final_categorized_reports(scope, current_api, reported_globals, unreferenced_log, xml_defined_globals, file_counts, api_duration, cache_duration, start_sources_time, final_output_path, is_debug):
    """Sorts tracked undocumented tokens into the 10 distinct structural Lua buckets."""
    global DEBUG_FILE_HANDLE
    sources_duration = time.time() - start_sources_time
    total_found_count = len(reported_globals)
    total_lua, total_xml, total_txt = file_counts
    total_files_scanned = total_lua + total_xml + total_txt
    files_breakdown = f"{total_files_scanned} (*.lua {total_lua} / *.xml {total_xml} / *.txt {total_txt})"
    
    cat_constants_iteration = []
    cat_constants_general = []
    cat_global_events = []
    cat_global_settings = []
    cat_event_handlers = []
    cat_strings_si = []
    cat_zos_special_api = []
    cat_camelcase_vars = []
    cat_remaining = []
    cat_xml_controls = []

    zos_specials = {"hmake", "hstructure", "internalassert"}

    for var_name, full_entry in unreferenced_log:
        if var_name in xml_defined_globals:
            cat_xml_controls.append(full_entry)
        elif var_name in zos_specials:
            cat_zos_special_api.append(full_entry)
        elif var_name.startswith("SI_"):
            cat_strings_si.append(full_entry)
        elif "ITERATION_" in var_name or var_name.endswith("_MIN_VALUE") or var_name.endswith("_MAX_VALUE"):
            cat_constants_iteration.append(full_entry)
        elif var_name.startswith("EVENT_"):
            cat_global_events.append(full_entry)
        elif "_SETTING_" in var_name:
            cat_global_settings.append(full_entry)
        elif re.match(r'^on[A-Z]', var_name, re.IGNORECASE):
            cat_event_handlers.append(full_entry)
        elif var_name.startswith(tuple("abcdefghijklmnopqrstuvwxyz_")) and not var_name.isupper():
            cat_camelcase_vars.append(full_entry)
        elif var_name.isupper():
            cat_constants_general.append(full_entry)
        else:
            cat_remaining.append(full_entry)

    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(f"-- Checked on {datetime.now().strftime('%d.%m.%Y %H:%M:%S')} / ServerScope: {scope} / APIVersion: {current_api}\n")
        f.write(f"-- Total Files Actually Scanned: {files_breakdown}\n")
        f.write(f"-- Total Undocumented Global Variables Found: {total_found_count}\n\n")
        
        f.write("-- 1. Global Constants (with ITERATION_ / _MIN_VALUE / _MAX_VALUE) --\n")
        for entry in sorted(cat_constants_iteration):
            f.write(f"{entry}\n")
        
        f.write("\n-- 2. Global Constants (General All-Caps & Flags) --\n")
        for entry in sorted(cat_constants_general):
            f.write(f"{entry}\n")
        
        f.write("\n-- 3. Global Events (EVENT_*) --\n")
        for entry in sorted(cat_global_events):
            f.write(f"{entry}\n")
        
        f.write("\n-- 4. Global Settings (*_SETTING_*) --\n")
        for entry in sorted(cat_global_settings):
            f.write(f"{entry}\n")
        
        f.write("\n-- 5. Event Handlers (On[A-Z]*) --\n")
        for entry in sorted(cat_event_handlers):
            f.write(f"{entry}\n")
        
        f.write("\n-- 6. String Constants (SI_) --\n")
        for entry in sorted(cat_strings_si):
            f.write(f"{entry}\n")
        
        f.write("\n-- 7. ZOs Special API --\n")
        for entry in sorted(cat_zos_special_api):
            f.write(f"{entry}\n")
        
        f.write("\n-- 8. Variables to check (missing local definition?) --\n")
        for entry in sorted(cat_camelcase_vars):
            f.write(f"{entry}\n")
        
        if cat_remaining:
            f.write("\n-- 9. Other Undocumented Variables --\n")
            for entry in sorted(cat_remaining):
                f.write(f"{entry}\n")

        f.write("\n-- 10. Global XML defined controls/fonts --\n")
        for entry in sorted(cat_xml_controls):
            f.write(f"{entry}\n")
                
    stats_block = (
        "\n========================================\n"
        f"  ANALYSIS STATISTICS ({scope.upper()})\n"
        "========================================\n"
        f"Total Files Scanned        : {files_breakdown}\n"
        f"Undocumented Globals Found : {total_found_count}\n"
        f"Parsing API Documentation  : {api_duration:.4f}s\n"
        f"Building Manifest Cache    : {cache_duration:.4f}s\n"
        f"Scanning ESOUI Sources     : {sources_duration:.4f}s\n"
        "========================================"
    )
    log_debug(stats_block, console_only=False)
    if is_debug and DEBUG_FILE_HANDLE:
        DEBUG_FILE_HANDLE.close()


if __name__ == '__main__':
    main()
