"""
Statische Python-Codeanalyse für ESO Lua-, Manifest- (.addon/.txt) und XML-Dateien.
"""

import os
import re
from collections import defaultdict
from datetime import datetime

from src.esoui_config import (
    C,
    ESO_BINDINGS_SCHEMA_FILE,
    ESO_XML_SCHEMA_FILE,
    EXTRACT_FOLDER,
    LUA_STD_LIBS,
    print_wrapped_tree_item,
    resolve_config_file_path,
)
from src.esoui_ram_index import (
    ESOUI_RAM_DICTIONARY,
    ESOUI_UNDOCUMENTED_SET,
    build_esoui_index_once,
    collect_dependency_globals,
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


def strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False):
    """Single-pass Lua lexer stripping comments and optionally strings while keeping line numbers."""
    if not isinstance(content, str) or not content:
        return ""

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


def check_for_uncommented_libstub(content):
    code_only = strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)
    return bool(re.search(r'\blibstub\b', code_only, flags=re.IGNORECASE))


def strip_lua_comments_preserve_lines(content):
    return strip_lua_comments_and_strings_preserve_lines(content, keep_strings=True)


def strip_lua_strings_preserve_lines(content):
    return strip_lua_comments_and_strings_preserve_lines(content, keep_strings=False)


def collect_addon_context(extract_dir):
    """Collects Bindings.xml presence, XML content, global tables, SavedVariables, and manifests."""
    has_bindings_xml = False
    xml_combined_parts = []
    all_global_tables = set()
    saved_variables = set()
    root_addon_manifests = []
    root_txt_manifests = []

    if extract_dir and os.path.exists(extract_dir):
        top_entries = os.listdir(extract_dir)
        top_dirs = [d for d in top_entries if os.path.isdir(os.path.join(extract_dir, d))]
        top_files = [f for f in top_entries if os.path.isfile(os.path.join(extract_dir, f))]
        manifest_root_dir = os.path.join(extract_dir, top_dirs) if (len(top_dirs) == 1 and not top_files) else extract_dir

        for f in os.listdir(manifest_root_dir):
            full_p = os.path.join(manifest_root_dir, f)
            if os.path.isfile(full_p):
                low = f.lower()
                if low.endswith(".addon"):
                    root_addon_manifests.append(f)
                elif low.endswith(".txt"):
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as mf:
                            head_text = mf.read(1024)
                        if re.search(r'^\s*##\s*[A-Za-z]+:', head_text, flags=re.MULTILINE):
                            root_txt_manifests.append(f)
                    except Exception:
                        pass

        for root, _, files in os.walk(extract_dir):
            for f in files:
                lower_f = f.lower()
                full_path = os.path.join(root, f)
                if f == "Bindings.xml":
                    has_bindings_xml = True
                if lower_f.endswith(".xml"):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as xf:
                            raw_xml = xf.read()
                        xml_combined_parts.append(re.sub(r'<!--.*?-->', '', raw_xml, flags=re.DOTALL))
                    except Exception:
                        pass
                elif lower_f.endswith(".lua"):
                    try:
                        with open(full_path, "r", encoding="utf-8", errors="ignore") as lf:
                            lua_clean = strip_lua_comments_preserve_lines(lf.read())
                        tbl_matches = re.findall(
                            r'^(?<!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:\{\}|\1\s*or\s*\{})',
                            lua_clean,
                            flags=re.MULTILINE,
                        )
                        for m in tbl_matches:
                            if not re.search(r'\blocal\s+' + re.escape(m) + r'\b', lua_clean):
                                all_global_tables.add(m)
                    except Exception:
                        pass
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

    return {
        "has_bindings_xml": has_bindings_xml,
        "xml_content": "\n".join(xml_combined_parts),
        "all_global_tables": all_global_tables,
        "saved_variables": saved_variables,
        "root_addon_manifests": root_addon_manifests,
        "root_txt_manifests": root_txt_manifests,
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
    lua_keywords = {
        "local", "function", "if", "end", "then", "return", "else", "elseif",
        "for", "in", "pairs", "ipairs", "true", "false", "nil", "and", "or",
        "not", "while", "repeat", "until", "break", "do", "self"
    }
    file_locals = _collect_lua_local_identifiers(code_only)
    file_hits = defaultdict(list)
    ident_pat = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')

    for idx, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if not stripped_line or re.match(r'^local\s+[A-Za-z_][A-Za-z0-9_]*\s*=\s*[A-Za-z_][A-Za-z0-9_]*\s*$', stripped_line):
            continue
        for match in ident_pat.finditer(line):
            word = match.group(1)
            if len(word) < 3 or word in lua_keywords or word in file_locals:
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
        r'\b(?:if|elseif)\s+(?:type\s*\(\s*([A-Za-z_][A-Za-z0-9_]*)\s*\)\s*(?:==|~=)\s*""|([A-Za-z_][A-Za-z0-9_]*)\s*(?:~= nil)?)\s*then\b'
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


def _check_lua_global_tables_and_locals(comment_free_lua, raw_lines, clean_lines_list, lua_file_count, addon_ctx, lua_issues):
    """Checks global table pollution, multiple global tables, global functions, and local aliases."""
    lua_suggestions = []
    has_bindings_xml = addon_ctx["has_bindings_xml"]
    combined_xml_content = addon_ctx["xml_content"]
    all_addon_globals = addon_ctx["all_global_tables"]

    if not is_index_built():
        build_esoui_index_once()

    if len(all_addon_globals) > 1:
        sorted_globals = ", ".join(sorted(all_addon_globals))
        lua_issues.append(
            f"Multiple Global Addon Tables: Found {len(all_addon_globals)} global tables across the addon ({sorted_globals}). "
            "Only ONE global table per addon is allowed; attach sub-tables to your main addon table instead!"
        )
    global_func_matches = re.findall(r'^(?!local\s)function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', comment_free_lua, flags=re.MULTILINE)
    for g_func in global_func_matches:
        if g_func not in ESOUI_RAM_DICTIONARY and g_func not in ESOUI_UNDOCUMENTED_SET:
            if not re.search(r'\blocal\s+' + re.escape(g_func) + r'\b', comment_free_lua):
                lua_issues.append(
                    f"Global Function Pollution: Global function '{g_func}()' leaked into _G. "
                    "Keep it 'local' or attach it to your single addon table (e.g., MyAddon." + g_func + ")!"
                )

    raw_table_matches = re.findall(r'^(?<!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?:\{\}|\1\s*or\s*\{})', comment_free_lua, flags=re.MULTILINE)
    global_table_matches = [
        m for m in dict.fromkeys(raw_table_matches)
        if not re.search(r'\blocal\s+' + re.escape(m) + r'\b', comment_free_lua)
    ]

    aliased_globals_in_file = set()
    for g_table in global_table_matches:
        used_in_xml = bool(re.search(r'\b' + re.escape(g_table) + r'\b', combined_xml_content))
        is_legitimate_global = (lua_file_count > 1) or has_bindings_xml or used_in_xml

        alias_match = re.search(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*' + re.escape(g_table) + r'\b', comment_free_lua)
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
            lua_issues.append(
                "Global Pollution: Created global table '" + g_table
                + "' in a single-file addon w/o Bindings.xml, globals used in XML, and no API provided. Everything should be kept strictly 'local'!"
            )
        elif local_alias and direct_usage_lines:
            formatted_hits = [f"    {g_table}:{line_no} --{orig_line}" for line_no, orig_line in direct_usage_lines]
            lua_suggestions.append(
                f"Best Practice Violation: Global table '{g_table}' has local alias '{local_alias}', "
                f"but '{g_table}' is still accessed directly {len(direct_usage_lines)} time(s) instead of using '{local_alias}':\n"
                + "\n".join(formatted_hits)
            )

    primary_rep, minor_rep = find_repeated_globals_in_lua(
        "\n".join(raw_lines), raw_lines, all_addon_globals, ESOUI_RAM_DICTIONARY, ESOUI_UNDOCUMENTED_SET, LUA_STD_LIBS
    )
    for finding in primary_rep:
        if not any(f"Global '{ag}'" in finding for ag in aliased_globals_in_file):
            lua_suggestions.append(finding)
    lua_suggestions.extend(minor_rep)
    return lua_suggestions


def extract_globals_from_lua_source(lua_code, rel_display_path):
    """Extracts global identifiers with exact file path and line number from a dependency Lua file."""
    exposed = {}
    clean_lua = strip_lua_comments_preserve_lines(lua_code)
    local_strings = dict(re.findall(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*["\']([^"\']+)["\']', clean_lua))

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
    return exposed

def analyze_lua_file(file_name, content, active_extract_dir, addon_ctx):
    """Runs all static checks on a single Lua source file and queues unverified globals for AI."""
    lua_file_count = sum(
        1 for _, _, files in (os.walk(active_extract_dir) if os.path.exists(active_extract_dir) else [])
        for f in files if f.lower().endswith('.lua')
    )

    lua_issues = []
    if check_for_uncommented_libstub(content):
        lua_issues.append(
            "Deprecated LibStub Usage: Found active 'LibStub' reference in Lua code. "
            "LibStub is obsolete since Summerset and must not be used anymore (see https://esoui.com)."
        )
    comment_free_lua = strip_lua_comments_preserve_lines(content)
    raw_lines = content.splitlines()
    clean_lines_list = comment_free_lua.splitlines()

    _check_lua_deprecated_savedvars(comment_free_lua, raw_lines, lua_issues)
    lua_suggestions = _check_lua_global_tables_and_locals(
        comment_free_lua, raw_lines, clean_lines_list, lua_file_count, addon_ctx, lua_issues
    )
    _check_lua_startup_chat_spam(comment_free_lua, raw_lines, lua_suggestions, addon_ctx)
    ai_slop_block = _check_lua_ai_slop_patterns(content, raw_lines)

    if lua_issues:
        print(f"    ├── {C.RED}[FAIL]{C.RESET} Static rule violations detected ({len(lua_issues)}):")
        summary_reasons = []
        for issue in lua_issues:
            short_reason = issue.split(":", 1).strip()
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
        return "[STATUS] FAIL\n[CRITICAL VIOLATIONS]\n" + issues_str + ai_slop_block + "\n[BEST PRACTICE SUGGESTIONS]\n" + sugg_str

    clean_code_for_words = strip_lua_strings_preserve_lines(comment_free_lua)
    flattened_content = re.sub(r'\s+', ' ', clean_code_for_words)
    table_keys_to_ignore = set()
    for block in re.findall(r'\{([^{}]+)\}', flattened_content):
        table_keys_to_ignore.update(re.findall(r'(?<!\[)\b([A-Za-z_][A-Za-z0-9_]*)\b\s*=', block))

    local_defs = _collect_lua_local_identifiers(clean_code_for_words)
    all_words = set(re.findall(r'(?<![.:])\b([A-Za-z_][A-Za-z0-9_]*)\b', clean_code_for_words))
    lua_keywords = {
        "local", "function", "if", "end", "then", "return", "else", "elseif",
        "for", "in", "pairs", "ipairs", "true", "false", "nil", "and", "or",
        "not", "while", "repeat", "until", "break"
    }
    words_to_check = all_words - lua_keywords - table_keys_to_ignore - local_defs

    addon_main_namespace = file_name.replace("\\", "/").split("/") if ("\\" in file_name or "/" in file_name) else os.path.splitext(file_name)
    blessed_keywords = {str(addon_main_namespace)} | addon_ctx["all_global_tables"]
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
        dep_globals_map = collect_dependency_globals(active_extract_dir, extract_globals_from_lua_source)
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
            return "[STATUS] PASS\n[CRITICAL VIOLATIONS] None" + ai_slop_block + "\n[BEST PRACTICE SUGGESTIONS]\n" + "\n".join(["  - " + s for s in lua_suggestions])
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
