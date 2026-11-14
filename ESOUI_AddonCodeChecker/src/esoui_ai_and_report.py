"""
ZIP-Strukturprüfung, MMOUI-Filelist-Orchestrierung, Ollama-AI-Review und BBCode-Report-Generierung.
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
    ESOUI_BATCH_CHUNK_SIZE,
    ESOUI_LATEST_MAX_ITEMS,
    EXTRACT_FOLDER,
    FORBIDDEN_KEYWORDS,
    FORBIDDEN_OS_JUNK_NAMES,
    MODEL_NAME,
    OLLAMA_HOST,
    REPORTS_BASE_DIR,
    ZIP_FOLDER,
    make_clickable_file_link,
    print_wrapped_tree_item,
)
from src.esoui_download_io import download_zip, parse_last_selection_spec, read_cli_input_with_esc
from src.esoui_filelist_search import (
    get_last_updated_addons,
    lookup_addon_metadata,
    search_addons,
)
from src.esoui_ram_index import build_esoui_index_once, is_index_built
from src.esoui_lua_analyzer import (
    BATCH_BEST_PRACTICE_TRACKER,
    BATCH_LEAK_TRACKER,
    collect_addon_context,
)
from src.esoui_manifest_xml_analyzer import analyze_file_content


try:
    from esoui_rules_bestpractice import CUSTOM_RULES
except ImportError:
    CUSTOM_RULES = ""

client = Client(host=OLLAMA_HOST)
OLLAMA_PREFLIGHT_CACHE = None


def print_addon_metadata(addon_id, force_refresh=False):
    """Displays title, author, version, and API version from filelist.json for a given addon_id."""
    try:
        meta = lookup_addon_metadata(addon_id, force=force_refresh)
        if meta:
            print(
                f"{C.CYAN}-> Addon Info [{C.WHITE}{meta['addon_id']}{C.CYAN}]: "
                f"{C.WHITE}{meta['title']}{C.CYAN} | v{C.WHITE}{meta['version'] or '?'}{C.CYAN} | "
                f"by {C.WHITE}{meta['author'] or '?'}{C.CYAN} | API: {C.WHITE}{meta['api_version'] or '?'}{C.RESET}"
            )
    except Exception as e:
        if DEBUG_MODE:
            print(f"{C.YELLOW}[FILELIST-DEBUG] Metadata lookup failed for ID {addon_id}: {e}{C.RESET}")


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
            title_text = str(item.get("title") or item.get("name") or "Unknown Addon").strip()
            author_text = str(item.get("author") or item.get("authorName") or "?").strip()
            version_text = str(item.get("version") or "?").strip()
            api_val = item.get("apiversion") or item.get("apiVersion") or item.get("compatible") or "?"
            if isinstance(api_val, list):
                api_val = ", ".join(str(x) for x in api_val)
            dl_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"

            print(
                f"{C.CYAN}[{global_idx}/{total_selected} | #{rank}]{C.RESET} "
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
            f"   - search api 101043 (or 'search api !101043' for outdated addons){C.RESET}"
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
            print(f"{C.RED}-> Error: Missing API version(s) after 'search api'. Example: 'search api 101043' or 'search api !101043'{C.RESET}")
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

    stage_note = f" (matched at '+' fallback stage {stage_used})" if "+" in query_part else ""
    print(f"{C.GREEN}-> Found {C.WHITE}{len(hits)}{C.GREEN} matching addon(s){stage_note}:{C.RESET}")

    for idx, item in enumerate(hits, 1):
        addon_id = str(item.get("id") or item.get("UID") or item.get("addon_id") or "").strip()
        title_text = str(item.get("title") or item.get("name") or "Unknown").strip()
        author_text = str(item.get("author") or item.get("authorName") or "?").strip()
        version_text = str(item.get("version") or "?").strip()
        api_val = item.get("apiversion") or item.get("apiVersion") or item.get("compatible") or "?"
        if isinstance(api_val, list):
            api_val = ", ".join(str(x) for x in api_val)
        print(
            f"  {C.WHITE}[{idx:>3}]{C.RESET} {C.BOLD}{title_text}{C.RESET} "
            f"(ID: {C.CYAN}{addon_id}{C.RESET} | v{version_text} | by {author_text} | API: {api_val})"
        )

    sel_input = auto_select_spec if auto_select_spec is not None else read_cli_input_with_esc(
        f"\nSelect result number(s) to check (e.g. '1', '1-3', '2, 5', 'all', or Enter/ESC to cancel): "
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
def _check_zip_structure(zip_path, report):
    """Inspects all ZIP archive entries against allowed/blocked extensions and hidden/OS junk rules."""
    forbidden_entries = []
    disallowed_by_ext = defaultdict(list)
    dds_textures = []
    non_addon_files = []
    seen_hidden_dirs = set()

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for entry in zip_ref.namelist():
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
                        if not re.search(r'^\s*##\s*Title\s*:', text_preview, flags=re.MULTILINE | re.IGNORECASE):
                            non_addon_files.append((f"{normalized} (missing '## Title:' manifest tag)", False))
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
                for nf, is_crit in sorted(non_addon_files, key=lambda x: x[0]):
                    if is_crit:
                        print_wrapped_tree_item(f"- [CRITICAL] {nf}", color=C.RED)
                    else:
                        print_wrapped_tree_item(f"- {nf}", color=C.YELLOW)
            else:
                print(f"    └── {C.GREEN}Non-addon-relevant / forbidden items: None{C.RESET}")

            report.write("--- [ZIP Archive Structure Analysis] ---\n")
            if non_addon_files:
                report.write(f"[NON-ADDON-RELEVANT / FORBIDDEN ITEMS - {len(non_addon_files)} item(s)]\n")
                for nf, is_crit in sorted(non_addon_files, key=lambda x: x[0]):
                    prefix = "[CRITICAL] " if is_crit else ""
                    report.write(f"  - {prefix}{nf}\n")
                report.write("\n")

            if forbidden_entries or disallowed_by_ext:
                report.write("[STATUS] FAIL\n[CRITICAL VIOLATIONS]\n")
                if forbidden_entries:
                    report.write("  - Hidden, OS-metadata, or development folders/files found:\n")
                    for entry in sorted(set(forbidden_entries)):
                        report.write("    " + entry + "\n")
                for ext, files in disallowed_by_ext.items():
                    report.write("  - Disallowed file extension " + ext + ":\n")
                    for entry in files:
                        report.write("    " + entry + "\n")
            else:
                report.write("[STATUS] PASS\n")
            report.write("\n" + "=" * 50 + "\n\n")
    except Exception as e:
        print(f"    └── {C.RED}[ERROR] Failed to read ZIP structure: {str(e)}{C.RESET}")
        report.write("Failed to read ZIP structure: " + str(e) + "\n\n")


def _write_ram_tracker_fallback(report, target_files=None):
    """Writes unverified globals from BATCH_LEAK_TRACKER for all or specific files."""
    items = BATCH_LEAK_TRACKER.items() if target_files is None else [
        (f, BATCH_LEAK_TRACKER.get(f, [])) for f in target_files
    ]
    for rel_file_path, leaks in items:
        report.write(f"--- [File: {rel_file_path}] ---\n")
        if leaks:
            report.write("[STATUS] WARN\n[CRITICAL VIOLATIONS]\n")
            report.write("  - Unverified Globals found (Not in API-Doc / Custom-Stubs):\n")
            for index, leak in enumerate(leaks, 1):
                report.write(f"    {index}. {leak}\n")
            report.write("[BEST PRACTICE SUGGESTIONS] If these are valid variables, please add them to your 'eso-api_base_Manual_NonGenerated.lua' file.\n\n")
        else:
            report.write("[STATUS] PASS\n\n")
        report.write("--------------------------------------------------\n\n")
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

    try:
        ps_resp = client.ps()
        running_models = ps_resp.get("models", []) if isinstance(ps_resp, dict) else getattr(ps_resp, "models", [])
        is_loaded = any(
            (rm.get("model") or rm.get("name") if isinstance(rm, dict) else getattr(rm, "model", None) or getattr(rm, "name", None))
            in (model_name, target_short + ":latest")
            for rm in running_models
        )
        if is_loaded:
            print(f"    │     {C.GREEN}[OK]{C.RESET} LLM '{model_name}' is already loaded in memory.")
        else:
            print(f"    │     {C.CYAN}⚙ Loading LLM '{model_name}' into memory...{C.RESET}")
            load_start = time.perf_counter()
            client.generate(model=model_name, prompt="", keep_alive="10m")
            load_ms = (time.perf_counter() - load_start) * 1000
            print(f"    │     {C.GREEN}[OK]{C.RESET} LLM '{model_name}' loaded and active ({C.MAGENTA}{load_ms:.0f} ms{C.RESET}).")
    except Exception:
        pass

    OLLAMA_PREFLIGHT_CACHE = (True, "Ready")
    return OLLAMA_PREFLIGHT_CACHE


def _run_ai_code_review(addon_code_bundle, report):
    """Reviews each queued file individually with Ollama using configurable context and template rules."""
    if BATCH_BEST_PRACTICE_TRACKER:
        report.write("--- [Local Static Best Practice Report] ---\n")
        for rel_file_path, suggestions in BATCH_BEST_PRACTICE_TRACKER.items():
            report.write(f"--- [File: {rel_file_path}] ---\n[BEST PRACTICE SUGGESTIONS]\n")
            for s in suggestions:
                report.write("  - " + s + "\n")
            report.write("\n--------------------------------------------------\n\n")

    if not addon_code_bundle:
        print(f"  {C.GREEN}✔ All files passed local pre-checks. Skipping AI review!{C.RESET}")
        return

    report.write("--- [Unified AI Code Review Report] ---\n")
    ai_ready, status_reason = _ensure_ollama_and_model_ready(MODEL_NAME)
    if not ai_ready:
        print(f"  {C.YELLOW}⚠ AI review skipped: {status_reason} Using RAM tracker fallback...{C.RESET}")
        _write_ram_tracker_fallback(report)
        return

    total_files = len(addon_code_bundle)
    banner_msg = f"[AI REVIEW] Reviewing {total_files} file(s) sequentially with Ollama ({MODEL_NAME}) [Timeout: {AI_TIMEOUT_SECONDS}s/file]..."
    box_inner_width = len(banner_msg) + 4
    print(f"\n  {C.BLUE}{C.BOLD}╔{'═' * box_inner_width}╗{C.RESET}")
    print(f"  {C.BLUE}{C.BOLD}║  {banner_msg}  ║{C.RESET}")
    print(f"  {C.BLUE}{C.BOLD}╚{'═' * box_inner_width}╝{C.RESET}")

    max_chars_per_file = 42000
    for idx, file_block in enumerate(addon_code_bundle, 1):
        lines = file_block.splitlines()
        first_line = next(iter(lines), "")
        rel_path = first_line.replace("### START_FILE:", "").strip() or f"file_{idx}"
        print(f"\n  {C.CYAN}[AI {idx}/{total_files}]{C.RESET} Reviewing {C.BOLD}{rel_path}{C.RESET}...")

        review_payload = file_block
        if len(review_payload) > max_chars_per_file:
            review_payload = review_payload[:22000] + "\n\n-- [... MIDDLE SECTION TRUNCATED FOR CONTEXT LIMIT ...] --\n\n" + review_payload[-18000:]

        prompt = (
            f"You are a strict, silent code reviewer for Elder Scrolls Online addons.\n"
            f"Review the single file below against these rules:\n{CUSTOM_RULES}\n\n"
            f"FILE TO REVIEW:\n\"\"\"\n{review_payload}\n\"\"\"\n\n"
            f"STRICT OUTPUT INSTRUCTIONS (DO NOT IGNORE):\n"
            f"- NEVER output JSON, markdown code fences (```), introductions, or explanations.\n"
            f"- If the file has NO violations AND NO suggestions, output ONLY these 2 lines:\n"
            f"--- [File: {rel_path}] ---\n[STATUS] PASS\n\n"
            f"- Otherwise, output ONLY this exact plain-text template:\n"
            f"--- [File: {rel_path}] ---\n[STATUS] PASS or FAIL\n"
            f"[CRITICAL VIOLATIONS] None OR itemized list of real violations\n"
            f"[BEST PRACTICE SUGGESTIONS] None OR itemized list of real suggestions\n"
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
            timed_out = False
            while not future.done():
                elapsed_sec = int(time.perf_counter() - start_wait)
                if elapsed_sec >= AI_TIMEOUT_SECONDS:
                    future.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)
                    timed_out = True
                    break
                print(f"\r    ├── {C.CYAN}⏳ Waiting for Ollama... ({elapsed_sec}s / {AI_TIMEOUT_SECONDS}s){C.RESET}", end="", flush=True)
                time.sleep(0.5)

            elapsed_ms = (time.perf_counter() - start_wait) * 1000
            print("\r" + " " * 75 + "\r", end="", flush=True)
            print(f"    ├── {C.CYAN}AI review took {C.MAGENTA}{elapsed_ms:.2f} ms{C.RESET}")

            if timed_out:
                print(f"    └── {C.YELLOW}⚠ Timed out after {AI_TIMEOUT_SECONDS}s. Using RAM tracker fallback...{C.RESET}")
                _write_ram_tracker_fallback(report, target_files=[rel_path])
                continue

            response = future.result()
            executor.shutdown(wait=False)
            ai_response = response.get('response', '').strip()
            if ai_response.startswith("```"):
                ai_response = re.sub(r'^```[a-zA-Z]*\n?', '', ai_response)
                ai_response = re.sub(r'\n?```$', '', ai_response).strip()

            invalid_template = (
                "I'm sorry" in ai_response
                or "assist with that request" in ai_response
                or ai_response.startswith("{")
                or "--- [File:" not in ai_response
                or "[STATUS]" not in ai_response
                or len(ai_response) < 10
            )
            if invalid_template:
                print(f"    └── {C.YELLOW}⚠ AI returned invalid format/JSON. Using RAM tracker fallback...{C.RESET}")
                _write_ram_tracker_fallback(report, target_files=[rel_path])
            else:
                print(f"    └── {C.GREEN}✔ AI review completed.{C.RESET}")
                report.write(ai_response + "\n\n--------------------------------------------------\n\n")
        except Exception as e:
            executor.shutdown(wait=False)
            print(f"    └── {C.RED}✖ AI Execution Error: {str(e)}{C.RESET}")
            _write_ram_tracker_fallback(report, target_files=[rel_path])


def _apply_bbcode_report_styling(report_file_path):
    """Formats the finalized plain-text report into ESOUI forum BBCode with list and spoiler tags."""
    lb, rb = chr(91), chr(93)
    try:
        with open(report_file_path, "r", encoding="utf-8") as rf:
            styled_report = rf.read()

        styled_report = re.sub(r'^[=-]{10,}\s*\n?', '', styled_report, flags=re.MULTILINE)
        styled_report = re.sub(r'^===\s*END OF REPORT\s*===\s*\n?', '', styled_report, flags=re.MULTILINE)
        styled_report = re.sub(
            r'^---\s*(\[ZIP Archive Structure Analysis\])\s*---',
            rf'{lb}u{rb}{lb}b{rb}Report results - Please review and fix where applicable{lb}/b{rb}{lb}/u{rb}\n\n{lb}u{rb}{lb}b{rb}\1{lb}/b{rb}{lb}/u{rb}',
            styled_report,
            flags=re.MULTILINE,
        )
        styled_report = re.sub(r'^---\s*(\[[^\]]+\])\s*---', rf'{lb}u{rb}\1{lb}/u{rb}', styled_report, flags=re.MULTILINE)
        styled_report = re.sub(r'^\[STATUS\]\s+FAIL\b', f'{lb}STATUS{rb} {lb}color="Red"{rb}FAIL{lb}/color{rb}', styled_report, flags=re.MULTILINE)
        styled_report = re.sub(r'^\[STATUS\]\s+PASS(?:ED)?\b', f'{lb}STATUS{rb} {lb}color="Green"{rb}PASS{lb}/color{rb}', styled_report, flags=re.MULTILINE)
        styled_report = re.sub(
            r'^\[CRITICAL VIOLATIONS\]\s*\n(\s+- )',
            rf'{lb}color="Red"{rb}{lb}CRITICAL VIOLATIONS{rb}{lb}/color{rb}\n\1',
            styled_report,
            flags=re.MULTILINE,
        )
        styled_report = re.sub(
            r'^\[BEST PRACTICE SUGGESTIONS\]\s+None\b',
            f'{lb}BEST PRACTICE SUGGESTIONS{rb} {lb}color="Green"{rb}None{lb}/color{rb}',
            styled_report,
            flags=re.MULTILINE,
        )
        styled_report = re.sub(
            r'^\[NON-ADDON-RELEVANT / FORBIDDEN ITEMS\s*-\s*(\d+\s*item\(s\))\]',
            rf'{lb}color="Red"{rb}{lb}NON-ADDON-RELEVANT / FORBIDDEN:{lb}/color{rb} \1{lb}color="Red"{rb}{rb}{lb}/color{rb}',
            styled_report,
            flags=re.MULTILINE,
        )

        formatted_lines = []
        in_bb_list = False
        in_spoiler = False
        for line in styled_report.splitlines():
            bullet_match = re.match(r'^\s{1,4}-\s+(.*)$', line)
            is_continuation = in_bb_list and bool(re.match(r'^\s{4,}\S', line))
            if bullet_match:
                if in_spoiler:
                    formatted_lines.append(f"{lb}/spoiler{rb}")
                    in_spoiler = False
                if not in_bb_list:
                    formatted_lines.append(f"{lb}list{rb}")
                    in_bb_list = True
                formatted_lines.append(f"{lb}*{rb} {bullet_match.group(1)}")
            elif is_continuation:
                if not in_spoiler:
                    formatted_lines.append(f"{lb}spoiler{rb}")
                    in_spoiler = True
                formatted_lines.append(line)
            else:
                if in_spoiler:
                    formatted_lines.append(f"{lb}/spoiler{rb}")
                    in_spoiler = False
                if in_bb_list:
                    formatted_lines.append(f"{lb}/list{rb}")
                    in_bb_list = False
                formatted_lines.append(line)
        if in_spoiler:
            formatted_lines.append(f"{lb}/spoiler{rb}")
        if in_bb_list:
            formatted_lines.append(f"{lb}/list{rb}")

        with open(report_file_path, "w", encoding="utf-8") as wf:
            wf.write("\n".join(formatted_lines).strip() + "\n")
    except Exception as bb_err:
        print(f"  {C.YELLOW}⚠ Could not apply BBCode styling to report: {bb_err}{C.RESET}")


def process_addon(zip_path, zip_name):
    """Coordinates ZIP audit, extraction, static analysis, AI review, and cleanup."""
    lb, rb = chr(91), chr(93)
    addon_start_time = datetime.now()
    BATCH_LEAK_TRACKER.clear()
    BATCH_BEST_PRACTICE_TRACKER.clear()

    print(f"{C.CYAN}-------------------------------------------------------------------{C.RESET}")
    clickable_zip_start = make_clickable_file_link(zip_path, color=C.WHITE, display_text=zip_name)
    print(f"{C.CYAN}{C.BOLD}  ADDON START: {clickable_zip_start}")

    os.makedirs(EXTRACT_FOLDER, exist_ok=True)
    now = datetime.now()
    current_date_report_dir = os.path.join(REPORTS_BASE_DIR, now.strftime("%y%m%d"))
    os.makedirs(current_date_report_dir, exist_ok=True)

    zip_clean_name = zip_name[:-4] if zip_name.lower().endswith('.zip') else zip_name
    current_report_file = os.path.join(current_date_report_dir, f"{now.strftime('%y%m%d_%H%M%S')}_{zip_clean_name}.txt")
    addon_code_bundle = []
    ai_preflight_triggered = False

    with open(current_report_file, "w", encoding="utf-8") as report:
        print(f"{C.CYAN}[2/4] Analyzing ZIP structure and extracting archive...{C.RESET}")
        report.write(f'{lb}u{rb}{lb}color="DarkOrange"{rb}ESOUI ADDON UPLOAD CHECK REPORT{lb}/color{rb}{lb}/u{rb}\n')
        report.write(f"{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {zip_name}\n")
        report.write(f"{lb}b{rb}TIMESTAMP{lb}/b{rb}:    {now.strftime('%Y-%m-%d %I:%M:%S %p')}\n\n")
        report.write("Welcome and thank you for your contribution.\n" "
        report.write("Please review the add-on upload rules and best practices, and ensure all of your uploads follow them:\n")
        report.write(f"{lb}url{rb}https://esoui.com{lb}/url{rb}\n\n")
        report.write("Most important: Check the AI disclosure and credits parts, and use/apply them (where applicable)!\n")
        report.write("Thank you very much for supporting our addon quality and compatibility efforts, acting fair and with respect.\n\n")
        
        _check_zip_structure(zip_path, report)

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
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if lower_file.endswith(('.txt', '.addon')):
                        if not re.search(r'^\s*##\s*Title\s*:', content, flags=re.MULTILINE | re.IGNORECASE):
                            continue
                    print(f"\n  {C.BOLD}[FILE]{C.RESET} {rel_path}")
                    result = analyze_file_content(rel_path, content, current_extract_dir, addon_ctx)
                    if result.startswith("[STATUS] FAIL") or result.startswith("[STATUS] PASS"):
                        is_fail = result.startswith("[STATUS] FAIL")
                        status_tag = f"{C.RED}[FAIL]{C.RESET}" if is_fail else f"{C.GREEN}[PASS]{C.RESET}"
                        if not lower_file.endswith('.lua'):
                            file_label = "XML" if lower_file.endswith('.xml') else "Manifest"
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
                        report.write("--- [File: " + rel_path + "] ---\n" + result + "\n\n--------------------------------------------------\n\n")
                    else:
                        if lower_file.endswith('.xml'):
                            print(f"    └── {C.BLUE}[QUEUE FOR AI]{C.RESET} {C.CYAN}XSD valid, queued for semantic XML review.{C.RESET}")
                        if not ai_preflight_triggered:
                            ai_preflight_triggered = True
                            _ensure_ollama_and_model_ready(MODEL_NAME)
                        clean_lines_for_ai = [line for line in content.splitlines() if line.strip() and not line.strip().startswith("--")]
                        addon_code_bundle.append("### START_FILE: " + rel_path + "\n\n[SOURCE_CODE]\n" + "\n".join(clean_lines_for_ai) + "\n### END_FILE: " + rel_path + "\n")
                except Exception as e:
                    print(f"    └── {C.RED}[ERROR]{C.RESET} {str(e)}")
                    report.write("--- [File: " + rel_path + "] ---\n[STATUS] ERROR\n[CRITICAL VIOLATIONS] Read Error: " + str(e) + "\n\n")
        except Exception as e:
            print(f"  {C.RED}[ERROR] Failed to extract ZIP: {str(e)}{C.RESET}")
            report.write("Failed to extract ZIP: " + str(e) + "\n\n")

        print("")
        _run_ai_code_review(addon_code_bundle, report)
        report.write("=== END OF REPORT ===\n")

    _apply_bbcode_report_styling(current_report_file)

    if os.path.exists(EXTRACT_FOLDER):
        shutil.rmtree(EXTRACT_FOLDER)
    addon_duration = (datetime.now() - addon_start_time).total_seconds()
    print(f"\n{C.CYAN}[4/4] Report saved to:{C.RESET} {make_clickable_file_link(current_report_file)}")
    print(f"{C.CYAN}{C.BOLD}  ADDON END:   {C.WHITE}{zip_name}{C.CYAN} ({C.MAGENTA}{addon_duration:.2f}s{C.CYAN}){C.RESET}")
    print(f"{C.CYAN}{C.BOLD}=================================================================={C.RESET}\n")
