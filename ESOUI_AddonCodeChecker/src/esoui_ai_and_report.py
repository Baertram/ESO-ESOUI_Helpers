"""
ZIP-Strukturprüfung, MMOUI-Filelist-Orchestrierung, Ollama-AI-Review und kompaktes BBCode-Reporting.
"""

import concurrent.futures
import os
import re
import shutil
import subprocess
import time
import zipfile
from collections import defaultdict
from datetime import datetime

from ollama import Client

from src.esoui_config import (
    AI_NUM_CTX,
    AI_TIMEOUT_SECONDS,
    ALLOWED_DOC_STEMS,
    ALLOWED_EXTENSIONS,
    BLOCKED_EXECUTABLE_EXTENSIONS,
    C,
    DEBUG_MODE,
    ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX,
    ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX,
    ESOUI_BATCH_CHUNK_SIZE,
    ESOUI_LATEST_MAX_ITEMS,
    ESOUI_UPLOAD_RULES_URL,
    EXTRACT_FOLDER,
    FORBIDDEN_KEYWORDS,
    FORBIDDEN_OS_JUNK_NAMES,
    MODEL_NAME,
    OLLAMA_HOST,
    REPORTS_BASE_DIR,
    ZIP_FOLDER,
    make_clickable_file_link,
    make_clickable_url_link,
    print_wrapped_tree_item,
)

from src.esoui_download_io import download_zip, parse_last_selection_spec, read_cli_input_with_esc
from src.esoui_filelist_search import (
    extract_primary_api_version,
    get_last_updated_addons,
    is_discontinued_or_outdated,
    lookup_addon_metadata,
    search_addons,
)

from src.esoui_lua_analyzer import (
    BATCH_BEST_PRACTICE_TRACKER,
    BATCH_LEAK_TRACKER,
    collect_addon_context,
)
from src.esoui_manifest_xml_analyzer import analyze_file_content
from src.esoui_ram_index import build_esoui_index_once, get_current_api_version, is_index_built

try:
    from esoui_rules_bestpractice import CUSTOM_RULES
except ImportError:
    CUSTOM_RULES = ""

client = Client(host=OLLAMA_HOST)
OLLAMA_PREFLIGHT_CACHE = None


def _format_colored_api_version(api_str, current_api=None, base_color=""):
    """
    Colors each numeric API token relative to current_api:
      - older (< current_api): RED
      - current (== current_api): GREEN
      - newer/future (> current_api): WHITE
    """
    raw = str(api_str or "").strip()
    if not raw or raw == "?":
        return f"{C.WHITE}?{base_color}"

    cur_int = int(current_api) if (current_api and str(current_api).isdigit()) else None
    if cur_int is None:
        return f"{C.WHITE}{raw}{base_color}"

    def _color_token(match):
        tok = match.group(0)
        val = int(tok)
        if val < cur_int:
            col = C.RED
        elif val == cur_int:
            col = C.GREEN
        else:
            col = C.WHITE
        return f"{col}{tok}{C.RESET}{base_color}"

    return re.sub(r"\b\d{6}\b", _color_token, raw)


def print_addon_metadata(addon_id, force_refresh=False):
    """Displays title, author, version, and API version from filelist.json for a given addon_id."""
    try:
        meta = lookup_addon_metadata(addon_id, force=force_refresh)
        if meta:
            cur_api = get_current_api_version()
            colored_api = _format_colored_api_version(meta.get("api_version") or "?", current_api=cur_api, base_color=C.CYAN)
            aid = str(meta["addon_id"])
            clickable_id = make_clickable_url_link(f"{ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}{aid}", color=C.WHITE, display_text=aid)
            print(
                f"{C.CYAN}-> Addon Info {chr(91)}{clickable_id}{C.CYAN}{chr(93)}: "
                f"{C.WHITE}{meta['title']}{C.CYAN} | v{C.WHITE}{meta['version'] or '?'}{C.CYAN} | "
                f"by {C.WHITE}{meta['author'] or '?'}{C.CYAN} | API: {colored_api}{C.RESET}"
            )
    except Exception as e:
        if DEBUG_MODE:
            print(f"{C.YELLOW}[FILELIST-DEBUG] Metadata lookup failed for ID {addon_id}: {e}{C.RESET}")


def _extract_entry_api_display(item):
    return extract_primary_api_version(item) or "?"

def _process_addon_entries_in_chunks(entries, mode_label, chunk_size=None, force_download=False):
    """Downloads and checks selected filelist entries [(rank_idx, entry_dict), ...] in chunks."""
    if chunk_size is None:
        chunk_size = ESOUI_BATCH_CHUNK_SIZE

    if not entries:
        print(f"{C.YELLOW}No matching addons selected for '{mode_label}'.{C.RESET}\n")
        return

    t0 = datetime.now()
    total_selected = len(entries)
    print(
        f"{C.CYAN}[FILELIST] Selected {C.WHITE}{total_selected}{C.CYAN} addon(s) for '{C.WHITE}{mode_label}{C.CYAN}'. "
        f"Processing in chunks of max {C.WHITE}{chunk_size}{C.CYAN}...{C.RESET}"
    )

    for chunk_start in range(0, total_selected, chunk_size):
        chunk = entries[chunk_start:chunk_start + chunk_size]
        chunk_num = (chunk_start // chunk_size) + 1
        total_chunks = (total_selected + chunk_size - 1) // chunk_size

        print(f"\n{C.CYAN}{C.BOLD}>>> CHUNK {chunk_num}/{total_chunks}: Downloading {len(chunk)} addon(s)... <<<{C.RESET}")
        downloaded_batch = []
        for offset, (rank, item) in enumerate(chunk, 1):
            global_idx = chunk_start + offset
            addon_id = str(item.get("id") or item.get("UID") or item.get("addon_id") or "").strip()
            title_text = str(item.get("title") or item.get("UIName") or item.get("name") or "Unknown Addon").strip()
            author_text = str(item.get("author") or item.get("UIAuthorName") or "?").strip()
            version_text = str(item.get("version") or item.get("UIVersion") or "?").strip()
            api_val = _extract_entry_api_display(item)
            dl_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"

            print(
                f"{C.CYAN}{chr(91)}{global_idx}/{total_selected} | #{rank}{chr(93)}{C.RESET} "
                f"{C.WHITE}{title_text}{C.RESET} v{version_text} by {author_text} "
                f"(ID: {addon_id}, API: {api_val})"
            )
            zip_path, zip_name = download_zip(dl_url, ZIP_FOLDER, force_download=force_download)
            if zip_path and zip_name:
                downloaded_batch.append((zip_path, zip_name))
            else:
                print(f"{C.RED}  -> Skipping #{rank} (ID: {addon_id}) due to download failure.{C.RESET}")
            time.sleep(0.5)

        print(f"\n{C.CYAN}{C.BOLD}>>> CHUNK {chunk_num}/{total_chunks}: Checking {len(downloaded_batch)} downloaded addon(s)... <<<{C.RESET}")
        for zip_path, zip_name in downloaded_batch:
            process_addon(zip_path, zip_name)

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"{C.CYAN}=== '{mode_label}' finished ({C.WHITE}{total_selected}{C.CYAN} addons) in {C.MAGENTA}{elapsed:.2f} seconds{C.CYAN}. ==={C.RESET}\n")


def process_latest_filelist_in_chunks(selected_ranks, raw_spec_label=None, chunk_size=None, force_download=False):
    """Fetches top 200 live addons from filelist.json sorted by lastUpdate and processes selected_ranks."""
    if isinstance(selected_ranks, int):
        selected_ranks = list(range(1, selected_ranks + 1))

    if raw_spec_label is None:
        raw_spec_label = ", ".join(str(r) for r in selected_ranks)

    try:
        _, top_items = get_last_updated_addons(spec="", limit=ESOUI_LATEST_MAX_ITEMS, force=force_download)
    except Exception as e:
        print(f"{C.RED}[ERROR] Failed to load MMOUI filelist.json: {str(e)}{C.RESET}\n")
        return

    if not top_items:
        print(f"{C.YELLOW}No 'Live' addon entries found in MMOUI filelist.json.{C.RESET}\n")
        return

    selected_entries = []
    for rank in selected_ranks:
        if rank <= len(top_items):
            selected_entries.append((rank, top_items[rank - 1]))
        else:
            print(f"{C.YELLOW}[FILELIST] Rank #{rank} not available (only {len(top_items)} entries returned).{C.RESET}")

    _process_addon_entries_in_chunks(
        selected_entries,
        mode_label=f"last {raw_spec_label}",
        chunk_size=chunk_size,
        force_download=force_download,
    )
def handle_search_command(raw_search_args, force_download=False, auto_select_spec=None):
    """Handles 'search <q1, q2>', 'search dep <d1, d2>', 'search author <a1, a2>', and 'search api <v1, !v2>' via filelist.json."""
    query_part = (raw_search_args or "").strip()
    if not query_part:
        print(
            f"{C.RED}-> Error: Missing search term(s). Examples:\n"
            f"   - search LibAddonMenu, Master Merchant\n"
            f"   - search dep LibStub, LibAddonMenu-2.0\n"
            f"   - search author Baertram, sirinsidiator\n"
            f"   - search api 101051 (or 'search api !101051' for outdated addons){C.RESET}"
        )
        return

    search_mode = "all"
    mode_prefix = ""
    if re.match(r'^dep(?:\s+|$)', query_part, flags=re.IGNORECASE):
        search_mode = "dep"
        mode_prefix = "dep "
        query_part = query_part[3:].strip()
        if not query_part:
            print(f"{C.RED}-> Error: Missing dependency name(s) after 'search dep'. Example: 'search dep LibAddonMenu-2.0'{C.RESET}")
            return
    elif re.match(r'^author(?:\s+|$)', query_part, flags=re.IGNORECASE):
        search_mode = "author"
        mode_prefix = "author "
        query_part = query_part[6:].strip()
        if not query_part:
            print(f"{C.RED}-> Error: Missing author name(s) after 'search author'. Example: 'search author Baertram'{C.RESET}")
            return
    elif re.match(r'^api(?:\s+|$)', query_part, flags=re.IGNORECASE):
        search_mode = "api"
        mode_prefix = "api "
        query_part = query_part[3:].strip()
        if not query_part:
            print(f"{C.RED}-> Error: Missing API version(s) after 'search api'. Example: 'search api 101051' or 'search api !101051'{C.RESET}")
            return

    mode_labels = {"all": "Title/Author/ID", "dep": "Dependencies", "author": "Author", "api": "API Version"}
    print(f"\n{C.CYAN}[SEARCH] Searching {mode_labels[search_mode]} for '{C.WHITE}{query_part}{C.CYAN}'...{C.RESET}")
    try:
        hits, stage_used = search_addons(query_part, search_mode=search_mode, force=force_download)
    except Exception as e:
        print(f"{C.RED}[ERROR] Failed to search MMOUI filelist.json: {str(e)}{C.RESET}\n")
        return

    if not hits:
        print(f"{C.YELLOW}-> No matching 'Live' addons found for '{query_part}'.{C.RESET}\n")
        return

    cur_api = get_current_api_version()
    cur_api_hint = f" (Current Live API: {C.GREEN}{cur_api}{C.GREEN})" if cur_api else ""
    stage_note = f" (matched at '+' fallback stage {stage_used})" if "+" in query_part else ""
    print(f"{C.GREEN}-> Found {C.WHITE}{len(hits)}{C.GREEN} matching addon(s){stage_note}{cur_api_hint}:{C.RESET}")

    for idx, item in enumerate(hits, 1):
        addon_id = str(item.get("id") or item.get("UID") or item.get("addon_id") or "").strip()
        title_text = str(item.get("title") or item.get("UIName") or "Unknown").strip()
        author_text = str(item.get("author") or item.get("UIAuthorName") or "?").strip()
        version_text = str(item.get("version") or item.get("UIVersion") or "?").strip()
        api_val = _format_colored_api_version(_extract_entry_api_display(item), current_api=cur_api)
        clickable_id = (
            make_clickable_url_link(f"{ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}{addon_id}", color=C.CYAN, display_text=addon_id)
            if addon_id
            else f"{C.CYAN}?{C.RESET}"
        )
        if is_discontinued_or_outdated(item):
            formatted_title = f"{C.RED}{C.BOLD}✖ {title_text}{C.RESET}"
        else:
            formatted_title = f"{C.BOLD}{title_text}{C.RESET}"
        print(
            f"  {C.WHITE}{chr(91)}{idx:>3}{chr(93)}{C.RESET} {formatted_title} "
            f"(ID: {clickable_id} | v{version_text} | by {author_text} | API: {api_val})"
        )

    sel_input = auto_select_spec if auto_select_spec is not None else read_cli_input_with_esc(
        "\nSelect result number(s) to check (e.g. '1', '1-3', '2, 5', 'all', or Enter/ESC to cancel): "
    ).strip()

    if not sel_input or sel_input == "__ESC__" or sel_input.lower() in ("cancel", "exit", "0"):
        print(f"{C.CYAN}-> Search selection cancelled.{C.RESET}\n")
        return

    if sel_input.lower() == "all":
        sel_input = f"1-{len(hits)}"

    selected_ranks, err_msg = parse_last_selection_spec(sel_input, len(hits))
    if err_msg:
        print(f"{C.RED}-> Error: {err_msg}{C.RESET}\n")
        return

    selected_entries = [(rank, hits[rank - 1]) for rank in selected_ranks]
    _process_addon_entries_in_chunks(
        selected_entries,
        mode_label=f"search {mode_prefix}{query_part} [{sel_input}]",
        force_download=force_download,
    )
def _build_bbcode_zip_list(namelist, flagged_paths, manifest_paths=None):
    """Builds a nested vBulletin [SIZE="2"][list]...[/list][/SIZE] tree marking flagged items with :mad: and manifests with [MANIFEST]."""
    lb, rb = chr(91), chr(93)
    tree = {}
    flagged_norm = {p.replace("\\", "/").rstrip("/") for p in flagged_paths}
    manifest_norm = {p.replace("\\", "/").rstrip("/") for p in (manifest_paths or set())}

    for entry in namelist:
        norm = entry.replace("\\", "/").strip("/")
        if not norm:
            continue
        parts = norm.split("/")
        node = tree
        for idx, part in enumerate(parts):
            is_leaf_file = (idx == len(parts) - 1) and not entry.endswith("/")
            if part not in node:
                node[part] = None if is_leaf_file else {}
            elif node[part] is None and not is_leaf_file:
                node[part] = {}
            if not is_leaf_file:
                node = node[part]

    out_lines = [f'{lb}SIZE="2"{rb}{lb}list{rb}']

    def _walk(sub_tree, parent_path=""):
        items = sorted(sub_tree.items(), key=lambda kv: (kv[-1] is None, next(iter(kv)).lower()))
        for name, child in items:
            curr_path = f"{parent_path}/{name}" if parent_path else name
            display_name = f"{name}/" if child is not None else name
            if child is None and curr_path in manifest_norm:
                display_name = f"{display_name} {lb}MANIFEST{rb}"
            is_bad = (curr_path in flagged_norm) or any(
                curr_path.startswith(fp + "/") for fp in flagged_norm
            )
            if is_bad:
                out_lines.append(f'{lb}*{rb} {lb}color="Red"{rb}:mad: {display_name}{lb}/color{rb}')
            else:
                out_lines.append(f"{lb}*{rb} {display_name}")
            if child is not None:
                out_lines.append(f"{lb}list{rb}")
                _walk(child, curr_path)
                out_lines.append(f"{lb}/list{rb}")

    _walk(tree)
    out_lines.append(f"{lb}/list{rb}{lb}/SIZE{rb}")
    return "\n".join(out_lines)


def _check_zip_structure(zip_path, report_data):
    """Inspects all ZIP archive entries and populates report_data['zip_tree_bbcode'] & violations."""
    forbidden_entries = []
    disallowed_by_ext = defaultdict(list)
    dds_textures = []
    non_addon_files = []
    flagged_paths = set()
    manifest_paths = set()
    seen_hidden_dirs = set()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            all_entries = zip_ref.namelist()
            for entry in all_entries:
                normalized = entry.replace('\\', '/')
                parts = [p for p in normalized.split('/') if p]
                if not parts:
                    continue

                is_dir = normalized.endswith('/')
                base_filename = parts[-1].lower()
                base_stem, entry_ext = os.path.splitext(base_filename)

                hidden_or_os_reason = None
                for idx, part in enumerate(parts):
                    part_lower = part.lower()
                    if (
                        part.startswith('.')
                        or part_lower in FORBIDDEN_OS_JUNK_NAMES
                        or any(kw in part_lower for kw in FORBIDDEN_KEYWORDS)
                    ):
                        if idx < len(parts) - 1 or is_dir:
                            dir_prefix = '/'.join(parts[:idx + 1]) + '/'
                            if dir_prefix not in seen_hidden_dirs:
                                seen_hidden_dirs.add(dir_prefix)
                                hidden_or_os_reason = (dir_prefix, "hidden/dev/OS folder")
                        else:
                            hidden_or_os_reason = (normalized, "hidden/OS/dev file")
                        break

                if hidden_or_os_reason:
                    flagged_path, reason_label = hidden_or_os_reason
                    non_addon_files.append((f"{flagged_path} ({reason_label})", True))
                    forbidden_entries.append(flagged_path)
                    continue

                if is_dir:
                    continue

                is_doc_or_license = (base_stem in ALLOWED_DOC_STEMS) or (entry_ext in {'.md', '.license', '.bbcode'})
                if entry_ext == '.dds':
                    dds_textures.append(normalized)
                elif is_doc_or_license:
                    pass
                elif entry_ext in BLOCKED_EXECUTABLE_EXTENSIONS:
                    non_addon_files.append((normalized, True))
                elif entry_ext not in ALLOWED_EXTENSIONS:
                    non_addon_files.append((normalized, False))
                elif entry_ext in ('.txt', '.addon'):
                    try:
                        text_preview = zip_ref.read(entry).decode('utf-8', errors='ignore')
                        if re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', text_preview, flags=re.MULTILINE | re.IGNORECASE):
                            manifest_paths.add(normalized)
                        else:
                            non_addon_files.append((f"{normalized} (missing '## Title:' / '## AddOnVersion:' manifest tag)", False))
                    except Exception:
                        non_addon_files.append((f"{normalized} (unreadable manifest)", False))

                if not is_doc_or_license and entry_ext not in ALLOWED_EXTENSIONS:
                    disallowed_by_ext[entry_ext].append(normalized)
            if dds_textures:
                print(f"    ├── {C.CYAN}Textures (.dds) found ({len(dds_textures)}):{C.RESET}")
                for tex in sorted(dds_textures):
                    print(f"    │     - {tex}")
            else:
                print("    ├── Textures (.dds): None")

            if non_addon_files:
                has_any_critical = any(is_crit for _, is_crit in non_addon_files)
                header_color = C.RED if has_any_critical else C.YELLOW
                print(f"    └── {header_color}Non-addon-relevant / forbidden items found ({len(non_addon_files)}):{C.RESET}")
                for nf, is_crit in sorted(non_addon_files, key=lambda x: x):
                    if is_crit:
                        print_wrapped_tree_item(f"- [CRITICAL] {nf}", color=C.RED)
                    else:
                        print_wrapped_tree_item(f"- {nf}", color=C.YELLOW)
            else:
                print(f"    └── {C.GREEN}Non-addon-relevant / forbidden items: None{C.RESET}")

            for fe in forbidden_entries:
                flagged_paths.add(fe)
            for files in disallowed_by_ext.values():
                for f_item in files:
                    flagged_paths.add(f_item)

            report_data["zip_all_entries"] = list(all_entries)
            report_data["zip_flagged_paths"] = set(flagged_paths)
            report_data["zip_manifest_paths"] = set(manifest_paths)
            report_data["zip_tree_bbcode"] = _build_bbcode_zip_list(all_entries, flagged_paths, manifest_paths)

            if forbidden_entries:
                report_data["zip_violations"].append("Hidden, OS-metadata, or development folders/files found")
            for ext, files in disallowed_by_ext.items():
                report_data["zip_violations"].append(f"Disallowed file extension '{ext}' found ({len(files)} file(s))")
            for nf, is_crit in non_addon_files:
                if not is_crit:
                    report_data["best_practices"]["Possible action: Non-addon-relevant / unreferenced manifest file"].append((nf, None, ""))
    except Exception as e:
        print(f"    └── {C.RED}[ERROR] Failed to read ZIP structure: {str(e)}{C.RESET}")
        report_data["zip_violations"].append(f"Failed to read ZIP structure: {str(e)}")


def _ensure_ollama_and_model_ready(model_name):
    """Checks if Ollama is installed, starts the server if inactive, and warms up the LLM."""
    global OLLAMA_PREFLIGHT_CACHE
    if OLLAMA_PREFLIGHT_CACHE is not None:
        return OLLAMA_PREFLIGHT_CACHE

    print(f"    ├── {C.CYAN}Checking Ollama installation & server status...{C.RESET}")
    ollama_exe = shutil.which("ollama")
    if not ollama_exe and os.name == "nt":
        win_default = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Ollama", "ollama.exe")
        if os.path.isfile(win_default):
            ollama_exe = win_default

    if not ollama_exe:
        return False, "Ollama is not installed or not found in PATH."

    server_running = False
    try:
        client.list()
        server_running = True
        print(f"    │     {C.GREEN}[OK]{C.RESET} Ollama server is already active.")
    except Exception:
        print(f"    │     {C.YELLOW}⚙ Ollama server is not running. Starting background service...{C.RESET}")
        try:
            creation_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            subprocess.Popen([ollama_exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=creation_flags)
            for _ in range(20):
                time.sleep(0.5)
                try:
                    client.list()
                    server_running = True
                    print(f"    │     {C.GREEN}[OK]{C.RESET} Ollama server started successfully.")
                    break
                except Exception:
                    pass
        except Exception as start_err:
            return False, f"Failed to start Ollama server: {start_err}"

    if not server_running:
        return False, "Ollama server did not respond after startup attempt."

    try:
        models_resp = client.list()
        raw_models = models_resp.get("models", []) if isinstance(models_resp, dict) else getattr(models_resp, "models", [])
        installed_names = set()
        for m in raw_models:
            m_name = m.get("model") or m.get("name") if isinstance(m, dict) else getattr(m, "model", None) or getattr(m, "name", None)
            if m_name:
                installed_names.add(str(m_name))
                if str(m_name).endswith(":latest"):
                    installed_names.add(str(m_name)[:-7])

        target_short = model_name[:-7] if model_name.endswith(":latest") else model_name
        if model_name not in installed_names and target_short not in installed_names:
            return False, f"LLM '{model_name}' is not installed locally (install via: ollama pull {model_name})."
        print(f"    │     {C.GREEN}[OK]{C.RESET} LLM '{model_name}' found locally.")
    except Exception as list_err:
        return False, f"Could not query installed Ollama models: {list_err}"

    OLLAMA_PREFLIGHT_CACHE = (True, "Ready")
    return OLLAMA_PREFLIGHT_CACHE


def _split_large_lua_file_for_ai(rel_path, source_text, max_chars=14000):
    """
    Splits an oversized Lua file at top-level block boundaries ('end' at depth 0)
    so each chunk fits comfortably within Ollama's timeout window without breaking functions.
    Prepends top-level 'local' header declarations as read-only context for parts 2..N.
    """
    if len(source_text) <= max_chars or not rel_path.lower().endswith(".lua"):
        return [(rel_path, source_text)]

    lines = source_text.splitlines()
    # Collect top-level 'local' declarations at the top of the file as context for later chunks
    header_locals = []
    for ln in lines[:120]:
        s = ln.strip()
        if s.startswith("local ") and not s.startswith("local function"):
            header_locals.append(ln)
    header_ctx = "\n".join(header_locals[:40])

    open_rx = re.compile(r"\b(function|if|for|while|repeat|do)\b")
    close_rx = re.compile(r"\b(end|until)\b")

    chunks = []
    curr_lines = []
    curr_len = 0
    depth = 0

    for ln in lines:
        code_part = re.sub(r"--.*$", "", ln)
        code_part = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', '""', code_part)
        code_part = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", "''", code_part)

        opens = len(open_rx.findall(code_part))
        closes = len(close_rx.findall(code_part))

        curr_lines.append(ln)
        curr_len += len(ln) + 1
        depth = max(0, depth + opens - closes)

        # Split cleanly right after a top-level block closes (depth == 0)
        if depth == 0 and curr_len >= max_chars:
            chunks.append("\n".join(curr_lines))
            curr_lines = []
            curr_len = 0

    if curr_lines:
        chunks.append("\n".join(curr_lines))

    if len(chunks) <= 1:
        return [(rel_path, source_text)]

    total_parts = len(chunks)
    result_parts = []
    for idx, chunk_body in enumerate(chunks, 1):
        if idx == 1 or not header_ctx:
            part_payload = f"-- [AI CHUNK {idx}/{total_parts} OF {rel_path}]\n{chunk_body}"
        else:
            part_payload = (
                f"-- [AI CHUNK {idx}/{total_parts} OF {rel_path} - CONTINUATION]\n"
                f"-- [FILE-LEVEL LOCALS CONTEXT START - DO NOT FLAG AS UNUSED]\n"
                f"{header_ctx}\n"
                f"-- [FILE-LEVEL LOCALS CONTEXT END]\n\n"
                f"{chunk_body}"
            )
        result_parts.append((f"{rel_path} (part {idx}/{total_parts})", part_payload))
    return result_parts


def _run_ai_code_review(addon_code_bundle):
    """Reviews queued files sequentially with Ollama and returns parsed AI findings [(rel_path, status, crit_lines, bp_lines)]."""
    ai_findings = []
    if not addon_code_bundle:
        print(f"  {C.GREEN}✔ All files passed local pre-checks. Skipping AI review!{C.RESET}")
        return ai_findings

    ai_ready, status_reason = _ensure_ollama_and_model_ready(MODEL_NAME)
    if not ai_ready:
        print(f"  {C.YELLOW}⚠ AI review skipped: {status_reason} Using RAM tracker fallback...{C.RESET}")
        return ai_findings

    expanded_work_items = []
    for raw_idx, file_block in enumerate(addon_code_bundle, 1):
        lines = file_block.splitlines()
        first_line = next(iter(lines), "")
        orig_rel_path = first_line.replace("### START_FILE:", "").strip() or f"file_{raw_idx}"
        marker = "[SOURCE_CODE]\n"
        end_marker = f"\n### END_FILE: {orig_rel_path}"
        if marker in file_block:
            body_part = file_block.split(marker, 1)[1]
            if end_marker in body_part:
                body_part = body_part.split(end_marker, 1)[0]
        else:
            body_part = file_block

        parts = _split_large_lua_file_for_ai(orig_rel_path, body_part, max_chars=14000)
        if len(parts) > 1:
            print(
                f"  {C.YELLOW}ℹ Splitting large file {C.BOLD}{orig_rel_path}{C.RESET}{C.YELLOW} "
                f"into {len(parts)} scope-safe chunks to prevent AI timeout.{C.RESET}"
            )
        for display_label, part_code in parts:
            expanded_work_items.append((orig_rel_path, display_label, part_code))

    total_items = len(expanded_work_items)
    print(f"\n  {C.BLUE}{C.BOLD}[AI REVIEW] Reviewing {total_items} item(s) with Ollama ({MODEL_NAME})...{C.RESET}")

    for idx, (orig_rel_path, display_label, part_code) in enumerate(expanded_work_items, 1):
        print(f"  {C.CYAN}[AI {idx}/{total_items}]{C.RESET} Reviewing {C.BOLD}{display_label}{C.RESET}...")

        review_payload = f"### START_FILE: {display_label}\n\n[SOURCE_CODE]\n{part_code}\n### END_FILE: {display_label}\n"
        prompt = (
            f"You are a strict, silent code reviewer for Elder Scrolls Online addons.\n"
            f"Review the code section below (which may be a numbered part of a larger file) against these rules:\n{CUSTOM_RULES}\n\n"
            f"FILE TO REVIEW:\n\"\"\"\n{review_payload}\n\"\"\"\n\n"
            f"Output ONLY plain text using:\n"
            f"--- [File: {orig_rel_path}] ---\n[STATUS] PASS or FAIL\n"
            f"[CRITICAL VIOLATIONS] None OR itemized list\n"
            f"[BEST PRACTICE SUGGESTIONS] None OR itemized list\n"
        )

        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = executor.submit(
            lambda p=prompt: client.generate(
                model=MODEL_NAME,
                prompt=p,
                keep_alive="10m",
                options={"temperature": 0.0, "top_p": 0.1, "num_ctx": AI_NUM_CTX, "num_predict": 1024},
            )
        )
        start_wait = time.perf_counter()
        try:
            while not future.done():
                if int(time.perf_counter() - start_wait) >= AI_TIMEOUT_SECONDS:
                    future.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise TimeoutError("AI review timed out")
                time.sleep(0.5)
            response = future.result()
            executor.shutdown(wait=False)
            ai_response = response.get("response", "").strip()
            if "--- [File:" in ai_response and "[STATUS]" in ai_response:
                ai_findings.append((orig_rel_path, ai_response))
        except Exception as e:
            executor.shutdown(wait=False)
            print(f"    └── {C.YELLOW}⚠ AI fallback for {display_label}: {e}{C.RESET}")

    return ai_findings
def _parse_findings_into_report_data(rel_path, category, raw_result, report_data):
    """Extracts critical violations and best-practice items from an analyzer result into grouped buckets."""
    rel_norm = rel_path.replace("\\", "/")
    section = None
    for line in raw_result.splitlines():
        s = line.strip()
        if s == "[CRITICAL VIOLATIONS]":
            section = "crit"
            continue
        if s == "[BEST PRACTICE SUGGESTIONS]":
            section = "bp"
            continue
        if s.startswith("[STATUS]") or s == "None" or not s:
            continue

        if section == "crit" and s.startswith("- "):
            item_text = s[2:].strip()
            line_match = re.search(r'\b(?:at\s+)?line\s+(\d+)\b', item_text, flags=re.IGNORECASE)
            line_no = line_match.group(1) if line_match else None
            code_match = re.search(r'\(((?:--|\#\#)[^()]+(?:\([^()]*\)[^()]*)*)\)\s*\.?$', item_text)
            raw_code = code_match.group(1).strip() if code_match else ""
            code_comment = re.sub(r'^--\s*', '', raw_code)
            rule_title = re.sub(r'\s*\((?:at\s+)?line\s+\d+\)|\s+at\s+line\s+\d+', '', item_text, flags=re.IGNORECASE)
            if code_match:
                rule_title = rule_title[:rule_title.rfind("(")].strip().rstrip(":")
            else:
                rule_title = next(iter(rule_title.split(":", 1))).strip()
            report_data["critical"][category][rule_title].append((rel_norm, line_no, code_comment))

        elif section == "bp":
            if s.startswith("- "):
                bp_header = s[2:].strip()
                if "without a local reference" in bp_header:
                    bp_rule = "Possible action: Global variable used multiple times without a local reference"
                elif "Startup Chat Spam" in bp_header:
                    bp_rule = "Possible action: Startup Chat Spam Detected (unconditional message on load/player activated)"
                elif "Manifest .addon found" in bp_header:
                    bp_rule = "Possible action: Console UI Manifest Notice (.addon used instead of .txt)"
                elif "Mandatory version check >= outdated - consider an update" in bp_header:
                    bp_rule = "Possible action: Mandatory version check >= outdated - consider an update"
                    ln_m = re.search(r'\bline\s+(\d+)\b', bp_header, flags=re.IGNORECASE)
                    c_m = re.search(r'\((##[^()]+(?:\([^()]*\)[^()]*)*)\)\s*\.?$', bp_header)
                    report_data["best_practices"][bp_rule].append(
                        (rel_norm, ln_m.group(1) if ln_m else None, c_m.group(1).strip() if c_m else "")
                    )
                else:
                    bp_rule = "Possible action: " + next(iter(bp_header.split(":", 1))).strip()
                report_data["_last_bp_rule"] = bp_rule
                if "Manifest .addon found" in bp_header:
                    report_data["best_practices"][bp_rule].append((rel_norm, "1", ""))
            elif report_data.get("_last_bp_rule"):
                hit_m = re.match(r'^([A-Za-z0-9_]+):(\d+)\s+--\s*(.*)$', s)
                num_m = re.match(r'^(\d+):\s+--\s*(.*)$', s)
                if hit_m:
                    var_n, ln_no, c_txt = hit_m.group(1), hit_m.group(2), hit_m.group(3).strip()
                    grouped_vars = report_data.setdefault("bp_grouped_globals", defaultdict(lambda: defaultdict(list)))
                    grouped_vars[var_n][rel_norm].append((ln_no, c_txt))
                elif num_m:
                    ln_no, c_txt = num_m.group(1), num_m.group(2).strip()
                    report_data["best_practices"][report_data["_last_bp_rule"]].append((rel_norm, ln_no, c_txt))

def _render_final_bbcode_report(report_file_path, zip_name, timestamp_str, report_data):
    """Writes the compact, grouped ESOUI BBCode report without any PASS noise."""
    lb, rb = chr(91), chr(93)
    out = [
        "Welcome. Please review the add-on upload rules and best practices, and ensure all of your uploads follow them:",
        f"{lb}url{rb}{ESOUI_UPLOAD_RULES_URL}{lb}/url{rb}",
        "",
        "Below you'll find the report for your uploaded zip archive. Only findings requiring attention are listed.",
        "Please also read the other rules and best practices, especially the AI disclosure and credits parts, and apply them where applicable.",
        "Thank you very much for supporting our addon quality and compatibility efforts.",
        "",
        f'{lb}b{rb}{lb}u{rb}{lb}color="RoyalBlue"{rb}Addon check - report results{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}',
        f"{lb}b{rb}TIMESTAMP{lb}/b{rb}:    {timestamp_str}",
        f"{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {zip_name}",
    ]

    if report_data.get("zip_tree_bbcode"):
        out.append(report_data["zip_tree_bbcode"])

    unverified_entries = report_data.get("unverified_globals") or []
    has_crit = bool(report_data["zip_violations"]) or any(bool(v) for v in report_data["critical"].values())
    has_unverified = bool(unverified_entries)
    has_bp = bool(report_data["best_practices"]) or bool(report_data.get("bp_grouped_globals"))

    if has_crit:
        out.append(f'{lb}SIZE="4"{rb}{lb}b{rb}{lb}u{rb}{lb}color="Red"{rb}{lb}FONT="Impact"{rb}Critical violations{lb}/FONT{rb}{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}{lb}/SIZE{rb}')
        if report_data["zip_violations"]:
            out.append("")
            out.append(f'{lb}b{rb}{lb}FONT="Book Antiqua"{rb}ZIP Archive{lb}/FONT{rb}{lb}/b{rb}')
            out.append(f"{lb}list{rb}")
            for zv in dict.fromkeys(report_data["zip_violations"]):
                out.append(f"{lb}*{rb} {zv}")
            out.append(f"{lb}/list{rb}")

        for cat_key, cat_label in (("manifest", "Manifest (.addon / .txt)"), ("lua", "Lua Files"), ("xml", "XML Files")):
            rules_map = report_data["critical"].get(cat_key)
            if not rules_map:
                continue
            out.append("")
            out.append(f'{lb}b{rb}{lb}FONT="Book Antiqua"{rb}{cat_label}{lb}/FONT{rb}{lb}/b{rb}')
            for rule_title, entries in rules_map.items():
                out.append(f"{lb}u{rb}{rule_title}{lb}/u{rb}")
                out.append(f"{lb}list{rb}")
                for f_path, ln_no, code_txt in entries:
                    loc = f"{f_path}:{ln_no}" if ln_no else f_path
                    spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                    out.append(f"{lb}*{rb} {loc}{spoiler_part}")
                out.append(f"{lb}/list{rb}")

    if has_unverified:
        out.append("")
        out.append(f'{lb}SIZE="4"{rb}{lb}b{rb}{lb}u{rb}{lb}color="DarkOrchid"{rb}{lb}FONT="Impact"{rb}Unverified Globals{lb}/FONT{rb}{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}{lb}/SIZE{rb}')
        out.append("")
        out.append(f"{lb}u{rb}Not found in ESO API Documentation / Custom-Stubs (please verify local/global scope){lb}/u{rb}")
        out.append(f"{lb}list{rb}")
        for f_path, code_txt in unverified_entries:
            spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
            out.append(f"{lb}*{rb} {f_path}{spoiler_part}")
        out.append(f"{lb}/list{rb}")

    if has_bp:
        out.append("")
        out.append(f'{lb}SIZE="4"{rb}{lb}b{rb}{lb}u{rb}{lb}color="DarkOrange"{rb}{lb}FONT="Impact"{rb}Best practices{lb}/FONT{rb}{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}{lb}/SIZE{rb}')

        outdated_dep_rule = "Possible action: Mandatory version check >= outdated - consider an update"
        outdated_entries = report_data["best_practices"].get(outdated_dep_rule)
        if outdated_entries:
            out.append("")
            out.append(f"{lb}u{rb}{outdated_dep_rule}{lb}/u{rb}")
            out.append(f"{lb}list{rb}")
            for f_path, ln_no, code_txt in outdated_entries:
                loc = f"{f_path}:{ln_no}" if ln_no else f_path
                spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                out.append(f"{lb}*{rb} {loc}{spoiler_part}")
            out.append(f"{lb}/list{rb}")

        grouped_globals = report_data.get("bp_grouped_globals")
        if grouped_globals:
            out.append("")
            out.append(f"{lb}u{rb}Possible action: Global variable used multiple times without a local reference{lb}/u{rb}")
            out.append(f"{lb}list{rb}")
            for var_name in sorted(grouped_globals.keys(), key=lambda x: x.lower()):
                files_map = grouped_globals[var_name]
                total_hits = sum(len(hits) for hits in files_map.values())
                spoiler_lines = []
                for f_path in sorted(files_map.keys(), key=lambda x: x.lower()):
                    spoiler_lines.append(f"{lb}u{rb}{lb}b{rb}{f_path}{lb}/b{rb}{lb}/u{rb}")
                    for ln_no, code_txt in files_map[f_path]:
                        spoiler_lines.append(f"  {ln_no}: {code_txt}")
                spoiler_body = "\n".join(spoiler_lines)
                out.append(
                    f'{lb}*{rb} {lb}b{rb}{var_name}{lb}/b{rb} (x{total_hits}) '
                    f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                )
            out.append(f"{lb}/list{rb}")

        for bp_rule, entries in report_data["best_practices"].items():
            if bp_rule == outdated_dep_rule:
                continue
            out.append("")
            out.append(f"{lb}u{rb}{bp_rule}{lb}/u{rb}")
            out.append(f"{lb}list{rb}")
            for f_path, ln_no, code_txt in entries:
                loc = f"{f_path}:{ln_no}" if ln_no else f_path
                spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                out.append(f"{lb}*{rb} {loc}{spoiler_part}")
            out.append(f"{lb}/list{rb}")

    if not has_crit and not has_unverified and not has_bp:
        out.append("")
        out.append(f'{lb}color="Green"{rb}No critical violations or best practice issues found.{lb}/color{rb}')

    with open(report_file_path, "w", encoding="utf-8") as wf:
        wf.write("\n".join(out).strip() + "\n")
def process_addon(zip_path, zip_name):
    """Coordinates ZIP audit, extraction, static analysis, AI review, and compact BBCode report."""
    addon_start_time = datetime.now()
    BATCH_LEAK_TRACKER.clear()
    BATCH_BEST_PRACTICE_TRACKER.clear()

    print(f"{C.CYAN}-------------------------------------------------------------------{C.RESET}")
    clickable_zip_start = make_clickable_file_link(zip_path, color=C.WHITE, display_text=zip_name)
    print(f"{C.CYAN}{C.BOLD}  ADDON START: {clickable_zip_start}")

    os.makedirs(EXTRACT_FOLDER, exist_ok=True)
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
    current_date_report_dir = os.path.join(REPORTS_BASE_DIR, now.strftime("%y%m%d"))
    os.makedirs(current_date_report_dir, exist_ok=True)

    zip_clean_name = zip_name[:-4] if zip_name.lower().endswith('.zip') else zip_name
    current_report_file = os.path.join(current_date_report_dir, f"{now.strftime('%y%m%d_%H%M%S')}_{zip_clean_name}.txt")
    addon_code_bundle = []
    ai_preflight_triggered = False

    report_data = {
        "zip_tree_bbcode": "",
        "zip_violations": [],
        "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
        "best_practices": defaultdict(list),
    }

    print(f"{C.CYAN}[2/4] Analyzing ZIP structure and extracting archive...{C.RESET}")
    _check_zip_structure(zip_path, report_data)

    current_extract_dir = os.path.join(EXTRACT_FOLDER, zip_clean_name)
    if os.path.exists(current_extract_dir):
        shutil.rmtree(current_extract_dir)
    os.makedirs(current_extract_dir)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(current_extract_dir)

        print(f"{C.CYAN}[3/4] Running static checks & building AI batch context...{C.RESET}")
        if not is_index_built():
            build_esoui_index_once()
        addon_ctx = collect_addon_context(current_extract_dir)

        files_to_process = []
        for root, _, files in os.walk(current_extract_dir):
            for file in files:
                lower_file = file.lower()
                if lower_file.endswith(('.xml', '.lua', '.txt', '.addon')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, current_extract_dir)
                    priority = 0 if lower_file.endswith(('.addon', '.txt')) else (1 if lower_file.endswith('.xml') else 2)
                    files_to_process.append((priority, rel_path.lower(), file, file_path, rel_path))

        files_to_process.sort(key=lambda item: (item, item))

        for _, _, file, file_path, rel_path in files_to_process:
            lower_file = file.lower()
            category = "manifest" if lower_file.endswith(('.addon', '.txt')) else ("xml" if lower_file.endswith('.xml') else "lua")
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if category == "manifest":
                    if not re.search(r'^\s*##\s*(?:Title|AddOnVersion)\s*:', content, flags=re.MULTILINE | re.IGNORECASE):
                        continue
                print(f"\n  {C.BOLD}[FILE]{C.RESET} {rel_path}")
                result = analyze_file_content(rel_path, content, current_extract_dir, addon_ctx)
                if result.startswith("[STATUS] FAIL") or result.startswith("[STATUS] PASS"):
                    is_fail = result.startswith("[STATUS] FAIL")
                    status_tag = f"{C.RED}[FAIL]{C.RESET}" if is_fail else f"{C.GREEN}[PASS]{C.RESET}"
                    if category != "lua":
                        file_label = "XML" if category == "xml" else "Manifest"
                        if is_fail:
                            print(f"    ├── {status_tag} {file_label} check failed:")
                            in_crit = False
                            for r_line in result.splitlines():
                                stripped_r = r_line.strip()
                                if stripped_r == "[CRITICAL VIOLATIONS]":
                                    in_crit = True
                                    continue
                                if stripped_r.startswith("[BEST PRACTICE"):
                                    break
                                if in_crit and stripped_r.startswith("- "):
                                    print_wrapped_tree_item(stripped_r, color=C.RED)
                            print(f"    └── {C.RED}See report for full details.{C.RESET}")
                        else:
                            print(f"    └── {status_tag} {file_label} check finished.")
                    _parse_findings_into_report_data(rel_path, category, result, report_data)
                else:
                    if category == "xml":
                        print(f"    └── {C.BLUE}[QUEUE FOR AI]{C.RESET} {C.CYAN}XSD valid, queued for semantic XML review.{C.RESET}")
                    if not ai_preflight_triggered:
                        ai_preflight_triggered = True
                        _ensure_ollama_and_model_ready(MODEL_NAME)
                    clean_lines_for_ai = [line for line in content.splitlines() if line.strip() and not line.strip().startswith("--")]
                    addon_code_bundle.append("### START_FILE: " + rel_path + "\n\n[SOURCE_CODE]\n" + "\n".join(clean_lines_for_ai) + "\n### END_FILE: " + rel_path + "\n")
            except Exception as e:
                print(f"    └── {C.RED}[ERROR]{C.RESET} {str(e)}")
                report_data["critical"][category]["File Read Error"].append((rel_path.replace("\\", "/"), None, f"-- {e}"))
    except Exception as e:
        print(f"  {C.RED}[ERROR] Failed to extract ZIP: {str(e)}{C.RESET}")
        report_data["zip_violations"].append(f"Failed to extract ZIP: {e}")

    print("")
    ai_findings = _run_ai_code_review(addon_code_bundle)
    for ai_file, ai_resp in ai_findings:
        ai_cat = "xml" if ai_file.lower().endswith(".xml") else "lua"
        _parse_findings_into_report_data(ai_file, ai_cat, ai_resp, report_data)

    for leak_file, leaks in BATCH_LEAK_TRACKER.items():
        if leaks:
            report_data.setdefault("unverified_globals", []).append(
                (leak_file.replace("\\", "/"), ", ".join(leaks))
            )
    for bp_file, suggs in BATCH_BEST_PRACTICE_TRACKER.items():
        if suggs:
            _parse_findings_into_report_data(bp_file, "lua", "[BEST PRACTICE SUGGESTIONS]\n" + "\n".join(f"  - {s}" for s in suggs), report_data)

    all_flagged = set(report_data.get("zip_flagged_paths", set()))
    for cat_rules in report_data["critical"].values():
        for entries in cat_rules.values():
            for f_path, _, _ in entries:
                all_flagged.add(f_path)
    if report_data.get("zip_all_entries"):
        report_data["zip_tree_bbcode"] = _build_bbcode_zip_list(
            report_data["zip_all_entries"],
            all_flagged,
            report_data.get("zip_manifest_paths", set()),
        )

    _render_final_bbcode_report(current_report_file, zip_name, timestamp_str, report_data)

    if os.path.exists(EXTRACT_FOLDER):
        shutil.rmtree(EXTRACT_FOLDER)
    addon_duration = (datetime.now() - addon_start_time).total_seconds()
    print(f"\n{C.CYAN}[4/4] Report saved to:{C.RESET} {make_clickable_file_link(current_report_file)}")
    print(f"{C.CYAN}{C.BOLD}  ADDON END:   {C.WHITE}{zip_name}{C.CYAN} ({C.MAGENTA}{addon_duration:.2f}s{C.CYAN}){C.RESET}")
    print(f"{C.CYAN}{C.BOLD}=================================================================={C.RESET}\n")
