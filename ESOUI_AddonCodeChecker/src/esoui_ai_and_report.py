"""
ZIP-Strukturprüfung, MMOUI-Filelist-Orchestrierung, Ollama-AI-Review und kompaktes BBCode-Reporting.
"""

import concurrent.futures
import os
import re
import shutil
import struct
import subprocess
import sys
import time
import zipfile

if os.name == "nt":
    import msvcrt
else:
    import select

from collections import defaultdict
from datetime import datetime

from ollama import Client

from src.esoui_config import (
    AI_NUM_CTX,
    AI_TIMEOUT_SECONDS,
    ALLOWED_DOC_EXTENSIONS,
    ALLOWED_DOC_STEMS,
    ALLOWED_EXTENSIONS,
    ALLOWED_LANGUAGE_PATCH_ROOT_PREFIXES,
    BLOCKED_EXECUTABLE_EXTENSIONS,
    C,
    DEBUG_MODE,
    ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX,
    ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX,
    ESOUI_BATCH_CHUNK_SIZE,
    ESOUI_COMMENT_MAX_CHARS,
    ESOUI_LATEST_MAX_ITEMS,
    ESOUI_UPLOAD_RULES_URL,
    EXTRACT_FOLDER,
    FORBIDDEN_KEYWORDS,
    FORBIDDEN_OS_JUNK_NAMES,
    MODEL_NAME,
    OLLAMA_HOST,
    REPORTS_BASE_DIR,
    ZIP_FOLDER,
    format_report_display_link,
    format_zip_display_link,
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
    get_wiki_lgb_fetch_error,
)

from src.esoui_manifest_xml_analyzer import analyze_file_content
from src.esoui_ram_index import build_esoui_index_once, get_current_api_version, is_index_built

try:
    from add_input.esoui_rules_bestpractice import CUSTOM_RULES
except ImportError:
    try:
        from esoui_rules_bestpractice import CUSTOM_RULES
    except ImportError:
        CUSTOM_RULES = ""

# Ollama client instance, session preflight status cache, and CLI toggle for repeated globals report
client = Client(host=OLLAMA_HOST)
OLLAMA_PREFLIGHT_CACHE = None
SHOW_BP_MULTI_GLOBALS = False


def is_bp_multi_globals_enabled():
    """Returns whether the 'Global variable used multiple times w/o a local reference' report section is enabled."""
    return bool(SHOW_BP_MULTI_GLOBALS)


def toggle_bp_multi_globals():
    """Toggles SHOW_BP_MULTI_GLOBALS for the current CLI session and returns the new boolean state."""
    global SHOW_BP_MULTI_GLOBALS
    SHOW_BP_MULTI_GLOBALS = not SHOW_BP_MULTI_GLOBALS
    return SHOW_BP_MULTI_GLOBALS
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
    """Returns the primary API version string for a filelist entry (or '?' if missing)."""
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

    checked_summaries = []
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
                downloaded_batch.append((zip_path, zip_name, addon_id, title_text, version_text))
            else:
                print(f"{C.RED}  -> Skipping #{rank} (ID: {addon_id}) due to download failure.{C.RESET}")
            time.sleep(0.5)

        print(f"\n{C.CYAN}{C.BOLD}>>> CHUNK {chunk_num}/{total_chunks}: Checking {len(downloaded_batch)} downloaded addon(s)... <<<{C.RESET}")
        for zip_path, zip_name, known_id, known_title, known_ver in downloaded_batch:
            process_addon(
                zip_path,
                zip_name,
                known_addon_id=known_id,
                known_addon_title=known_title,
                known_addon_version=known_ver,
                summary_collector=checked_summaries,
            )

    print_multi_addon_summary(checked_summaries)
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

    while True:
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
            print(f"{C.RED}-> Error: {err_msg}{C.RESET}")
            if auto_select_spec is not None:
                return
            continue
        break

    selected_entries = [(rank, hits[rank - 1]) for rank in selected_ranks]
    _process_addon_entries_in_chunks(
        selected_entries,
        mode_label=f"search {mode_prefix}{query_part} [{sel_input}]",
        force_download=force_download,
    )


def _build_bbcode_zip_list(namelist, flagged_paths, manifest_paths=None, errors_only=False):
    """Builds a nested vBulletin [SIZE="2"][list]...[/list][/SIZE] tree marking flagged items with :mad: and manifests with [MANIFEST]."""
    lb, rb = chr(91), chr(93)
    tree = {}
    flagged_norm = {p.replace("\\", "/").rstrip("/") for p in flagged_paths}
    manifest_norm = {p.replace("\\", "/").rstrip("/") for p in (manifest_paths or set())}
    omitted_clean_files = 0

    for entry in namelist:
        norm = entry.replace("\\", "/").strip("/")
        if not norm:
            continue
        is_entry_file = not entry.endswith("/")
        if errors_only and is_entry_file:
            is_flagged_entry = (norm in flagged_norm) or any(norm.startswith(fp + "/") for fp in flagged_norm)
            if not is_flagged_entry and norm not in manifest_norm:
                omitted_clean_files += 1
                continue
        parts = norm.split("/")
        node = tree
        for idx, part in enumerate(parts):
            is_leaf_file = (idx == len(parts) - 1) and is_entry_file
            if part not in node:
                node[part] = None if is_leaf_file else {}
            elif node[part] is None and not is_leaf_file:
                node[part] = {}
            if not is_leaf_file:
                node = node[part]
    def _prune_empty_dirs(sub_tree):
        for k in list(sub_tree.keys()):
            if isinstance(sub_tree[k], dict):
                _prune_empty_dirs(sub_tree[k])
                if not sub_tree[k]:
                    del sub_tree[k]

    if errors_only:
        _prune_empty_dirs(tree)

    out_lines = [f'{lb}SIZE="2"{rb}{lb}list{rb}']
    mad_smilies_used = [0]
    max_tree_mad_smilies = 49

    def _walk(sub_tree, parent_path=""):
        items = sorted(sub_tree.items(), key=lambda kv: (kv[-1] is None, next(iter(kv)).lower()))
        dds_shown = 0
        dds_truncated = False
        for name, child in items:
            curr_path = f"{parent_path}/{name}" if parent_path else name
            is_bad = (curr_path in flagged_norm) or any(
                curr_path.startswith(fp + "/") for fp in flagged_norm
            )
            if child is None and name.lower().endswith(".dds") and not is_bad:
                dds_shown += 1
                if dds_shown > 1:
                    if not dds_truncated:
                        out_lines.append(f"{lb}*{rb} ...")
                        dds_truncated = True
                    continue

            display_name = f"{name}/" if child is not None else name
            if child is None and curr_path in manifest_norm:
                display_name = f"{display_name} {lb}MANIFEST{rb}"
            if is_bad:
                if mad_smilies_used.__getitem__(0) < max_tree_mad_smilies:
                    mad_smilies_used[0] = mad_smilies_used.__getitem__(0) + 1
                    bad_marker = ":mad:"
                else:
                    bad_marker = f"{lb}!{rb}"
                out_lines.append(f'{lb}*{rb} {lb}color="Red"{rb}{bad_marker} {display_name}{lb}/color{rb}')
            else:
                out_lines.append(f"{lb}*{rb} {display_name}")
            if child is not None:
                out_lines.append(f"{lb}list{rb}")
                _walk(child, curr_path)
                out_lines.append(f"{lb}/list{rb}")
    _walk(tree)
    if omitted_clean_files > 0:
        out_lines.append(f"{lb}*{rb} [i]... ({omitted_clean_files} clean files without critical errors omitted)[/i]")
    out_lines.append(f"{lb}/list{rb}{lb}/SIZE{rb}")
    return "\n".join(out_lines)


def _inspect_dds_header(header_bytes):
    """
    Inspects the first 128..148 bytes of a DDS file.
    Returns (is_valid_dds, width, height, compression_label, is_recommended_dxt3_or_dxt5).
    """
    if not header_bytes or len(header_bytes) < 128:
        return False, 0, 0, "Invalid/Truncated", False
    magic, dw_size, _flags, height, width = struct.unpack("<4sIIII", header_bytes[:20])
    if magic != b"DDS " or dw_size != 124 or width <= 0 or height <= 0:
        return False, 0, 0, "Invalid/Truncated", False

    pf_size, pf_flags, four_cc = struct.unpack("<II4s", header_bytes[76:88])
    if pf_size != 32:
        return False, width, height, "Invalid PixelFormat", False

    has_fourcc = bool(pf_flags & 0x4)
    if has_fourcc:
        if four_cc == b"DXT5":
            return True, width, height, "DXT5", True
        if four_cc == b"DXT3":
            return True, width, height, "DXT3", True
        if four_cc == b"DXT1":
            return True, width, height, "DXT1", False
        if four_cc == b"DX10":
            if len(header_bytes) >= 132:
                dxgi_fmt = struct.unpack("<I", header_bytes[128:132]).__getitem__(0)
                if dxgi_fmt in (77, 78):
                    return True, width, height, "DXT5 (BC3/DX10)", True
                if dxgi_fmt in (74, 75):
                    return True, width, height, "DXT3 (BC2/DX10)", True
                if dxgi_fmt in (71, 72):
                    return True, width, height, "DXT1 (BC1/DX10)", False
                if dxgi_fmt in (98, 99):
                    return True, width, height, "BC7 (DX10)", False
                return True, width, height, f"DX10 (format {dxgi_fmt})", False
            return False, width, height, "Truncated DX10 Header", False
        clean_cc = "".join(chr(b) if 32 <= b < 127 else "?" for b in four_cc).strip() or "Unknown FourCC"
        return True, width, height, clean_cc, False

    return True, width, height, "Uncompressed RGBA/RGB", False


def _check_zip_structure(zip_path, report_data):
    """Inspects all ZIP archive entries and populates report_data['zip_tree_bbcode'] & violations."""
    forbidden_entries = []
    disallowed_by_ext = defaultdict(list)
    dds_textures = []
    dds_invalid_entries = []
    dds_non_recommended_comp = []
    legacy_font_files = []
    non_addon_files = []
    unreferenced_txt_files = []
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

                is_doc_or_license = (base_stem in ALLOWED_DOC_STEMS) or (entry_ext in ALLOWED_DOC_EXTENSIONS)
                if entry_ext == '.dds':
                    try:
                        with zip_ref.open(entry) as dds_fp:
                            dds_hdr = dds_fp.read(148)
                    except Exception:
                        dds_hdr = b""
                    dds_ok, dds_w, dds_h, dds_fmt, dds_comp_ok = _inspect_dds_header(dds_hdr)
                    if not dds_ok:
                        dds_textures.append((normalized, f"invalid/truncated DDS header ({dds_fmt})", True, False))
                        dds_invalid_entries.append(f"{normalized} (invalid/truncated DDS header)")
                        flagged_paths.add(normalized)
                    elif (dds_w % 4 != 0) or (dds_h % 4 != 0):
                        dds_textures.append((normalized, f"{dds_w}x{dds_h}, {dds_fmt} - dds textures' height/width must be divisible by 4", True, False))
                        dds_invalid_entries.append(f"{normalized} ({dds_w}x{dds_h} - dds textures' height/width must be divisible by 4)")
                        flagged_paths.add(normalized)
                    elif not dds_comp_ok:
                        dds_textures.append((normalized, f"{dds_w}x{dds_h}, {dds_fmt} - Best practice: Use DXT5 or DXT3 compression", False, True))
                        dds_non_recommended_comp.append((dds_fmt, normalized, f"{dds_w}x{dds_h}"))
                    else:
                        dds_textures.append((normalized, f"{dds_w}x{dds_h}, {dds_fmt}", False, False))
                elif entry_ext == '.font':
                    legacy_font_files.append(normalized)
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
                        elif entry_ext == '.txt':
                            unreferenced_txt_files.append((f"{normalized} (missing '## Title:' / '## AddOnVersion:' manifest tag)", False))
                        else:
                            non_addon_files.append((f"{normalized} (missing '## Title:' / '## AddOnVersion:' manifest tag)", False))
                    except Exception:
                        non_addon_files.append((f"{normalized} (unreadable manifest)", False))

                if not is_doc_or_license and entry_ext not in ALLOWED_EXTENSIONS:
                    disallowed_by_ext[entry_ext].append(normalized)

            if not manifest_paths and unreferenced_txt_files:
                non_addon_files.extend(unreferenced_txt_files)

            if dds_textures:
                has_dds_crit = any(item.__getitem__(2) for item in dds_textures)
                has_dds_bp = any(item.__getitem__(3) for item in dds_textures)
                dds_hdr_col = C.RED if has_dds_crit else (C.YELLOW if has_dds_bp else C.CYAN)
                print(f"    ├── {dds_hdr_col}Textures (.dds) found ({len(dds_textures)}):{C.RESET}")
                for tex_path, tex_info, is_crit_dds, is_bp_dds in sorted(dds_textures, key=lambda x: x.__getitem__(0).lower()):
                    if is_crit_dds:
                        print(f"    │     {C.RED}- [CRITICAL] {tex_path} ({tex_info}){C.RESET}")
                    elif is_bp_dds:
                        print(f"    │     {C.YELLOW}- {tex_path} ({tex_info}){C.RESET}")
                    else:
                        print(f"    │     - {tex_path} ({tex_info})")
            else:
                print("    ├── Textures (.dds): None")

            if legacy_font_files:
                print(f"    ├── {C.YELLOW}Legacy font files (.font) found ({len(legacy_font_files)}) - Best practice: Migrate to slug file:{C.RESET}")
                for fnt in sorted(legacy_font_files):
                    print(f"    │     - {fnt} (Best practice: Migrate to slug file)")
                for fnt in sorted(legacy_font_files):
                    report_data["best_practices"]["Possible action: Please consider migrating the font files to slug files"].append((fnt, None, ""))

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

            top_level_dirs = set()
            has_lang_patch_files = False
            has_invalid_lang_patch_root = False
            for entry in all_entries:
                norm_e = entry.replace("\\", "/").strip("/")
                if not norm_e:
                    continue
                parts_e = norm_e.split("/")
                first_seg = parts_e.__getitem__(0)
                if first_seg.startswith(".") or first_seg.lower() in FORBIDDEN_OS_JUNK_NAMES:
                    continue
                norm_e_slash = norm_e + ("/" if entry.endswith("/") else "")
                low_e_slash = norm_e_slash.lower()
                is_lang_patch_entry = any(
                    low_e_slash.startswith(pfx) or pfx.startswith(low_e_slash)
                    for pfx in ALLOWED_LANGUAGE_PATCH_ROOT_PREFIXES
                )
                if is_lang_patch_entry:
                    if any(low_e_slash.startswith(pfx) for pfx in ALLOWED_LANGUAGE_PATCH_ROOT_PREFIXES):
                        has_lang_patch_files = True
                    continue
                if "/esoui/lang/" in f"/{low_e_slash}" or "/gamedata/lang/" in f"/{low_e_slash}":
                    has_invalid_lang_patch_root = True
                if len(parts_e) > 1 or entry.endswith("/"):
                    top_level_dirs.add(first_seg)

            zip_manifest_folder_errors = []
            has_wrong_addon_zip = has_invalid_lang_patch_root
            has_multiple_top_dirs = len(top_level_dirs) > 1

            if has_lang_patch_files and not top_level_dirs:
                pass
            elif not top_level_dirs:
                has_wrong_addon_zip = True
            elif manifest_paths:
                for m_path in sorted(manifest_paths):
                    m_parts = m_path.replace("\\", "/").split("/")
                    m_stem, _ = os.path.splitext(m_parts[-1])
                    if len(m_parts) < 2 or m_parts[-2] != m_stem:
                        has_wrong_addon_zip = True
                        break
            else:
                has_wrong_addon_zip = True

            if has_wrong_addon_zip:
                zip_manifest_folder_errors.append(
                    ("Wrong addon zip", "Foldername must match manifest (case-sensitive)")
                )
            if has_multiple_top_dirs:
                zip_manifest_folder_errors.append(
                    ("Check addon zip", "Contains multiple folders: DO NOT OVERWRITE OTHER ADDONS FROM WITHIN YOUR ADDON!")
                )

            report_data["zip_manifest_folder_errors"] = zip_manifest_folder_errors
            report_data["zip_all_entries"] = list(all_entries)
            report_data["zip_flagged_paths"] = set(flagged_paths)
            report_data["zip_manifest_paths"] = set(manifest_paths)
            report_data["zip_tree_bbcode"] = _build_bbcode_zip_list(all_entries, flagged_paths, manifest_paths)

            if forbidden_entries:
                report_data["zip_violations"].append("Hidden, OS-metadata, or development folders/files found")
            for dds_err in dds_invalid_entries:
                report_data["zip_violations"].append(f"Invalid .dds texture: {dds_err}")
            if dds_non_recommended_comp:
                grouped_dds = report_data.setdefault("dds_compression_grouped", defaultdict(list))
                for dds_fmt_lbl, dds_fp, dds_dims in dds_non_recommended_comp:
                    grouped_dds[dds_fmt_lbl].append((dds_fp, dds_dims))
            for ext, files in disallowed_by_ext.items():
                report_data["zip_violations"].append(f"Disallowed file extension '{ext}' found ({len(files)} file(s))")
            for nf, is_crit in non_addon_files:
                if not is_crit:
                    report_data["best_practices"]["Possible action: Non-addon-relevant file"].append((nf, None, ""))
    except Exception as e:
        print(f"    └── {C.RED}[ERROR] Failed to read ZIP structure: {str(e)}{C.RESET}")
        report_data["zip_violations"].append(f"Failed to read ZIP structure: {str(e)}")


def _ensure_ollama_and_model_ready(model_name):
    """Checks if Ollama is installed, starts the server if inactive, and verifies the local model."""
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


def _poll_escape_key_pressed():
    """Returns True if ESC was pressed in the terminal without blocking."""
    try:
        if os.name == "nt":
            while msvcrt.kbhit():
                ch = msvcrt.getwch()
                if ch in ("\x00", "\xe0"):
                    if msvcrt.kbhit():
                        msvcrt.getwch()
                    continue
                if ch == "\x1b":
                    return True
            return False
        if sys.stdin and sys.stdin.isatty():
            ready, _, _ = select.select([sys.stdin], [], [], 0)
            if ready:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    return True
    except Exception:
        pass
    return False


def _run_ai_code_review(addon_code_bundle):
    """Reviews queued files sequentially with Ollama and returns parsed AI findings [(rel_path, ai_response)]."""
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
            body_part = file_block.split(marker, 1).__getitem__(1)
            if end_marker in body_part:
                body_part = body_part.split(end_marker, 1).__getitem__(0)
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
    print(
        f"\n  {C.BLUE}{C.BOLD}[AI REVIEW] Reviewing {total_items} item(s) with Ollama ({MODEL_NAME}) "
        f"{C.CYAN}(Press ESC anytime to abort AI review){C.BLUE}...{C.RESET}"
    )

    aborted_by_esc = False
    for idx, (orig_rel_path, display_label, part_code) in enumerate(expanded_work_items, 1):
        if aborted_by_esc or _poll_escape_key_pressed():
            print(f"  {C.YELLOW}⏹ AI review aborted by user (ESC). Finalizing report with static results...{C.RESET}")
            break

        print(f"  {C.CYAN}[AI {idx}/{total_items}]{C.RESET} Reviewing {C.BOLD}{display_label}{C.RESET}...")

        review_payload = f"### START_FILE: {display_label}\n\n[SOURCE_CODE]\n{part_code}\n### END_FILE: {display_label}\n"
        prompt = (
            f"You are a strict, silent code reviewer for Elder Scrolls Online addons.\n"
            f"Review the code section below (which may be a numbered part of a larger file) against these rules:\n{CUSTOM_RULES}\n"
            f"IMPORTANT: All .dds texture files (dimensions and compression) are already checked statically by the ZIP analyzer. "
            f"NEVER output any claims or rules about .dds texture dimensions, power-of-two, divisibility, or .dds compression.\n\n"
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
                if _poll_escape_key_pressed():
                    aborted_by_esc = True
                    future.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                if int(time.perf_counter() - start_wait) >= AI_TIMEOUT_SECONDS:
                    future.cancel()
                    executor.shutdown(wait=False, cancel_futures=True)
                    raise TimeoutError("AI review timed out")
                time.sleep(0.1)

            if aborted_by_esc:
                print(f"    └── {C.YELLOW}⏹ AI review aborted by user (ESC). Finalizing report with static results...{C.RESET}")
                break

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
        if s == "[REVIEW POTENTIAL AI CODE]":
            section = "ai_slop"
            continue
        if s.startswith("[STATUS]") or s == "None" or not s:
            continue

        if section == "crit" and s.startswith("- "):
            item_text = s[2:].strip()
            ev_filter_m = re.match(
                r'^(Use event filters for [^:]+):\s*(EVENT_[A-Z0-9_]+)\s*\(line\s+(\d+)\)\s*\((.+)\)\s*$',
                item_text,
            )
            if ev_filter_m:
                rule_title = ev_filter_m.group(1).strip()
                ev_name = ev_filter_m.group(2).strip()
                line_no = ev_filter_m.group(3).strip()
                snippet_txt = ev_filter_m.group(4).strip()
                report_data["critical"][category][rule_title].append(
                    (f"EVENT_FILTER::{ev_name}::{rel_norm}", line_no, snippet_txt)
                )
                continue

            lgb_m = re.match(
                r"^LibGroupBroadcast (?:Protocoll/Event|Protocoll \[\d+\]|Event \[\d+\]) conflict\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if lgb_m:
                line_no = int(lgb_m.group(1))
                desc_txt = lgb_m.group(2).strip()
                report_data.setdefault("lgb_conflicts", []).append((rel_norm, line_no, desc_txt))
                continue

            pollution_m = re.match(
                r"^Global Variable Pollution\s*\(missing 'local' for '([^']+)'\)\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if pollution_m:
                var_name = pollution_m.group(1).strip()
                line_no = int(pollution_m.group(2))
                raw_code = pollution_m.group(3).strip()
                code_comment = re.sub(r'^--\s*', '', raw_code)
                report_data.setdefault("global_var_pollution", []).append(
                    (rel_norm, line_no, var_name, code_comment)
                )
                continue

            xsd_m = re.match(r'^XSD Validation Error\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$', item_text)
            if xsd_m:
                report_data["critical"][category]["XSD Validation Error"].append(
                    (rel_norm, xsd_m.group(1).strip(), xsd_m.group(2).strip())
                )
                continue

            if item_text.startswith("Global Function Pollution (leaked into _G)"):
                ln_m = re.search(r'\b(?:at\s+)?line\s+(\d+)\b', item_text, flags=re.IGNORECASE)
                ln_val = int(ln_m.group(1)) if ln_m else 0
                c_m = re.search(r'\((--\s*.*)\)\s*\.?$', item_text)
                raw_c = c_m.group(1).strip() if c_m else ""
                code_snip = re.sub(r'^--\s*', '', raw_c)
                report_data.setdefault("global_func_pollution", []).append((rel_norm, ln_val, code_snip))
                continue
            sv_unique_m = re.match(
                r"^Non-unique / too short SavedVariables \(use e\.g\. <AddonName>_SV\):\s*([^(]+?)\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if sv_unique_m:
                bad_vars_str = ", ".join(v.strip() for v in sv_unique_m.group(1).split(",") if v.strip())
                line_no = sv_unique_m.group(2).strip()
                rule_hdr = "Non-unique / too short SavedVariables (use e.g. <AddonName>_SV)"
                report_data["critical"][category][rule_hdr].append((rel_norm, line_no, bad_vars_str))
                continue

            non_unique_g_m = re.match(
                r"^Non-unique / too short global variable '([^']+)'\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if non_unique_g_m:
                var_name = non_unique_g_m.group(1).strip()
                line_no = int(non_unique_g_m.group(2))
                report_data.setdefault("non_unique_globals", []).append((rel_norm, line_no, var_name))
                continue

            addon_loaded_unreg_m = re.match(
                r"^(Unregister EVENT_ADD_ON_LOADED (?:is missing|does not match your register name))\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if addon_loaded_unreg_m:
                rule_hdr = addon_loaded_unreg_m.group(1).strip()
                pairs_txt = addon_loaded_unreg_m.group(3).strip()
                report_data["critical"][category][rule_hdr].append((rel_norm, "", pairs_txt))
                continue

            inv_ctx_hook_m = re.match(
                r"^Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if inv_ctx_hook_m:
                line_no = inv_ctx_hook_m.group(1).strip()
                raw_c = inv_ctx_hook_m.group(2).strip()
                code_snip = re.sub(r"^--\s*", "", raw_c)
                rule_hdr = "Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu"
                report_data["critical"][category][rule_hdr].append((rel_norm, line_no, code_snip))
                continue

            if item_text.startswith("Multiple Global Addon Tables:"):
                m_multi = re.search(r'\(([^()]+)\)\s*$', item_text)
                tbl_detail = m_multi.group(1).strip() if m_multi else ""
                report_data["critical"][category]["Multiple Global Addon Tables"].append((rel_norm, None, tbl_detail))
                continue

            dep_missing_m = re.match(
                r"^(Mandatory version check >= missing for non-optional dependency)\s*\(line\s+(\d+)\)\s*:\s*\((.+)\)\s*$",
                item_text,
            )
            if dep_missing_m:
                report_data["critical"][category][dep_missing_m.group(1).strip()].append(
                    (rel_norm, dep_missing_m.group(2).strip(), dep_missing_m.group(3).strip())
                )
                continue

            line_match = re.search(r'\b(?:at\s+)?line\s+(\d+)\b', item_text, flags=re.IGNORECASE)
            line_no = line_match.group(1) if line_match else None
            rule_title = re.sub(r'\s*\((?:at\s+)?line\s+\d+\)|\s+at\s+line\s+\d+', '', item_text, flags=re.IGNORECASE)
            code_match = re.search(r'\(((?:--|\#\#).*)\)\s*\.?$', rule_title)
            raw_code = code_match.group(1).strip() if code_match else ""
            code_comment = re.sub(r'^--\s*', '', raw_code)
            if code_match:
                rule_title = rule_title[:code_match.start()].strip().rstrip(":")
            else:
                rule_title = next(iter(rule_title.split(":", 1))).strip()
            report_data["critical"][category][rule_title].append((rel_norm, line_no, code_comment))

        elif section == "bp":
            if s.startswith("- "):
                bp_header = s[2:].strip()
                if bp_header.startswith("Hardcoded language files - Use dynamic $(language):"):
                    raw_files = bp_header.split(":", 1).__getitem__(1).strip()
                    for lf_item in raw_files.split(","):
                        clean_lf = lf_item.strip()
                        if clean_lf and clean_lf not in report_data.setdefault("hardcoded_lang_files", []):
                            report_data["hardcoded_lang_files"].append(clean_lf)
                    report_data["_last_bp_rule"] = None
                    continue
                m_missing_ref = re.match(
                    r"^Missing local reference to global addon table '([^']+)'\s*\(lines?\s+([0-9,\s]+)\)\s*$",
                    bp_header,
                )
                if m_missing_ref:
                    g_name = m_missing_ref.group(1).strip()
                    lines_str = ", ".join(tok.strip() for tok in m_missing_ref.group(2).split(",") if tok.strip())
                    report_data.setdefault("missing_local_addon_ref", defaultdict(list))[g_name].append((rel_norm, lines_str))
                    report_data["_last_bp_rule"] = None
                    continue
                if "without a local reference" in bp_header:
                    bp_rule = "Possible action: Global variable used multiple times without a local reference"
                elif "Startup Chat Spam" in bp_header:
                    bp_rule = "Possible action: Startup Chat Spam Detected (unconditional message on load/player activated)"
                elif "Manifest .addon found" in bp_header:
                    bp_rule = "Possible action: Console UI Manifest Notice (.addon used instead of .txt)"
                elif "Mandatory version check >= outdated - consider an update" in bp_header:
                    bp_rule = "Possible action: Mandatory version check >= outdated - consider an update"
                    ln_m = re.search(r'\bline\s+(\d+)\b', bp_header, flags=re.IGNORECASE)
                    c_m = re.search(r'\(([^()]+(?:\([^()]*\)[^()]*)*)\)\s*\.?$', bp_header)
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
        elif section == "ai_slop":
            if s.startswith("pcall usage:"):
                report_data["_last_slop_rule"] = "Possible action: Potential AI code - defensive pcall() usage (verify if needed)"
            elif s.startswith("Unnecessary 'exists' checks:"):
                report_data["_last_slop_rule"] = "Possible action: Potential AI code - unnecessary existence check on documented ESO global"
            elif s.startswith("- ") and report_data.get("_last_slop_rule"):
                slop_item = s[2:].strip()
                m_slop = re.match(r'^(\d+)(?:\s*\(([^)]+)\))?:\s*--\s*(.*)$', slop_item)
                if m_slop:
                    ln_no, ident_info, c_txt = m_slop.group(1), m_slop.group(2), m_slop.group(3).strip()
                    if report_data["_last_slop_rule"] == "Possible action: Potential AI code - defensive pcall() usage (verify if needed)":
                        report_data["best_practices"][report_data["_last_slop_rule"]].append((rel_norm, ln_no, c_txt))
                    else:
                        loc_label = f"{rel_norm}:{ln_no} ({ident_info})" if ident_info else f"{rel_norm}:{ln_no}"
                        report_data["best_practices"][report_data["_last_slop_rule"]].append((loc_label, None, c_txt))


def _harmonize_xsd_message(raw_msg):
    """Generically compresses and groups all repetitive libxml2 XSD error strings per XML element."""
    if not raw_msg:
        return ""
    parts = [p.strip() for p in raw_msg.split("|") if p.strip()]
    elem_buckets = defaultdict(lambda: defaultdict(list))
    elem_order = []
    unparsed = []

    rx_elem_attr = re.compile(r"^Element '([^']+)', attribute '([^']+)':\s*(.+)$")
    rx_elem_only = re.compile(r"^Element '([^']+)':\s*(.+)$")
    rx_unexpected_child = re.compile(
        r"^Element '([^']+)': This element is not expected\.(?:\s*Expected is (?:one of )?\(\s*(.+?)\s*\)\.)?$"
    )
    rx_missing_child = re.compile(
        r"^Missing child element\(s\)\.(?:\s*Expected is (?:one of )?\(\s*(.+?)\s*\)\.)?$"
    )
    rx_facet_enum = re.compile(
        r"^\[facet 'enumeration'\] The value '([^']+)' is not an element of the set \{(.+?)\}\.$"
    )
    rx_atomic_type = re.compile(
        r"^'([^']+)' is not a valid value of the atomic type '([^']+)'\.$"
    )

    def _register_elem(el):
        if el not in elem_order:
            elem_order.append(el)

    def _append_unique(lst, val):
        if val and val not in lst:
            lst.append(val)

    def _format_expected_list(raw_exp):
        tokens = [t.strip().strip("'\"") for t in re.split(r"[,|]", raw_exp or "") if t.strip()]
        return ", ".join(f"'{t}'" for t in dict.fromkeys(tokens))

    for part in parts:
        m_ea = rx_elem_attr.match(part)
        if m_ea:
            elem, attr, detail = m_ea.groups()
            _register_elem(elem)
            if detail == f"The attribute '{attr}' is not allowed.":
                _append_unique(elem_buckets[elem]["not_allowed"], attr)
            elif detail == f"The attribute '{attr}' is required but missing.":
                _append_unique(elem_buckets[elem]["missing_req"], attr)
            else:
                m_enum = rx_facet_enum.match(detail)
                m_atom = rx_atomic_type.match(detail)
                if m_enum:
                    bad_val, allowed_set = m_enum.groups()
                    allowed_fmt = _format_expected_list(allowed_set)
                    clean_det = f"attribute '{attr}': Invalid value '{bad_val}' (must be one of {allowed_fmt})."
                elif m_atom:
                    bad_val, type_name = m_atom.groups()
                    clean_det = f"attribute '{attr}': Invalid value '{bad_val}' (expected type '{type_name}')."
                else:
                    clean_det = f"attribute '{attr}': {detail}"
                _append_unique(elem_buckets[elem]["other"], clean_det)
            continue

        m_eo = rx_elem_only.match(part)
        if m_eo:
            elem, detail = m_eo.groups()
            _register_elem(elem)
            m_uc = rx_unexpected_child.match(detail)
            m_mc = rx_missing_child.match(detail)
            if m_uc:
                bad_child, exp_raw = m_uc.groups()
                _append_unique(elem_buckets[elem]["unexpected_children"], bad_child)
                if exp_raw:
                    elem_buckets[elem]["unexpected_expected"] = [_format_expected_list(exp_raw)]
            elif m_mc:
                exp_raw = m_mc.group(1)
                exp_fmt = _format_expected_list(exp_raw) if exp_raw else ""
                msg_mc = f"Missing child element(s) (expected {exp_fmt})." if exp_fmt else "Missing child element(s)."
                _append_unique(elem_buckets[elem]["other"], msg_mc)
            else:
                _append_unique(elem_buckets[elem]["other"], detail)
            continue

        _append_unique(unparsed, part)

    harmonized_parts = []
    for el in elem_order:
        b = elem_buckets[el]
        sub_msgs = []

        na = b.get("not_allowed", [])
        if len(na) == 1:
            sub_msgs.append(f"Attribute '{na.__getitem__(0)}' is not allowed.")
        elif len(na) > 1:
            sub_msgs.append(f"Attributes {', '.join(f'{chr(39)}{a}{chr(39)}' for a in na)} are not allowed.")

        mr = b.get("missing_req", [])
        if len(mr) == 1:
            sub_msgs.append(f"Required attribute '{mr.__getitem__(0)}' is missing.")
        elif len(mr) > 1:
            sub_msgs.append(f"Required attributes {', '.join(f'{chr(39)}{a}{chr(39)}' for a in mr)} are missing.")

        uc = b.get("unexpected_children", [])
        if uc:
            uc_joined = ", ".join(f"'{c}'" for c in uc)
            exp_list = b.get("unexpected_expected", [])
            exp_suffix = f" (expected {exp_list.__getitem__(0)})" if exp_list and exp_list.__getitem__(0) else ""
            sub_msgs.append(f"Unexpected child element(s) {uc_joined}{exp_suffix}.")

        for rest in b.get("other", []):
            sub_msgs.append(rest)

        harmonized_parts.append(f"Element '{el}': {' '.join(sub_msgs)}")

    harmonized_parts.extend(unparsed)
    return " | ".join(harmonized_parts)


def _strip_addon_root_prefix(path_str):
    """Strips the leading top-level addon folder and formats the relative path with leading '\\'."""
    if not path_str:
        return ""
    norm = str(path_str).replace("/", "\\").lstrip("\\")
    if "\\" in norm:
        _, sub_path = norm.split("\\", 1)
        return "\\" + sub_path
    return "\\" + norm


def _build_bbcode_report_text(zip_name, timestamp_str, report_data, compact_bp=0, errors_only_tree=False):
    """Builds the ESOUI BBCode report text with progressive compaction levels."""

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
        (
            f'{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {lb}color="Red"{rb}:mad: {zip_name}{lb}/color{rb}'
            if report_data.get("zip_manifest_folder_errors")
            else f"{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {zip_name}"
        ),
    ]

    if report_data.get("zip_all_entries"):
        tree_bb = _build_bbcode_zip_list(
            report_data["zip_all_entries"],
            report_data.get("zip_all_flagged", report_data.get("zip_flagged_paths", set())),
            report_data.get("zip_manifest_paths", set()),
            errors_only=errors_only_tree,
        )
        out.append(tree_bb)
    elif report_data.get("zip_tree_bbcode"):
        out.append(report_data["zip_tree_bbcode"])
    unverified_entries = report_data.get("unverified_globals") or []
    pollution_entries = report_data.get("global_var_pollution") or []
    func_pollution_entries = report_data.get("global_func_pollution") or []
    non_unique_global_entries = report_data.get("non_unique_globals") or []
    lgb_entries = report_data.get("lgb_conflicts") or []
    zip_mf_folder_errors = report_data.get("zip_manifest_folder_errors") or []
    has_crit = (
        bool(report_data["zip_violations"])
        or bool(zip_mf_folder_errors)
        or bool(pollution_entries)
        or bool(func_pollution_entries)
        or bool(non_unique_global_entries)
        or bool(lgb_entries)
        or any(bool(v) for v in report_data["critical"].values())
    )
    has_unverified = bool(unverified_entries)
    include_multi_globals = is_bp_multi_globals_enabled()
    missing_addon_refs = report_data.get("missing_local_addon_ref") or {}
    hardcoded_lang_files = report_data.get("hardcoded_lang_files") or []
    dds_comp_grouped = report_data.get("dds_compression_grouped") or {}
    has_bp = (
        bool(report_data["best_practices"])
        or bool(missing_addon_refs)
        or bool(hardcoded_lang_files)
        or bool(dds_comp_grouped)
        or (include_multi_globals and bool(report_data.get("bp_grouped_globals")))
    )
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
            rules_map = report_data["critical"].get(cat_key) or {}
            has_cat_pollution = (cat_key == "lua" and bool(pollution_entries))
            has_cat_func_pollution = (cat_key == "lua" and bool(func_pollution_entries))
            has_cat_non_unique_g = (cat_key == "lua" and bool(non_unique_global_entries))
            has_cat_lgb = (cat_key == "manifest" and bool(lgb_entries))
            has_cat_zip_mf = (cat_key == "manifest" and bool(zip_mf_folder_errors))
            if not rules_map and not has_cat_pollution and not has_cat_func_pollution and not has_cat_non_unique_g and not has_cat_lgb and not has_cat_zip_mf:
                continue
            out.append("")
            out.append(f'{lb}b{rb}{lb}FONT="Book Antiqua"{rb}{cat_label}{lb}/FONT{rb}{lb}/b{rb}')
            if has_cat_zip_mf:
                for z_title, z_desc in zip_mf_folder_errors:
                    out.append(f'{lb}color="red"{rb}{lb}b{rb}{lb}u{rb}{z_title}{lb}/u{rb}{lb}/b{rb}{lb}/color{rb}')
                    out.append(z_desc)
                    out.append("")

            if has_cat_pollution:
                out.append(f"{lb}u{rb}{lb}b{rb}Global Variable Pollution{lb}/b{rb}{lb}/u{rb}")
                if report_data.get("is_strict_local_addon"):
                    out.append("Missing local definition? Single-file addon without Bindings/XML/API calls: keep everything 'local'!")
                else:
                    out.append("Missing local definition? Else: Please define only 1 global table for your addon, and add all relevant functions/tables/controls/variables to it")
                by_file = defaultdict(list)
                for f_path, ln_no, var_name, code_txt in pollution_entries:
                    by_file[_strip_addon_root_prefix(f_path)].append((int(ln_no), var_name, code_txt))
                spoiler_lines = []
                for f_path in sorted(by_file.keys(), key=lambda x: x.lower()):
                    spoiler_lines.append(f"{lb}u{rb}{lb}b{rb}{f_path}{lb}/b{rb}{lb}/u{rb}")
                    for ln_no, var_name, code_txt in sorted(by_file[f_path], key=lambda item: item):
                        spoiler_lines.append(f"  {ln_no}: {var_name} ({code_txt})")
                spoiler_body = "\n".join(spoiler_lines)
                out.append(f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}')

            if has_cat_non_unique_g:
                out.append(f"{lb}u{rb}Non-unique / too short global variable{lb}/u{rb}")
                out.append(f"{lb}list{rb}")
                by_file_nu = defaultdict(lambda: defaultdict(list))
                for f_path, ln_no, var_name in non_unique_global_entries:
                    short_nu = _strip_addon_root_prefix(f_path)
                    if var_name not in by_file_nu[short_nu][int(ln_no)]:
                        by_file_nu[short_nu][int(ln_no)].append(var_name)
                spoiler_lines = []
                for f_path in sorted(by_file_nu.keys(), key=lambda x: x.lower()):
                    spoiler_lines.append(f"{lb}u{rb}{lb}b{rb}{f_path}{lb}/b{rb}{lb}/u{rb}")
                    for ln_no in sorted(by_file_nu[f_path].keys()):
                        vars_joined = ", ".join(by_file_nu[f_path][ln_no])
                        spoiler_lines.append(f"{ln_no}: {vars_joined}")
                spoiler_body = "\n".join(spoiler_lines)
                out.append(f'{lb}*{rb} {lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}')
                out.append(f"{lb}/list{rb}")
            if has_cat_func_pollution:
                out.append(f"{lb}u{rb}Global Function Pollution (leaked into _G): Keep local or attach to your single addon table{lb}/u{rb}")
                out.append(f"{lb}list{rb}")
                by_file_fn = defaultdict(list)
                for f_path, ln_no, code_txt in func_pollution_entries:
                    by_file_fn[_strip_addon_root_prefix(f_path)].append((int(ln_no), code_txt))
                for f_path in sorted(by_file_fn.keys(), key=lambda x: x.lower()):
                    fn_lines = []
                    for ln_no, code_txt in sorted(by_file_fn[f_path], key=lambda item: item):
                        prefix = f"{ln_no}: " if ln_no else ""
                        fn_lines.append(f"{prefix}{code_txt}".strip())
                    spoiler_body = "\n".join(fn_lines)
                    spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}' if spoiler_body else ""
                    out.append(f"{lb}*{rb} {f_path}{spoiler_part}")
                out.append(f"{lb}/list{rb}")

            for rule_title, entries in rules_map.items():
                out.append(f"{lb}u{rb}{rule_title}{lb}/u{rb}")
                out.append(f"{lb}list{rb}")
                if rule_title == "XSD Validation Error":
                    grouped_xsd_entries = defaultdict(list)
                    for f_path, ln_no, code_txt in entries:
                        clean_xsd = _harmonize_xsd_message(code_txt)
                        grouped_xsd_entries[(_strip_addon_root_prefix(f_path), clean_xsd)].append(ln_no)
                    for (f_path, clean_xsd), line_list in grouped_xsd_entries.items():
                        valid_lines = []
                        for ln in line_list:
                            if ln and ln not in valid_lines:
                                valid_lines.append(ln)
                        if len(valid_lines) > 1:
                            loc = f"{f_path} (lines {', '.join(valid_lines)})"
                        elif len(valid_lines) == 1:
                            loc = f"{f_path}:{valid_lines.__getitem__(0)}"
                        else:
                            loc = f_path
                        spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{clean_xsd}{lb}/SIZE{rb}{lb}/spoiler{rb}' if clean_xsd else ""
                        out.append(f"{lb}*{rb} {loc}{spoiler_part}")
                else:
                    grouped_ev_filters = defaultdict(list)
                    ev_order = []
                    regular_entries = []
                    for f_path, ln_no, code_txt in entries:
                        if f_path.startswith("EVENT_FILTER::"):
                            _, ev_name, real_file = f_path.split("::", 2)
                            short_real = _strip_addon_root_prefix(real_file)
                            key = (ev_name, short_real)
                            if key not in grouped_ev_filters:
                                ev_order.append(key)
                            grouped_ev_filters[key].append((ln_no, code_txt))
                        else:
                            regular_entries.append((f_path, ln_no, code_txt))

                    for ev_name, short_real in ev_order:
                        ev_hits = grouped_ev_filters[(ev_name, short_real)]
                        by_line = defaultdict(list)
                        line_order = []
                        for ln_no, code_txt in ev_hits:
                            if ln_no not in by_line:
                                line_order.append(ln_no)
                            if " -- " in code_txt:
                                code_part, reason_part = code_txt.split(" -- ", 1)
                            else:
                                code_part, reason_part = code_txt, ""
                            by_line[ln_no].append((code_part.strip(), reason_part.strip()))

                        spoiler_sections = []
                        for ln_no in line_order:
                            header_loc = f"{short_real}:{ln_no}" if ln_no else short_real
                            line_items = by_line[ln_no]
                            base_code = next((c for c, _ in line_items if c), "")
                            reasons = []
                            for _, r_txt in line_items:
                                if r_txt and r_txt not in reasons:
                                    reasons.append(r_txt)
                            sec_lines = [f"{lb}u{rb}{lb}b{rb}{header_loc}{lb}/b{rb}{lb}/u{rb}"]
                            if base_code:
                                sec_lines.append(base_code)
                            for r_txt in reasons:
                                sec_lines.append(f"- {r_txt}")
                            spoiler_sections.append("\n".join(sec_lines))

                        spoiler_body = "\n\n".join(spoiler_sections)
                        out.append(
                            f'{lb}*{rb} {lb}b{rb}{ev_name}{lb}/b{rb}\n'
                            f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                        )

                    if rule_title == "Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu":
                        by_file_ctx = defaultdict(list)
                        file_ctx_order = []
                        for f_path, ln_no, code_txt in regular_entries:
                            short_fp = _strip_addon_root_prefix(f_path)
                            if short_fp not in by_file_ctx:
                                file_ctx_order.append(short_fp)
                            entry_str = f"{ln_no}: {code_txt}".strip() if ln_no else code_txt
                            if entry_str and entry_str not in by_file_ctx[short_fp]:
                                by_file_ctx[short_fp].append(entry_str)
                        for short_fp in file_ctx_order:
                            spoiler_body = "\n".join(by_file_ctx[short_fp])
                            spoiler_part = (
                                f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                                if spoiler_body
                                else ""
                            )
                            out.append(f"{lb}*{rb} {short_fp}{spoiler_part}")
                    elif rule_title == "EVENT_ADD_ON_LOADED addonName not compared against addon folder name (case-sensitive)":
                        by_file_cmp = defaultdict(list)
                        file_cmp_order = []
                        for f_path, ln_no, _ in regular_entries:
                            short_fp = _strip_addon_root_prefix(f_path)
                            if short_fp not in by_file_cmp:
                                file_cmp_order.append(short_fp)
                            if ln_no and ln_no not in by_file_cmp[short_fp]:
                                by_file_cmp[short_fp].append(ln_no)
                        for short_fp in file_cmp_order:
                            lines_joined = ", ".join(by_file_cmp[short_fp])
                            spoiler_part = (
                                f' {lb}spoiler{rb}{lb}SIZE="2"{rb}Lines: {lines_joined}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                                if lines_joined
                                else ""
                            )
                            out.append(f"{lb}*{rb} {short_fp}{spoiler_part}")
                    else:
                        for f_path, ln_no, code_txt in regular_entries:
                            short_fp = _strip_addon_root_prefix(f_path)
                            loc = f"{short_fp}:{ln_no}" if ln_no else short_fp
                            spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                            out.append(f"{lb}*{rb} {loc}{spoiler_part}")
                out.append(f"{lb}/list{rb}")
            if has_cat_lgb:
                out.append(f"{lb}u{rb}LibGroupBroadcast Protocoll/Event conflict{lb}/u{rb}")
                lgb_err = get_wiki_lgb_fetch_error()
                if lgb_err:
                    out.append(f'{lb}color="Red"{rb}{lgb_err}{lb}/color{rb}')
                out.append(f"{lb}list{rb}")
                sorted_lgb = sorted(
                    lgb_entries,
                    key=lambda item: (0 if item[2].startswith("Protocol") else 1, item[0].lower(), item[1]),
                )
                for f_path, ln_no, desc_txt in sorted_lgb:
                    out.append(f"{lb}*{rb} {_strip_addon_root_prefix(f_path)}:{ln_no} - {desc_txt}")
                out.append(f"{lb}/list{rb}")
                out.append("Read the LibGroupBroadcast addon description and add your protocolls/events etc. properly to the ESOUI Wiki!")

    if has_unverified:
        out.append("")
        out.append(f'{lb}SIZE="4"{rb}{lb}b{rb}{lb}u{rb}{lb}color="DarkOrchid"{rb}{lb}FONT="Impact"{rb}Unverified Globals{lb}/FONT{rb}{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}{lb}/SIZE{rb}')
        out.append("")
        out.append(f"{lb}u{rb}Not found in ESO API Documentation / Custom-Stubs (please verify local/global scope){lb}/u{rb}")
        out.append(f"{lb}list{rb}")
        for f_path, code_txt in unverified_entries:
            spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
            out.append(f"{lb}*{rb} {_strip_addon_root_prefix(f_path)}{spoiler_part}")
        out.append(f"{lb}/list{rb}")

    if has_bp:
        out.append("")
        out.append(f'{lb}SIZE="4"{rb}{lb}b{rb}{lb}u{rb}{lb}color="DarkOrange"{rb}{lb}FONT="Impact"{rb}Best practices{lb}/FONT{rb}{lb}/color{rb}{lb}/u{rb}{lb}/b{rb}{lb}/SIZE{rb}')

        if hardcoded_lang_files:
            out.append(f"{lb}u{rb}Hardcoded language files - Use dynamic $(language){lb}/u{rb}")
            out.append(f"{lb}spoiler{rb}\n" + "\n".join(hardcoded_lang_files) + f"\n{lb}/spoiler{rb}")

        if dds_comp_grouped:
            out.append("")
            out.append(f"{lb}u{rb}Possible action: DDS texture compression should be DXT5 or DXT3{lb}/u{rb}")
            out.append(f"{lb}list{rb}")
            for fmt_label in sorted(dds_comp_grouped.keys(), key=lambda x: x.lower()):
                items_sorted = sorted(dds_comp_grouped[fmt_label], key=lambda it: str(next(iter(it))).lower())
                formatted_files = ", ".join(
                    f"{_strip_addon_root_prefix(fp)} ({dims})" for fp, dims in items_sorted
                )
                out.append(
                    f'{lb}*{rb} {fmt_label} {lb}spoiler{rb}{lb}SIZE="2"{rb}{formatted_files}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                )
            out.append(f"{lb}/list{rb}")

        if missing_addon_refs:
            out.append("")
            out.append(f"{lb}u{rb}Possible action: local reference to global missing?{lb}/u{rb}")
            out.append("Consider adding a line local <globalName> = <globalName> at the top of your lua files")
            spoiler_sections = []
            for g_name in sorted(missing_addon_refs.keys(), key=lambda x: x.lower()):
                sec_lines = [f"{lb}u{rb}{lb}b{rb}{g_name}{lb}/b{rb}{lb}/u{rb}"]
                seen_locs = set()
                for f_path, lines_val in sorted(missing_addon_refs[g_name], key=lambda item: str(next(iter(item))).lower()):
                    short_fp = _strip_addon_root_prefix(f_path)
                    loc_str = f"  {short_fp}: {lines_val}"
                    if loc_str not in seen_locs:
                        seen_locs.add(loc_str)
                        sec_lines.append(loc_str)
                spoiler_sections.append("\n".join(sec_lines))
            spoiler_body = "\n\n".join(spoiler_sections)
            out.append(f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}')

        outdated_dep_rule = "Possible action: Mandatory version check >= outdated - consider an update"
        outdated_entries = report_data["best_practices"].get(outdated_dep_rule)
        if outdated_entries:
            out.append("")
            out.append(f"{lb}u{rb}{outdated_dep_rule}{lb}/u{rb}")
            out.append("Please verify via the ## AddOnVersion: tags of the actual zip files of your specified dependencies.")
            out.append(f"{lb}list{rb}")
            for f_path, ln_no, code_txt in outdated_entries:
                short_fp = _strip_addon_root_prefix(f_path)
                loc = f"{short_fp}:{ln_no}" if ln_no else short_fp
                spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                out.append(f"{lb}*{rb} {loc}{spoiler_part}")
            out.append(f"{lb}/list{rb}")

        grouped_globals = report_data.get("bp_grouped_globals") if include_multi_globals else None
        filtered_grouped_globals = defaultdict(dict)
        for var_name, files_dict in (grouped_globals or {}).items():
            for f_path, hits_list in files_dict.items():
                if len(hits_list) > 1:
                    filtered_grouped_globals[var_name][_strip_addon_root_prefix(f_path)] = hits_list

        if filtered_grouped_globals:
            out.append("")
            out.append(
                f"{lb}u{rb}Global variable used multiple times w/o a local reference{lb}/u{rb}"
            )
            out.append(f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{lb}list{rb}')
            if int(compact_bp) >= 4:
                per_file_vars = defaultdict(list)
                for var_name in sorted(filtered_grouped_globals.keys(), key=lambda x: x.lower()):
                    for f_path, hits_list in filtered_grouped_globals[var_name].items():
                        per_file_vars[f_path].append(f"{var_name} (x{len(hits_list)})")
                spoiler_lines = []
                for f_path in sorted(per_file_vars.keys(), key=lambda x: x.lower()):
                    var_list = per_file_vars[f_path]
                    short_fp = f_path.split("/", 1)[1] if "/" in f_path else f_path
                    spoiler_lines.append(f"{lb}b{rb}{short_fp}{lb}/b{rb} ({len(var_list)}): {', '.join(var_list)}")
                out.append(
                    f'{lb}*{rb} {len(per_file_vars)} file(s) affected '
                    f'{lb}spoiler{rb}{lb}SIZE="2"{rb}' + "\n".join(spoiler_lines) + f'{lb}/SIZE{rb}{lb}/spoiler{rb}'
                )
            elif int(compact_bp) == 3:
                per_file_vars = defaultdict(list)
                for var_name in sorted(filtered_grouped_globals.keys(), key=lambda x: x.lower()):
                    for f_path, hits_list in filtered_grouped_globals[var_name].items():
                        per_file_vars[f_path].append(f"{var_name} (x{len(hits_list)})")
                spoiler_lines = []
                for f_path in sorted(per_file_vars.keys(), key=lambda x: x.lower()):
                    var_list = per_file_vars[f_path]
                    spoiler_lines.append(
                        f'{lb}b{rb}{f_path}{lb}/b{rb} ({len(var_list)} globals): {", ".join(var_list)}'
                    )
                out.append(
                    f'{lb}*{rb} {len(per_file_vars)} file(s) affected '
                    f'{lb}spoiler{rb}{lb}SIZE="2"{rb}' + "\n".join(spoiler_lines) + f'{lb}/SIZE{rb}{lb}/spoiler{rb}'
                )

            elif int(compact_bp) == 2:
                per_file_vars = defaultdict(list)
                for var_name in sorted(filtered_grouped_globals.keys(), key=lambda x: x.lower()):
                    for f_path, hits_list in filtered_grouped_globals[var_name].items():
                        per_file_vars[f_path].append((var_name, hits_list))
                for f_path in sorted(per_file_vars.keys(), key=lambda x: x.lower()):
                    var_entries = per_file_vars[f_path]
                    spoiler_lines = []
                    for var_name, hits_list in var_entries:
                        all_lns = ", ".join(str(ln) for ln, _ in hits_list)
                        spoiler_lines.append(f"  {lb}b{rb}{var_name}{lb}/b{rb} (x{len(hits_list)}) - Lines: {all_lns}")
                    spoiler_body = "\n".join(spoiler_lines)
                    out.append(
                        f'{lb}*{rb} {lb}b{rb}{f_path}{lb}/b{rb} ({len(var_entries)} globals) '
                        f'{lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}'
                    )
            else:
                for var_name in sorted(filtered_grouped_globals.keys(), key=lambda x: x.lower()):
                    files_dict = filtered_grouped_globals[var_name]
                    total_hits = sum(len(v) for v in files_dict.values())
                    out.append(
                        f"{lb}*{rb} {lb}b{rb}{var_name}{lb}/b{rb} (used {total_hits} times without local reference):"
                    )
                    out.append(f"{lb}list{rb}")
                    for f_path in sorted(files_dict.keys(), key=lambda x: x.lower()):
                        hits_list = files_dict[f_path]
                        if int(compact_bp) >= 1:
                            all_lns = ", ".join(str(ln) for ln, _ in hits_list)
                            out.append(f"{lb}*{rb} {f_path}: lines {all_lns}")
                        else:
                            for ln, code_snip in hits_list:
                                code_suffix = f" [i]({code_snip})[/i]" if code_snip else ""
                                out.append(f"{lb}*{rb} {f_path}:{ln}{code_suffix}")
                    out.append(f"{lb}/list{rb}")
            out.append(f"{lb}/list{rb}{lb}/SIZE{rb}{lb}/spoiler{rb}")

        pcall_bp_rule = "Possible action: Potential AI code - defensive pcall() usage (verify if needed)"
        for bp_rule, entries in report_data["best_practices"].items():
            if bp_rule == outdated_dep_rule:
                continue
            out.append("")
            out.append(f"{lb}u{rb}{bp_rule}{lb}/u{rb}")
            out.append(f"{lb}list{rb}")
            if bp_rule == pcall_bp_rule:
                by_file = defaultdict(list)
                for f_path, ln_no, code_txt in entries:
                    by_file[_strip_addon_root_prefix(f_path)].append((ln_no, code_txt))
                for f_path in sorted(by_file.keys(), key=lambda x: x.lower()):
                    spoiler_lines = []
                    for ln_no, code_txt in by_file[f_path]:
                        prefix_ln = f"{ln_no}: " if ln_no else ""
                        spoiler_lines.append(f"{prefix_ln}{code_txt}".strip())
                    spoiler_body = "\n".join(spoiler_lines)
                    spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}' if spoiler_body else ""
                    out.append(f"{lb}*{rb} {f_path}{spoiler_part}")
            elif compact_bp and len(entries) > 1:
                by_file = defaultdict(list)
                for f_path, ln_no, code_txt in entries:
                    by_file[_strip_addon_root_prefix(f_path)].append((ln_no, code_txt))
                for f_path in sorted(by_file.keys(), key=lambda x: x.lower()):
                    f_hits = by_file[f_path]
                    first_ln, first_code = f_hits[0]
                    loc = f"{f_path}:{first_ln}" if first_ln else f_path
                    if len(f_hits) > 1:
                        extra_lns = ", ".join(str(ln) for ln, _ in f_hits[1:] if ln)
                        spoiler_body = f"{first_code}\nLines: {extra_lns}" if first_code else f"Lines: {extra_lns}"
                    else:
                        spoiler_body = first_code
                    spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{spoiler_body}{lb}/SIZE{rb}{lb}/spoiler{rb}' if spoiler_body else ""
                    out.append(f"{lb}*{rb} {loc}{spoiler_part}")
            else:
                for f_path, ln_no, code_txt in entries:
                    short_fp = _strip_addon_root_prefix(f_path)
                    loc = f"{short_fp}:{ln_no}" if ln_no else short_fp
                    spoiler_part = f' {lb}spoiler{rb}{lb}SIZE="2"{rb}{code_txt}{lb}/SIZE{rb}{lb}/spoiler{rb}' if code_txt else ""
                    out.append(f"{lb}*{rb} {loc}{spoiler_part}")
            out.append(f"{lb}/list{rb}")

    if not has_crit and not has_unverified and not has_bp:
        out.append("")
        out.append(f'{lb}color="Green"{rb}No critical violations or best practice issues found.{lb}/color{rb}')

    return "\n".join(out).strip() + "\n"
def _close_open_bbcode_tags(text_fragment):
    """Returns closing vBulletin tags (in LIFO order) for any still-open formatting/container tags."""
    lb, rb = chr(91), chr(93)
    tag_rx = re.compile(
        rf'{re.escape(lb)}(/?)(b|u|i|s|color|size|font|url|spoiler|list)(?:=[^\]\r\n]+)?{re.escape(rb)}',
        flags=re.IGNORECASE,
    )
    open_stack = []
    for m in tag_rx.finditer(text_fragment):
        is_closing = bool(m.group(1))
        raw_name = m.group(2)
        low_name = raw_name.lower()
        if not is_closing:
            open_stack.append(raw_name)
        else:
            for idx in range(len(open_stack) - 1, -1, -1):
                if open_stack.__getitem__(idx).lower() == low_name:
                    del open_stack[idx:]
                    break
    return "".join(f"{lb}/{tag}{rb}" for tag in reversed(open_stack))


def _strip_dangling_bbcode_prefix(text_fragment):
    """Removes an incomplete trailing '[tag...' fragment if a cut occurred inside a BBCode tag."""
    lb, rb = chr(91), chr(93)
    last_open = text_fragment.rfind(lb)
    if last_open != -1 and text_fragment.find(rb, last_open) == -1:
        return text_fragment[:last_open]
    return text_fragment


def _enforce_report_char_limit(rendered_text, max_chars=ESOUI_COMMENT_MAX_CHARS):
    """Trims oversized [spoiler] bodies first, then falls back to BBCode-balanced truncation with [trunc.]."""
    if len(rendered_text) <= max_chars:
        return rendered_text

    lb, rb = chr(91), chr(93)
    trunc_marker = f"{lb}trunc.{rb}"
    spoiler_rx = re.compile(
        rf'({re.escape(lb)}spoiler{re.escape(rb)}(?:{re.escape(lb)}SIZE="2"{re.escape(rb)})?)(.*?)((?:{re.escape(lb)}/SIZE{re.escape(rb)})?{re.escape(lb)}/spoiler{re.escape(rb)})',
        flags=re.DOTALL,
    )

    def _shrink_spoilers(text_in, max_body_len):
        def _repl(m):
            head, body, tail = m.group(1), m.group(2), m.group(3)
            if len(body) <= max_body_len:
                return m.group(0)
            budget = max(0, max_body_len - len(trunc_marker) - 1)
            cut = _strip_dangling_bbcode_prefix(body[:budget]).rstrip()
            closing_tags = _close_open_bbcode_tags(cut)
            while closing_tags and len(cut) + 1 + len(trunc_marker) + len(closing_tags) > max_body_len and cut:
                trim_step = max(1, (len(cut) + 1 + len(trunc_marker) + len(closing_tags)) - max_body_len)
                cut = _strip_dangling_bbcode_prefix(cut[:max(0, len(cut) - trim_step)]).rstrip()
                closing_tags = _close_open_bbcode_tags(cut)
            return f"{head}{cut} {trunc_marker}{closing_tags}{tail}"
        return spoiler_rx.sub(_repl, text_in)

    candidate = rendered_text
    for body_cap in (600, 250, 100, 40):
        candidate = _shrink_spoilers(candidate, body_cap)
        if len(candidate) <= max_chars:
            return candidate

    keep_len = max(0, max_chars - len(trunc_marker) - 4)
    cut_text = _strip_dangling_bbcode_prefix(candidate[:keep_len])
    if "\n" in cut_text:
        cut_text = cut_text.rsplit("\n", 1).__getitem__(0)
    cut_text = _strip_dangling_bbcode_prefix(cut_text).rstrip()
    closing_tags = _close_open_bbcode_tags(cut_text)
    suffix = f"\n{trunc_marker}{closing_tags}\n"
    while len(cut_text) + len(suffix) > max_chars and cut_text:
        if "\n" in cut_text:
            cut_text = cut_text.rsplit("\n", 1).__getitem__(0).rstrip()
        else:
            cut_text = cut_text[:max(0, max_chars - len(suffix))].rstrip()
        cut_text = _strip_dangling_bbcode_prefix(cut_text).rstrip()
        closing_tags = _close_open_bbcode_tags(cut_text)
        suffix = f"\n{trunc_marker}{closing_tags}\n"
    return cut_text + suffix


def _cap_report_smilies(rendered_text, max_smilies=50):
    """Ensures no more than max_smilies vBulletin smilies (:mad:, :cool:, etc.) appear in a single report."""
    lb, rb = chr(91), chr(93)
    smilie_rx = re.compile(r':(?:mad|cool|rolleyes|confused|eek|redface|biggrin|wink|tongue|frown|smile):', flags=re.IGNORECASE)
    seen = [0]

    def _repl(m):
        seen[0] = seen.__getitem__(0) + 1
        if seen.__getitem__(0) <= max_smilies:
            return m.group(0)
        return f"{lb}!{rb}"

    return smilie_rx.sub(_repl, rendered_text)


def _get_open_bbcode_tag_stack(text_fragment):
    """Returns list of open vBulletin tags (preserving original tag + attribute, e.g. 'SIZE=\"2\"') in open order."""
    lb, rb = chr(91), chr(93)
    tag_rx = re.compile(
        rf'{re.escape(lb)}(/?)((?:b|u|i|s|color|size|font|url|spoiler|list)(?:=[^\]\r\n]+)?){re.escape(rb)}',
        flags=re.IGNORECASE,
    )
    open_stack = []
    for m in tag_rx.finditer(text_fragment):
        is_closing = bool(m.group(1))
        full_tag = m.group(2)
        base_low = full_tag.split("=", 1).__getitem__(0).lower()
        if not is_closing:
            open_stack.append(full_tag)
        else:
            for idx in range(len(open_stack) - 1, -1, -1):
                if open_stack.__getitem__(idx).split("=", 1).__getitem__(0).lower() == base_low:
                    del open_stack[idx:]
                    break
    return open_stack


def _split_bbcode_report_into_posts(full_text, zip_name, timestamp_str, max_chars=ESOUI_COMMENT_MAX_CHARS):
    """
    Splits an oversized BBCode report cleanly on line boundaries into multiple valid vBulletin posts
    (each <= max_chars and <= 50 smilies), closing open BBCode tags at the end of each post and
    re-opening them at the start of the next post so nothing is ever lost with [trunc.].
    """
    lb, rb = chr(91), chr(93)
    capped_full = _cap_report_smilies(full_text, max_smilies=50)
    if len(capped_full) <= max_chars:
        return [capped_full]

    lines = full_text.splitlines()
    raw_chunks = []
    curr_lines = []
    curr_len = 0
    reopen_prefix_lines = []

    def _part_header(part_idx):
        return (
            f'{lb}b{rb}{lb}u{rb}{lb}color="RoyalBlue"{rb}Addon check - report results (Part {part_idx}){lb}/color{rb}{lb}/u{rb}{lb}/b{rb}\n'
            f'{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {zip_name} ({timestamp_str})\n\n'
        )

    footer_reserve = len(f"\n\n{lb}i{rb}(Continued in Part 99/99...){lb}/i{rb}\n") + 8
    for ln in lines:
        part_num = len(raw_chunks) + 1
        header_overhead = len(_part_header(part_num + 10)) if part_num > 1 else 0
        prospective_text = "\n".join(curr_lines + [ln])
        open_tags_after = _get_open_bbcode_tag_stack(prospective_text)
        closing_after = "".join(f"{lb}/{t.split('=', 1).__getitem__(0)}{rb}" for t in reversed(open_tags_after))
        total_if_added = header_overhead + footer_reserve + len(prospective_text) + len(closing_after) + 4

        if curr_lines and total_if_added > max_chars:
            chunk_body = "\n".join(curr_lines).rstrip()
            open_at_break = _get_open_bbcode_tag_stack(chunk_body)
            close_seq = "".join(f"{lb}/{t.split('=', 1).__getitem__(0)}{rb}" for t in reversed(open_at_break))
            if close_seq:
                chunk_body = chunk_body + close_seq
            raw_chunks.append(chunk_body)
            reopen_prefix = "".join(f"{lb}{t}{rb}" for t in open_at_break)
            curr_lines = [reopen_prefix + ln] if reopen_prefix else [ln]
            curr_len = len(curr_lines.__getitem__(0))
        else:
            curr_lines.append(ln)
            curr_len += len(ln) + 1

    if curr_lines:
        final_body = "\n".join(curr_lines).rstrip()
        open_end = _get_open_bbcode_tag_stack(final_body)
        if open_end:
            final_body += "".join(f"{lb}/{t.split('=', 1).__getitem__(0)}{rb}" for t in reversed(open_end))
        raw_chunks.append(final_body)

    total_parts = len(raw_chunks)
    final_posts = []
    for idx, body_txt in enumerate(raw_chunks, 1):
        if idx == 1:
            post_txt = body_txt + f"\n\n{lb}i{rb}(Continued in Part 2/{total_parts}...){lb}/i{rb}\n"
        else:
            hdr = (
                f'{lb}b{rb}{lb}u{rb}{lb}color="RoyalBlue"{rb}Addon check - report results (Part {idx}/{total_parts}){lb}/color{rb}{lb}/u{rb}{lb}/b{rb}\n'
                f'{lb}b{rb}ANALYSIS FOR{lb}/b{rb}: {zip_name} ({timestamp_str})\n\n'
            )
            footer = f"\n\n{lb}i{rb}(Continued in Part {idx + 1}/{total_parts}...){lb}/i{rb}\n" if idx < total_parts else "\n"
            post_txt = hdr + body_txt + footer
        post_txt = _cap_report_smilies(post_txt, max_smilies=50)
        if len(post_txt) > max_chars:
            post_txt = _cap_report_smilies(_enforce_report_char_limit(post_txt, max_chars), max_smilies=50)
        final_posts.append(post_txt)

    return final_posts


def _render_final_bbcode_report(report_file_path, zip_name, timestamp_str, report_data):
    """
    Writes the ESOUI BBCode report. If compact levels fit within ESOUI_COMMENT_MAX_CHARS (9,999),
    writes a single post; otherwise renders the full un-truncated report split into multiple
    posts (<= 9,999 chars each) and writes both a combined overview file and individual _partN.txt files.
    """
    single_post_candidate = None
    for level, tree_errors_only in ((0, False), (1, False), (2, False), (3, False), (3, True), (4, True)):
        cand = _build_bbcode_report_text(
            zip_name, timestamp_str, report_data, compact_bp=level, errors_only_tree=tree_errors_only
        )
        cand = _cap_report_smilies(cand, max_smilies=50)
        if len(cand) <= ESOUI_COMMENT_MAX_CHARS:
            single_post_candidate = cand
            break

    if single_post_candidate is not None:
        with open(report_file_path, "w", encoding="utf-8") as wf:
            wf.write(single_post_candidate)
        return [report_file_path]

    full_untruncated = _build_bbcode_report_text(
        zip_name, timestamp_str, report_data, compact_bp=0, errors_only_tree=False
    )
    posts = _split_bbcode_report_into_posts(full_untruncated, zip_name, timestamp_str, ESOUI_COMMENT_MAX_CHARS)

    base_no_ext, ext_str = os.path.splitext(report_file_path)
    part_paths = []
    combined_sections = []
    for idx, post_body in enumerate(posts, 1):
        part_file = f"{base_no_ext}_part{idx}{ext_str}"
        with open(part_file, "w", encoding="utf-8") as pf:
            pf.write(post_body)
        part_paths.append(part_file)
        combined_sections.append(
            f"==================== ESOUI POST {idx}/{len(posts)} ({len(post_body)} chars) ====================\n{post_body.rstrip()}"
        )

    with open(report_file_path, "w", encoding="utf-8") as wf:
        wf.write("\n\n".join(combined_sections) + "\n")

    return part_paths

def _extract_primary_manifest_info(extract_dir, addon_ctx):
    """Extracts (addon_title, addon_version_num, version_str, manifest_stem) from the primary root manifest."""
    root_mfs = (addon_ctx.get("root_addon_manifests") or []) + (addon_ctx.get("root_txt_manifests") or [])
    if not extract_dir or not os.path.isdir(extract_dir):
        return "", "", "", ""
    top_entries = os.listdir(extract_dir)
    top_dirs = [d for d in top_entries if os.path.isdir(os.path.join(extract_dir, d))]
    top_files = [f for f in top_entries if os.path.isfile(os.path.join(extract_dir, f))]
    manifest_root_dir = os.path.join(extract_dir, next(iter(top_dirs))) if (len(top_dirs) == 1 and not top_files) else extract_dir

    for mf_name in root_mfs:
        mf_path = os.path.join(manifest_root_dir, mf_name)
        if not os.path.isfile(mf_path):
            continue
        mf_stem = os.path.splitext(mf_name).__getitem__(0)
        title_val = ""
        add_on_ver_val = ""
        ver_val = ""
        try:
            with open(mf_path, "r", encoding="utf-8", errors="ignore") as fh:
                for raw_line in fh:
                    line = raw_line.lstrip("\ufeff").strip()
                    m_t = re.match(r"^##\s*Title\s*:\s*(.+)$", line, flags=re.IGNORECASE)
                    if m_t and not title_val:
                        title_val = re.sub(r"\|c[0-9a-fA-F]{6}|\|r", "", m_t.group(1)).strip()
                    m_av = re.match(r"^##\s*AddOnVersion\s*:\s*(\d+)", line, flags=re.IGNORECASE)
                    if m_av and not add_on_ver_val:
                        add_on_ver_val = m_av.group(1).strip()
                    m_v = re.match(r"^##\s*Version\s*:\s*(.+)$", line, flags=re.IGNORECASE)
                    if m_v and not ver_val:
                        ver_val = m_v.group(1).strip()
        except Exception:
            pass
        return title_val or mf_stem, add_on_ver_val, ver_val, mf_stem
    return "", "", "", ""


def _resolve_unique_esoui_id_from_filelist(addon_name, manifest_stem, add_on_ver, ver_str):
    """
    Searches filelist.json by addon name, manifest stem, AddOnVersion, and Version.
    Returns the numeric ESOUI ID string ONLY if there is exactly 1 unambiguous match; otherwise None.
    """
    from src.esoui_filelist_search import get_filelist

    try:
        items = get_filelist(force=False)
    except Exception:
        return None
    if not isinstance(items, list):
        return None

    name_targets = set()
    for raw_n in (addon_name, manifest_stem):
        if raw_n:
            clean_n = re.sub(r"\|c[0-9a-fA-F]{6}|\|r", "", str(raw_n)).strip().lower()
            if clean_n:
                name_targets.add(clean_n)
    if not name_targets:
        return None

    name_matches = []
    for entry in items:
        if not isinstance(entry, dict):
            continue
        eid = str(entry.get("id") or entry.get("UID") or entry.get("addon_id") or "").strip()
        if not eid:
            continue
        title_low = re.sub(r"\|c[0-9a-fA-F]{6}|\|r", "", str(entry.get("title") or entry.get("UIName") or "")).strip().lower()
        sub_addons = entry.get("addons") if isinstance(entry.get("addons"), list) else []
        sub_paths = set()
        for sub in sub_addons:
            if isinstance(sub, dict):
                raw_p = str(sub.get("path") or sub.get("dir") or sub.get("name") or "").replace("\\", "/").strip("/").lower()
                if raw_p:
                    sub_paths.add(raw_p)
                    sub_paths.add(raw_p.rsplit("/", 1)[-1])
        if (title_low and title_low in name_targets) or bool(sub_paths & name_targets):
            name_matches.append(entry)

    if len(name_matches) == 1:
        only_entry = next(iter(name_matches))
        return str(only_entry.get("id") or only_entry.get("UID") or only_entry.get("addon_id") or "").strip() or None
    if not name_matches:
        return None

    narrowed = list(name_matches)
    if add_on_ver:
        av_hits = []
        for entry in narrowed:
            top_av = str(entry.get("addOnVersion") or entry.get("addonVersion") or "").strip()
            sub_avs = {
                str(s.get("addOnVersion") or s.get("addonVersion") or "").strip()
                for s in (entry.get("addons") or [])
                if isinstance(s, dict)
            }
            if add_on_ver == top_av or add_on_ver in sub_avs:
                av_hits.append(entry)
        if len(av_hits) == 1:
            only_entry = next(iter(av_hits))
            return str(only_entry.get("id") or only_entry.get("UID") or only_entry.get("addon_id") or "").strip() or None
        if av_hits:
            narrowed = av_hits

    if ver_str:
        ver_low = ver_str.strip().lower()
        ver_hits = [
            e for e in narrowed
            if str(e.get("version") or e.get("UIVersion") or "").strip().lower() == ver_low
        ]
        if len(ver_hits) == 1:
            only_entry = next(iter(ver_hits))
            return str(only_entry.get("id") or only_entry.get("UID") or only_entry.get("addon_id") or "").strip() or None

    return None


def _count_report_findings(report_data):
    """
    Counts (manifest_count, critical_count, best_practice_count) from report_data
    for compact inline console status badges.
    """
    manifest_crit_map = (report_data.get("critical") or {}).get("manifest") or {}
    manifest_count = (
        sum(len(entries) for entries in manifest_crit_map.values())
        + len(report_data.get("lgb_conflicts") or ())
        + len(report_data.get("zip_manifest_folder_errors") or ())
    )

    lua_crit_map = (report_data.get("critical") or {}).get("lua") or {}
    xml_crit_map = (report_data.get("critical") or {}).get("xml") or {}
    critical_count = (
        len(report_data.get("zip_violations") or ())
        + sum(len(entries) for entries in lua_crit_map.values())
        + sum(len(entries) for entries in xml_crit_map.values())
        + len(report_data.get("global_var_pollution") or ())
        + len(report_data.get("global_func_pollution") or ())
        + len(report_data.get("non_unique_globals") or ())
    )

    bp_map = report_data.get("best_practices") or {}
    missing_refs = report_data.get("missing_local_addon_ref") or {}
    dds_comp_map = report_data.get("dds_compression_grouped") or {}
    bp_count = (
        sum(len(entries) for entries in bp_map.values())
        + sum(len(entries) for entries in missing_refs.values())
        + sum(len(entries) for entries in dds_comp_map.values())
        + len(report_data.get("hardcoded_lang_files") or ())
        + len(report_data.get("unverified_globals") or ())
    )
    if is_bp_multi_globals_enabled():
        grouped_g = report_data.get("bp_grouped_globals") or {}
        for files_dict in grouped_g.values():
            for hits_list in files_dict.values():
                if len(hits_list) > 1:
                    bp_count += 1

    return manifest_count, critical_count, bp_count


def _format_findings_status_badge(manifest_count, critical_count, bp_count):
    """Formats inline status badge showing '✅ Clean' when all 0, or only non-zero icons (📋, ❌, 💡)."""
    if manifest_count == 0 and critical_count == 0 and bp_count == 0:
        return f"  {C.GREEN}\u2705 Clean{C.RESET}"
    parts = []
    if manifest_count > 0:
        parts.append(f"{C.ORANGE}\U0001f4cb {manifest_count}{C.RESET}")
    if critical_count > 0:
        parts.append(f"{C.RED}\u274c {critical_count}{C.RESET}")
    if bp_count > 0:
        parts.append(f"{C.YELLOW}\U0001f4a1 {bp_count}{C.RESET}")
    return f"  ({' | '.join(parts)})"


def print_multi_addon_summary(summary_items):
    """Prints a numbered clickable summary list when more than 1 add-on was checked in a batch/multi-run."""
    if not summary_items or len(summary_items) <= 1:
        return
    lb, rb = chr(91), chr(93)
    print(f"{C.CYAN}{C.BOLD}Checked add-ons summary:{C.RESET}")
    for idx, item in enumerate(summary_items, 1):
        aid = str(item.get("addon_id") or "").strip()
        if aid and aid.isdigit():
            comments_url = f"{ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}{aid}/#comments"
            id_badge = f"{lb}{make_clickable_url_link(comments_url, color=C.CYAN, display_text=aid)}{rb}"
        else:
            id_badge = f"{lb}{C.YELLOW}local{C.RESET}{rb}"

        addon_name = str(item.get("addon_name") or item.get("zip_name") or "Unknown").strip()
        report_path = item.get("report_path") or ""
        clickable_name = (
            format_report_display_link(report_path, color=C.WHITE, custom_label=f"\U0001f4c4 {addon_name}")
            if report_path
            else f"{C.WHITE}\U0001f4c4 {addon_name}{C.RESET}"
        )

        ver_disp = str(item.get("version_display") or "?").strip()
        zip_path = item.get("zip_path") or ""
        clickable_zip = format_zip_display_link(zip_path, color=C.CYAN) if zip_path else str(item.get("zip_name") or "")
        status_badge = str(item.get("status_badge") or "")

        print(f"  {C.WHITE}{idx}){C.RESET} {id_badge} {clickable_name} (Version: {C.GREEN}{ver_disp}{C.RESET} {clickable_zip}){status_badge}")

def process_addon(
    zip_path,
    zip_name,
    known_addon_id=None,
    known_addon_title=None,
    known_addon_version=None,
    summary_collector=None,
):
    """Coordinates ZIP audit, extraction, static analysis, AI review, and compact BBCode report."""
    addon_start_time = datetime.now()
    BATCH_LEAK_TRACKER.clear()
    BATCH_BEST_PRACTICE_TRACKER.clear()

    osc_mark_start = "\033]133;A\033\\" if os.name == "nt" else ""
    print(f"{osc_mark_start}{C.CYAN}-------------------------------------------------------------------{C.RESET}")
    clickable_zip_start = format_zip_display_link(zip_path, color=C.WHITE)
    print(f"{C.CYAN}{C.BOLD}  ADDON START: {clickable_zip_start} {C.RESET}{C.CYAN}(Jump marks: Ctrl+Alt+Up/Down){C.RESET}")

    os.makedirs(EXTRACT_FOLDER, exist_ok=True)
    now = datetime.now()
    timestamp_str = now.strftime("%Y-%m-%d %I:%M:%S %p")
    current_date_report_dir = os.path.join(REPORTS_BASE_DIR, now.strftime("%y%m%d"))
    os.makedirs(current_date_report_dir, exist_ok=True)

    zip_clean_name = zip_name[:-4] if zip_name.lower().endswith('.zip') else zip_name
    current_report_file = os.path.join(current_date_report_dir, f"{now.strftime('%y%m%d_%H%M%S')}_{zip_clean_name}.txt")
    addon_code_bundle = []
    ai_preflight_triggered = False
    mf_title = ""
    mf_addon_ver = ""
    mf_ver_str = ""
    mf_stem = ""
    resolved_addon_id = str(known_addon_id).strip() if known_addon_id is not None else ""

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
        mf_title, mf_addon_ver, mf_ver_str, mf_stem = _extract_primary_manifest_info(current_extract_dir, addon_ctx)
        xml_txt_combined = str(addon_ctx.get("xml_content") or "")
        any_global_used_in_xml = any(
            bool(re.search(r'\b' + re.escape(gt) + r'\b', xml_txt_combined))
            for gt in (addon_ctx.get("all_global_tables") or ())
            if gt
        )
        own_lua_cnt = int(addon_ctx.get("own_lua_file_count") or addon_ctx.get("lua_file_count") or 0)
        report_data["is_strict_local_addon"] = (
            own_lua_cnt <= 1
            and not bool(addon_ctx.get("has_bindings_xml"))
            and not bool(addon_ctx.get("is_library"))
            and not bool(addon_ctx.get("has_public_api_functions"))
            and not any_global_used_in_xml
        )
        id_m = re.search(r'(?:^|[_-])(\d{2,6})(?:[_.-]|$)', zip_clean_name)
        if id_m:
            addon_ctx["current_addon_id"] = id_m.group(1)
        else:
            from src.esoui_filelist_search import resolve_dependency_online_package
            for root_mf in (addon_ctx.get("root_addon_manifests") or []) + (addon_ctx.get("root_txt_manifests") or []):
                root_stem, _ = os.path.splitext(root_mf)
                pkg_self = resolve_dependency_online_package(root_stem)
                if pkg_self and not pkg_self.get("is_embedded"):
                    addon_ctx["current_addon_id"] = pkg_self.get("addon_id")
                    break

        files_to_process = []
        for root, _, files in os.walk(current_extract_dir):
            for file in files:
                lower_file = file.lower()
                if lower_file.endswith(('.xml', '.lua', '.txt', '.addon')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, current_extract_dir)
                    priority = 0 if lower_file.endswith(('.addon', '.txt')) else (1 if lower_file.endswith('.xml') else 2)
                    files_to_process.append((priority, rel_path.lower(), file, file_path, rel_path))

        files_to_process.sort(key=lambda item: (item[0], item[1]))

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
                                    clean_console_r = re.sub(
                                        r"\[/?(?:color|b|i|u|s|size|font|url|spoiler|list|\*)(?:=[^\]]+)?\]",
                                        "",
                                        stripped_r,
                                        flags=re.IGNORECASE,
                                    )
                                    print_wrapped_tree_item(clean_console_r, color=C.RED)
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
    for f_path, _, _, _ in report_data.get("global_var_pollution") or []:
        all_flagged.add(f_path)
    for f_path, _, _ in report_data.get("global_func_pollution") or []:
        all_flagged.add(f_path)
    for f_path, _, _ in report_data.get("non_unique_globals") or []:
        all_flagged.add(f_path)
    for f_path, _, _ in report_data.get("lgb_conflicts") or []:
        all_flagged.add(f_path)
    for cat_rules in report_data["critical"].values():
        for entries in cat_rules.values():
            for f_path, _, _ in entries:
                if f_path.startswith("EVENT_FILTER::"):
                    all_flagged.add(f_path.split("::", 2)[2])
                else:
                    all_flagged.add(f_path)
    if report_data.get("zip_all_entries"):
        report_data["zip_all_flagged"] = set(all_flagged)
        report_data["zip_tree_bbcode"] = _build_bbcode_zip_list(
            report_data["zip_all_entries"],
            all_flagged,
            report_data.get("zip_manifest_paths", set()),
        )

    generated_report_files = _render_final_bbcode_report(current_report_file, zip_name, timestamp_str, report_data)

    display_addon_name = (
        mf_title
        or (str(known_addon_title).strip() if known_addon_title else "")
        or mf_stem
        or zip_clean_name
    )
    display_version = (
        mf_addon_ver
        or mf_ver_str
        or (str(known_addon_version).strip() if known_addon_version else "")
        or "?"
    )
    if not resolved_addon_id:
        resolved_addon_id = _resolve_unique_esoui_id_from_filelist(
            display_addon_name, mf_stem, mf_addon_ver, mf_ver_str
        ) or ""

    mf_cnt, crit_cnt, bp_cnt = _count_report_findings(report_data)
    status_badge = _format_findings_status_badge(mf_cnt, crit_cnt, bp_cnt)

    summary_entry = {
        "addon_id": resolved_addon_id,
        "addon_name": display_addon_name,
        "version_display": display_version,
        "zip_path": zip_path,
        "zip_name": zip_name,
        "report_path": current_report_file,
        "status_badge": status_badge,
    }
    if isinstance(summary_collector, list):
        summary_collector.append(summary_entry)

    if os.path.exists(EXTRACT_FOLDER):
        shutil.rmtree(EXTRACT_FOLDER)
    addon_duration = (datetime.now() - addon_start_time).total_seconds()
    clickable_zip_end = format_zip_display_link(zip_path, color=C.WHITE)
    osc_mark_end = "\033]133;D\033\\" if os.name == "nt" else ""
    print(f"\n{C.CYAN}[4/4] Report saved to:{C.RESET} {format_report_display_link(current_report_file)}{status_badge}")
    if len(generated_report_files) > 1:
        print(f"    {C.YELLOW}ℹ Report split into {len(generated_report_files)} ESOUI posts (max {ESOUI_COMMENT_MAX_CHARS} chars each):{C.RESET}")
        for part_idx, part_fp in enumerate(generated_report_files, 1):
            print(f"      - Post {part_idx}/{len(generated_report_files)}: {format_report_display_link(part_fp)}")
    print(f"{osc_mark_end}{C.CYAN}{C.BOLD}  ADDON END:   {clickable_zip_end}{C.CYAN} ({C.MAGENTA}{addon_duration:.2f}s{C.CYAN}){C.RESET}")
    print(f"{C.CYAN}{C.BOLD}=================================================================={C.RESET}\n")
    return summary_entry
