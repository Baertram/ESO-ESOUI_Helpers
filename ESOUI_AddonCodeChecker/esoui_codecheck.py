# 20261106 Created by Baertram, esoui.com - With assistance from AI
"""
Local AI ESOUI Addon Code Checker (esoui_codecheck.py)
------------------------------------------------------
CLI entry point and batch coordinator for static ESO addon checks and Ollama AI reviews.
"""

import json
import os
import re
from datetime import datetime


from src.esoui_config import (
    BASE_FOLDER,
    C,
    CMD_HISTORY_FILE,
    DEBUG_MODE,
    ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX,
    ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX,
    ESOUI_LATEST_MAX_ITEMS,
    ZIP_FOLDER,
)
from src.esoui_download_io import (
    download_zip,
    handle_clear_command,
    handle_input,
    is_authorized_esoui_url,
    parse_dl_command,
    parse_last_selection_spec,
    read_cli_input_with_esc,
)
from src.esoui_ai_and_report import (
    handle_search_command,
    is_bp_multi_globals_enabled,
    print_addon_metadata,
    print_multi_addon_summary,
    process_addon,
    process_latest_filelist_in_chunks,
    toggle_bp_multi_globals,
)

def _load_cmd_history(history_path=CMD_HISTORY_FILE):
    """Loads persisted repeat command history ('last_any', 'last_dl', 'last_search') from disk."""
    default_state = {"last_any": None, "last_dl": None, "last_search": None}
    if not os.path.isfile(history_path):
        return default_state
    try:
        with open(history_path, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            for key in default_state:
                val = loaded.get(key)
                if isinstance(val, str) and val.strip():
                    default_state[key] = val.strip()
    except (OSError, json.JSONDecodeError):
        pass
    return default_state


def _save_cmd_history(history_state, history_path=CMD_HISTORY_FILE):
    """Persists repeat command history atomically to Cache/cmd_history.json."""
    try:
        parent = os.path.dirname(history_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        tmp_path = history_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as fh:
            json.dump(history_state, fh, indent=2, ensure_ascii=False)
        os.replace(tmp_path, history_path)
    except OSError:
        pass


def _resolve_repeat_command(clean_cmd, history_state):
    """
    Resolves 'repeat', 'repeat dl', or 'repeat search' against stored CLI command history.
    Returns (resolved_command_or_None, error_message_or_None).
    """
    low = clean_cmd.strip().lower()
    if low == "repeat":
        last_any = history_state.get("last_any")
        if not last_any:
            return None, "Nothing to repeat yet (no previous check command executed)."
        return last_any, None
    if low == "repeat dl":
        last_dl = history_state.get("last_dl")
        if not last_dl:
            return None, "No previous 'dl' command to repeat."
        return last_dl, None
    if low == "repeat search":
        last_search = history_state.get("last_search")
        if not last_search:
            return None, "No previous 'search' command to repeat."
        return last_search, None
    return None, f"Invalid 'repeat' syntax '{clean_cmd}'. Supported: 'repeat', 'repeat dl', 'repeat search'."


def main_cli():
    """
    Runs the interactive CLI loop for ZIP archives, ESOUI URLs, TXT batch lists,
    'dl', 'last', 'search', 'repeat', 'bpglobal', and 'clear' commands.
    """

    print("==================================================================")
    print("               LOCAL AI ESOUI ADDON CHECKER READY                 ")
    if DEBUG_MODE:
        print(f"                  {C.YELLOW}[DEBUG MODE ENABLED (--debug)]{C.RESET}                  ")
    print("==================================================================")
    print(f"{C.CYAN}Supported inputs (prefix with '{C.WHITE}force {C.CYAN}' to bypass filelist & ZIP cache):{C.RESET}")
    print(f"  - {C.WHITE}ESOUI URL{C.RESET}       : [force] {ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}<addonId> (or {ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}<addonId>/)")
    print(f"  - {C.WHITE}Direct ID{C.RESET}       : [force] dl <addonId>  (e.g. dl 5026, force dl 5026)")
    print(f"  - {C.WHITE}Latest Addons{C.RESET}   : [force] last <1..{ESOUI_LATEST_MAX_ITEMS}> (e.g. last 2-5, force last 1, 3, 7)")
    print(f"  - {C.WHITE}Search Addons{C.RESET}   : [force] search <q1, q2> | search dep <d1, d2> | search author <a1, a2> | search api <v1, !v2>")
    print(f"  - {C.WHITE}Repeat Last{C.RESET}     : [force] repeat | repeat dl | repeat search")
    bp_state_lbl = f"{C.GREEN}ON{C.RESET}" if is_bp_multi_globals_enabled() else f"{C.YELLOW}OFF{C.RESET}"
    print(f"  - {C.WHITE}List multiple used globals{C.RESET}: bpglobal (toggle report section, default: {bp_state_lbl})")
    print(f"  - {C.WHITE}Cleanup{C.RESET}         : clear cache | clear cache addons | clear zips [YYMMDD] | clear reports [YYMMDD]")
    print(f"  - {C.WHITE}Local File / TXT{C.RESET}: Drag & drop a .zip archive or a .txt batch list\n")
    os.makedirs(BASE_FOLDER, exist_ok=True)

    # Load persisted 'repeat' command targets across terminal sessions
    cmd_history = _load_cmd_history()


    while True:
        raw = read_cli_input_with_esc(
            f"Input ([force] URL, 'dl <id>', 'last <1..{ESOUI_LATEST_MAX_ITEMS}>', 'search ...', 'repeat ...', 'bpglobal', 'clear ...', .zip/.txt, or ESC/'exit'): "
        ).strip()
        if raw == "__ESC__" or raw.lower() == "exit":
            print("Exiting. Have a great day!")
            break
        if not raw:
            continue

        clean = raw.strip('"').strip("'").strip()

        # 'clear' and 'bpglobal' are session utilities and never overwrite repeat history
        if re.match(r'^clear(?:\s+.*)?$', clean, flags=re.IGNORECASE) and not os.path.exists(clean):
            handle_clear_command(clean[5:].strip())
            continue

        if clean.lower() == "bpglobal" and not os.path.exists(clean):
            new_state = toggle_bp_multi_globals()
            state_txt = f"{C.GREEN}ON{C.RESET}" if new_state else f"{C.YELLOW}OFF{C.RESET}"
            print(f"{C.CYAN}-> Best practice section 'Global variable used multiple times w/o a local reference' is now:{C.RESET} {state_txt}\n")
            continue

        force_flag = False
        if re.match(r'^force(?:\s+|$)', clean, flags=re.IGNORECASE):
            force_flag = True
            clean = clean[5:].strip().strip('"').strip("'").strip()
            if not clean:
                print(f"{C.RED}-> Error: Missing target after 'force' (e.g. 'force dl 5026' or 'force last 1-5').{C.RESET}")
                continue

        # Resolve 'repeat', 'repeat dl', or 'repeat search' to its stored command string
        if re.match(r'^repeat(?:\s+.*)?$', clean, flags=re.IGNORECASE) and not os.path.exists(clean):
            repeated_cmd, rep_err = _resolve_repeat_command(clean, cmd_history)
            if rep_err:
                print(f"{C.RED}-> Error: {rep_err}{C.RESET}")
                continue
            clean = repeated_cmd
            if re.match(r'^force(?:\s+|$)', clean, flags=re.IGNORECASE):
                force_flag = True
                clean = clean[5:].strip().strip('"').strip("'").strip()
            display_rep = f"force {clean}" if force_flag else clean
            print(f"{C.CYAN}-> Repeating command:{C.RESET} {C.WHITE}{display_rep}{C.RESET}")

        executed_full_cmd = f"force {clean}" if force_flag else clean

        if re.match(r'^last(?:\s+.*)?$', clean, flags=re.IGNORECASE):
            spec_part = clean[4:].strip()
            selected_ranks, err_msg = parse_last_selection_spec(spec_part, ESOUI_LATEST_MAX_ITEMS)
            if err_msg:
                print(f"{C.RED}-> Error: {err_msg}{C.RESET}")
            else:
                cmd_history["last_any"] = executed_full_cmd
                _save_cmd_history(cmd_history)
                process_latest_filelist_in_chunks(selected_ranks, spec_part, force_download=force_flag)
            continue

        if re.match(r'^search(?:\s+.*)?$', clean, flags=re.IGNORECASE) and not os.path.exists(clean):
            cmd_history["last_search"] = executed_full_cmd
            cmd_history["last_any"] = executed_full_cmd
            _save_cmd_history(cmd_history)
            handle_search_command(clean[6:].strip(), force_download=force_flag)
            continue

        if re.match(r'^dl(?:\s*.*)?$', clean, flags=re.IGNORECASE) and not os.path.exists(clean):
            addon_ids = parse_dl_command(clean)
            if not addon_ids:
                print(f"{C.RED}-> Error: Invalid 'dl' syntax '{clean}'. Expected numeric addon ID(s), e.g. 'dl 5026' or 'dl 630, 3586'.{C.RESET}")
            else:
                cmd_history["last_dl"] = executed_full_cmd
                cmd_history["last_any"] = executed_full_cmd
                _save_cmd_history(cmd_history)
                dl_summaries = []
                for idx_dl, addon_id in enumerate(addon_ids, 1):
                    if len(addon_ids) > 1:
                        print(f"\n{C.CYAN}[DL {idx_dl}/{len(addon_ids)}]{C.RESET}")
                    print_addon_metadata(addon_id, force_refresh=force_flag)
                    dl_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"
                    print(f"{C.CYAN}-> Resolved 'dl {addon_id}' to direct download URL:{C.RESET} {C.WHITE}{dl_url}{C.RESET}")
                    zip_path, zip_name = download_zip(dl_url, ZIP_FOLDER, force_download=force_flag)
                    if zip_path and zip_name:
                        process_addon(zip_path, zip_name, known_addon_id=addon_id, summary_collector=dl_summaries)
                print_multi_addon_summary(dl_summaries)
            continue

        if os.path.exists(clean) and clean.lower().endswith(".txt"):
            cmd_history["last_any"] = executed_full_cmd
            _save_cmd_history(cmd_history)
            _run_txt_batch_file(clean)
        else:
            zip_path, zip_name = handle_input(clean, force_download=force_flag)
            if zip_path and zip_name:
                cmd_history["last_any"] = executed_full_cmd
                _save_cmd_history(cmd_history)
                process_addon(zip_path, zip_name)
    


def _run_txt_batch_file(txt_path):
    """Processes each command, ESOUI URL, or local ZIP path inside a .txt batch list sequentially."""
    print(f"\n=== Found TXT list: {os.path.basename(txt_path)} --- Starting batch processing... ===")
    t0 = datetime.now()
    filelist_last_used_in_batch = False
    skipped_count = 0
    batch_summaries = []
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith("#")]

    for idx, item in enumerate(lines, 1):
        print(f"\n[Batch Item {idx}/{len(lines)}] Checking: {item}")
        item_clean = item.strip()
        item_force = False
        if re.match(r'^force(?:\s+|$)', item_clean, flags=re.IGNORECASE):
            item_force = True
            item_clean = item_clean[5:].strip()
            if not item_clean:
                print(f"{C.RED}[CRITICAL ERROR] Batch stopped at item {idx}: Missing target after 'force'!{C.RESET}")
                break

        if re.match(r'^last(?:\s+.*)?$', item_clean, flags=re.IGNORECASE):
            if filelist_last_used_in_batch:
                print(f"{C.YELLOW}[SKIP] Duplicate '{item}' in TXT list (already executed once in this batch).{C.RESET}")
                skipped_count += 1
                continue
            spec_part = item_clean[4:].strip()
            selected_ranks, err_msg = parse_last_selection_spec(spec_part, ESOUI_LATEST_MAX_ITEMS)
            if err_msg:
                print(f"{C.RED}[CRITICAL ERROR] Batch stopped at item {idx}: {err_msg}{C.RESET}")
                break
            filelist_last_used_in_batch = True
            process_latest_filelist_in_chunks(selected_ranks, spec_part, force_download=item_force)
            continue

        if re.match(r'^search(?:\s+.*)?$', item_clean, flags=re.IGNORECASE) and not os.path.exists(item_clean):
            handle_search_command(item_clean[6:].strip(), force_download=item_force)
            continue

        if re.match(r'^dl(?:\s*.*)?$', item_clean, flags=re.IGNORECASE) and not os.path.exists(item_clean):
            addon_ids = parse_dl_command(item_clean)
            if not addon_ids:
                print(f"{C.RED}[CRITICAL ERROR] Batch stopped at item {idx}: Invalid 'dl' syntax '{item}' (expected e.g. 'dl 5026' or 'dl 630, 3586').{C.RESET}")
                break
            for addon_id in addon_ids:
                print_addon_metadata(addon_id, force_refresh=item_force)
                dl_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"
                print(f"{C.CYAN}-> Resolved 'dl {addon_id}' to direct download URL:{C.RESET} {C.WHITE}{dl_url}{C.RESET}")
                zip_path, zip_name = download_zip(dl_url, ZIP_FOLDER, force_download=item_force)
                if not zip_path or not zip_name:
                    print(f"{C.YELLOW}[SKIP] Batch item {idx}: Addon ID {addon_id} not found or no ZIP returned. Continuing with next item...{C.RESET}")
                    skipped_count += 1
                    continue
                process_addon(zip_path, zip_name, known_addon_id=addon_id, summary_collector=batch_summaries)
            continue

        if item_clean.lower().startswith(("http://", "https://")):
            if not is_authorized_esoui_url(item_clean):
                print(f"{C.RED}[CRITICAL ERROR] Batch stopped at item {idx}: Unauthorized URL rejected ({item_clean})!{C.RESET}")
                break
            url_id_m = re.search(r'(?:dl|info)(\d+)', item_clean, flags=re.IGNORECASE)
            url_addon_id = url_id_m.group(1) if url_id_m else None
            zip_path, zip_name = handle_input(item_clean, force_download=item_force)
            if not zip_path or not zip_name:
                print(f"{C.YELLOW}[SKIP] Batch item {idx}: ESOUI download URL returned no ZIP archive. Continuing with next item...{C.RESET}")
                skipped_count += 1
                continue
            process_addon(zip_path, zip_name, known_addon_id=url_addon_id, summary_collector=batch_summaries)
            continue

        zip_path, zip_name = handle_input(item_clean, force_download=item_force)
        if not zip_path or not zip_name:
            print(f"{C.RED}[CRITICAL ERROR] Batch stopped at item {idx} due to security/file error!{C.RESET}")
            break
        process_addon(zip_path, zip_name, summary_collector=batch_summaries)

    print_multi_addon_summary(batch_summaries)
    skip_note = f" ({skipped_count} skipped)" if skipped_count else ""
    print(f"=== Batch finished{skip_note} in {C.MAGENTA}{(datetime.now() - t0).total_seconds():.2f} seconds{C.RESET}. ===\n")


if __name__ == "__main__":
    main_cli()
