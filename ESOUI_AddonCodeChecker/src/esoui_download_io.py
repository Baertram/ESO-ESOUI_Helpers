"""
HTTP-Download mit Cookie-Session-Handling, lokalem ZIP-Cache, Eingabe-Validierung
sowie interaktiver CLI-Eingabe und 'clear'-Bereinigung.
"""

import hashlib
import http.cookiejar
import os
import re
import shutil
import sys
import urllib.request
from datetime import datetime

from src.esoui_config import (
    ALLOWED_DOWNLOAD_DOMAINS,
    C,
    CACHE_ADDONS_DIR,
    CACHE_DIR,
    ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX,
    ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX,
    ESOUI_LATEST_MAX_ITEMS,
    REPORTS_BASE_DIR,
    ZIP_FOLDER,
    get_project_root_dir,
    make_clickable_file_link,
)


def compute_file_sha256(file_path):
    """Computes the SHA-256 hash of a local file."""
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def download_zip(url, target_folder, force_download=False):
    """
    Validates that the remote ESOUI response is an actual non-empty ZIP archive,
    checks today's local Zips/<YYMMDD> cache before downloading body bytes,
    and verifies ZIP magic bytes.
    """
    now = datetime.now()
    folder_date = now.strftime("%y%m%d")
    permanent_zip_dir = os.path.join(target_folder, folder_date)
    os.makedirs(permanent_zip_dir, exist_ok=True)

    print(f"\n{C.CYAN}{C.BOLD}=================================================================={C.RESET}")
    mode_tag = f" {C.YELLOW}[FORCE RE-DOWNLOAD]{C.CYAN}" if force_download else ""
    print(f"{C.CYAN}[1/4] Checking remote ZIP metadata:{mode_tag} {url} ...{C.RESET}")
    try:
        cookie_jar = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'),
            ('Accept', '*/*')
        ]

        response = opener.open(url, timeout=20)
        content_type = response.headers.get("Content-Type", "").lower()
        content_disp = response.headers.get("Content-Disposition", "")
        remote_len_hdr = response.headers.get("Content-Length")
        remote_size = int(remote_len_hdr) if (remote_len_hdr and remote_len_hdr.isdigit()) else None

        if "text/html" in content_type and "attachment" not in content_disp.lower():
            raw_html_bytes = response.read()
            response.close()
            id_in_url = re.search(r'(?:dl|info)(\d+)', url, flags=re.IGNORECASE)

            if not raw_html_bytes.strip() and id_in_url:
                addon_id = id_in_url.group(1)
                info_url = f"{ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}{addon_id}-"
                try:
                    info_resp = opener.open(info_url, timeout=20)
                    info_html = info_resp.read().decode("iso-8859-1", errors="ignore")
                    final_info_url = info_resp.geturl()
                    info_resp.close()

                    if info_html.strip():
                        retry_req = urllib.request.Request(url, headers={'Referer': final_info_url})
                        response = opener.open(retry_req, timeout=20)
                        content_type = response.headers.get("Content-Type", "").lower()
                        content_disp = response.headers.get("Content-Disposition", "")
                        remote_len_hdr = response.headers.get("Content-Length")
                        remote_size = int(remote_len_hdr) if (remote_len_hdr and remote_len_hdr.isdigit()) else None

                        if "text/html" in content_type and "attachment" not in content_disp.lower():
                            raw_html_bytes = response.read()
                            response.close()
                except Exception:
                    pass
            if "text/html" in content_type and "attachment" not in content_disp.lower():
                html_body = raw_html_bytes.decode("iso-8859-1", errors="ignore")
                if not html_body.strip():
                    print(f"{C.RED}-> Error: Addon / download URL does not exist on ESOUI (empty page returned).{C.RESET}")
                    return None, None
                cdn_match = re.search(r'https?://[^"\'\s<>]+\.zip(?:\?[^"\'\s<>]*)?', html_body, flags=re.IGNORECASE)
                if cdn_match:
                    cdn_url = cdn_match.group(0)
                    print(f"{C.CYAN}-> Resolved ESOUI mirror link:{C.RESET} {C.WHITE}{cdn_url}{C.RESET}")
                    response = opener.open(cdn_url, timeout=20)
                    content_type = response.headers.get("Content-Type", "").lower()
                    content_disp = response.headers.get("Content-Disposition", "")
                    remote_len_hdr = response.headers.get("Content-Length")
                    remote_size = int(remote_len_hdr) if (remote_len_hdr and remote_len_hdr.isdigit()) else None
                else:
                    print(
                        f"{C.RED}-> Error: Addon / download URL returned an HTML page without a ZIP archive "
                        f"(HTTP Content-Type: '{content_type}').{C.RESET}"
                    )
                    return None, None

        with response:
            if remote_size == 0:
                print(f"{C.RED}-> Error: Addon / download URL returned an empty (0 byte) response.{C.RESET}")
                return None, None

            filename = None
            cd_match = re.search(r'filename\*?=(?:UTF-8\'\')?["\']?([^"\';]+)["\']?', content_disp, flags=re.IGNORECASE)
            if cd_match:
                filename = os.path.basename(cd_match.group(1).strip())

            if not filename:
                final_url_end = response.geturl().split("/")[-1].split("?", 1)
                if final_url_end.lower().endswith(".zip"):
                    filename = final_url_end

            if not filename:
                url_end = url.split("/")[-1].split("?", 1)
                filename = url_end if url_end.lower().endswith(".zip") else "downloaded_addon.zip"

            target_path = os.path.join(permanent_zip_dir, filename)
            short_zip_label = os.path.join("\\Zips", folder_date, filename)

            if not force_download and os.path.isfile(target_path):
                local_size = os.path.getsize(target_path)
                if remote_size is not None and local_size == remote_size and local_size > 0:
                    print(
                        f"{C.GREEN}-> Cache hit! Identical ZIP already exists locally "
                        f"({C.WHITE}{local_size:,} bytes{C.GREEN}), skipping download:{C.RESET} "
                        f"{make_clickable_file_link(target_path, display_text=short_zip_label)}"
                    )
                    return target_path, filename

            print(f"{C.CYAN}-> Downloading {C.WHITE}{filename}{C.CYAN} ...{C.RESET}")
            raw_data = response.read()

            if not raw_data or not raw_data.startswith(b"PK\x03\x04"):
                print(
                    f"{C.RED}-> Error: Addon / download URL returned an empty page or invalid ZIP data "
                    f"({len(raw_data)} bytes). Nothing was saved.{C.RESET}"
                )
                return None, None

            if not force_download and os.path.isfile(target_path):
                local_sha = compute_file_sha256(target_path)
                remote_sha = hashlib.sha256(raw_data).hexdigest()
                if local_sha == remote_sha:
                    print(
                        f"{C.GREEN}-> Cache hit! Identical SHA-256 ({C.WHITE}{remote_sha[:12]}...{C.GREEN}), "
                        f"using existing local ZIP:{C.RESET} "
                        f"{make_clickable_file_link(target_path, display_text=short_zip_label)}"
                    )
                    return target_path, filename

            with open(target_path, "wb") as out_file:
                out_file.write(raw_data)

        print(f"{C.CYAN}-> Download finished successfully! Kept permanently in:{C.RESET} {make_clickable_file_link(target_path, display_text=short_zip_label)}")
        return target_path, filename
    except Exception as e:
        print(f"{C.RED}-> Error downloading file: {str(e)}{C.RESET}")
        return None, None


def is_authorized_esoui_url(text_input):
    """Returns True if text_input is an http(s) URL pointing to an authorized ESOUI/MMOUI domain."""
    low = (text_input or "").strip().lower()
    if not low.startswith(("http://", "https://")):
        return False
    return any(domain in low for domain in ALLOWED_DOWNLOAD_DOMAINS)
def handle_input(user_input, force_download=False):
    """Validates user input (authorized URL with info->dl rewrite, local .zip file, or cached ZIP name)."""
    user_input = user_input.strip('"').strip("'").strip()

    if user_input.lower().startswith("force "):
        force_download = True
        user_input = user_input[6:].strip().strip('"').strip("'").strip()

    if user_input.startswith(("http://", "https://")):
        if not is_authorized_esoui_url(user_input):
            print(f"{C.RED}-> SECURITY BLOCK: URL is not from an authorized ESOUI server! Rejected: {user_input}{C.RESET}")
            return None, None

        search_prefix_escaped = re.escape(ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX).replace(r"https://www\.", r"https?://(?:www\.)?")
        info_match = re.match(
            rf'^{search_prefix_escaped}(\d+)(?:-[^/?#]+)?(?:\.html)?(?:[?#].*)?$',
            user_input,
            flags=re.IGNORECASE
        )
        if info_match:
            addon_id = info_match.group(1)
            rewritten_url = f"{ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}{addon_id}/"
            print(f"{C.CYAN}-> Rewrote ESOUI info link to direct download URL:{C.RESET} {C.WHITE}{rewritten_url}{C.RESET}")
            user_input = rewritten_url

        return download_zip(user_input, ZIP_FOLDER, force_download=force_download)

    if os.path.exists(user_input):
        if not user_input.lower().endswith(".zip"):
            print(f"{C.RED}-> SECURITY BLOCK: Local file is not a ZIP archive! Rejected: {user_input}{C.RESET}")
            return None, None

        filename = os.path.basename(user_input)
        now = datetime.now().strftime("%y%m%d")
        permanent_zip_dir = os.path.join(ZIP_FOLDER, now)
        os.makedirs(permanent_zip_dir, exist_ok=True)

        target_path = os.path.join(permanent_zip_dir, filename)
        if os.path.abspath(user_input) != os.path.abspath(target_path):
            shutil.copy2(user_input, target_path)
        short_zip_label = os.path.join("\\Zips", now, filename)
        print(f"\n{C.CYAN}{C.BOLD}=================================================================={C.RESET}")
        print(f"{C.CYAN}[1/4] Loading local ZIP archive:{C.RESET} {make_clickable_file_link(target_path, display_text=short_zip_label)}")
        return target_path, filename

    now = datetime.now().strftime("%y%m%d")
    check_in_zip_folder = os.path.join(ZIP_FOLDER, now, user_input if user_input.endswith(".zip") else user_input + ".zip")
    if os.path.exists(check_in_zip_folder):
        filename = os.path.basename(check_in_zip_folder)
        short_zip_label = os.path.join("\\Zips", now, filename)
        print(f"\n{C.CYAN}{C.BOLD}=================================================================={C.RESET}")
        print(f"{C.CYAN}[1/4] Using cached ZIP archive:{C.RESET} {make_clickable_file_link(check_in_zip_folder, display_text=short_zip_label)}")
        return check_in_zip_folder, filename

    print(
        f"{C.RED}-> Error: Invalid input. Supported inputs are:\n"
        f"   - ESOUI download/info URL: {ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX}<addonId> (or {ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX}<addonId>/)\n"
        f"   - Direct addon ID command: 'dl <addonId>' (e.g. 'dl 5026')\n"
        f"   - Latest Live Addons (1..{ESOUI_LATEST_MAX_ITEMS}): 'last <spec>' (e.g. 'last 5', 'last 2-5', 'last 1, 3, 7, 10-20')\n"
        f"   - Search Addons / Deps / Author / API: 'search <q1, q2>', 'search dep <d1, d2>', 'search author <a1, a2>', or 'search api <v1, !v2>'\n"
        f"   - Repeat previous check command: 'repeat', 'repeat dl', or 'repeat search'\n"
        f"   - Optional 'force ' prefix to bypass filelist/ZIP cache (e.g. 'force dl 5026', 'force last 1-3', 'force search Lib', 'force repeat')\n"
        f"   - Local .zip archive or .txt batch list file{C.RESET}"
    )
    return None, None


def read_cli_input_with_esc(prompt_text):
    """Reads a line from the console while listening for ESC/Ctrl+C on Windows TTY."""
    if os.name == "nt" and sys.stdin.isatty():
        import msvcrt
        sys.stdout.write(prompt_text)
        sys.stdout.flush()
        chars = []
        while True:
            ch = msvcrt.getwch()
            if ch in ("\x1b", "\x03"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "__ESC__"
            if ch in ("\r", "\n"):
                sys.stdout.write("\n")
                sys.stdout.flush()
                return "".join(chars)
            if ch == "\b":
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
                continue
            if ch in ("\x00", "\xe0"):
                msvcrt.getwch()
                continue
            chars.append(ch)
            sys.stdout.write(ch)
            sys.stdout.flush()
    return input(prompt_text)


def parse_last_selection_spec(spec_str, max_items):
    """Parses a selection string like '5', '2-5', or '1, 3, 7, 10-20'."""
    raw_spec = (spec_str or "").strip()
    if not raw_spec:
        return None, f"Missing selection. Examples: '5', '2-5', '1, 3, 7, 10-20' (range 1..{max_items})."

    if raw_spec.startswith(",") or raw_spec.endswith(",") or ",," in raw_spec:
        return None, f"Empty entry in '{raw_spec}'. Remove trailing or double commas."

    selected = []
    seen = set()
    for tok in [t.strip() for t in re.split(r"[,\s]+", raw_spec) if t.strip()]:
        range_match = re.match(r'^(\d+)\s*-\s*(\d+)$', tok)
        single_match = re.match(r'^(\d+)$', tok)
        if range_match:
            start_idx, end_idx = int(range_match.group(1)), int(range_match.group(2))
            if start_idx < 1 or end_idx > max_items:
                return None, f"Range '{tok}' out of bounds. Allowed values are 1..{max_items}."
            if start_idx > end_idx:
                return None, f"Invalid range '{tok}': start ({start_idx}) must be <= end ({end_idx})."
            for idx in range(start_idx, end_idx + 1):
                if idx not in seen:
                    seen.add(idx)
                    selected.append(idx)
        elif single_match:
            val = int(single_match.group(1))
            if val < 1 or val > max_items:
                return None, f"Value '{val}' out of bounds. Allowed values are 1..{max_items}."
            if val not in seen:
                seen.add(val)
                selected.append(val)
        else:
            return None, f"Invalid token '{tok}' in '{raw_spec}'. Use numbers or ranges like '2-5' (1..{max_items})."
    return selected, None


def parse_dl_command(text_input):
    """
    Matches 'dl <spec>' (e.g. 'dl 5026', 'dl 630, 3586', 'dl 630 3586', 'dl 630-632')
    and returns a list of numeric addon ID strings (or None if invalid).
    """
    m = re.match(r'^dl(?:\s+|(?=\d))(.+)$', (text_input or "").strip(), flags=re.IGNORECASE)
    if not m:
        return None
    spec_part = m.group(1).strip()
    id_ints, err = parse_last_selection_spec(spec_part, 999999999)
    if err or not id_ints:
        return None
    return [str(i) for i in id_ints]


def handle_clear_command(arg_str):
    """Handles 'clear cache', 'clear cache addons', 'clear zips [YYMMDD]', and 'clear reports [YYMMDD]'."""
    raw_args = (arg_str or "").strip()
    if not raw_args:
        print(
            f"{C.RED}-> Error: Missing parameter for 'clear'. Usage:\n"
            f"   - clear cache\n"
            f"   - clear cache addons\n"
            f"   - clear zips [YYMMDD]\n"
            f"   - clear reports [YYMMDD]{C.RESET}"
        )
        return

    parts = raw_args.split()
    target_type = parts[0].lower()
    if target_type not in ("cache", "zips", "reports"):
        print(f"{C.RED}-> Error: Unknown 'clear' target '{parts[0]}'. Allowed targets: cache, cache addons, zips, reports.{C.RESET}")
        return
    if target_type == "cache":
        if len(parts) == 2 and parts[1].lower() == "addons":
            target_type = "cache_addons"
        elif len(parts) > 1:
            print(f"{C.RED}-> Error: 'clear cache' only accepts optional sub-target 'addons' ('clear cache addons').{C.RESET}")
            return
    elif len(parts) > 2:
        print(f"{C.RED}-> Error: Too many parameters for 'clear {target_type}'. Expected optional YYMMDD date.{C.RESET}")
        return

    cutoff_date_str = None
    if len(parts) == 2:
        cutoff_date_str = parts[1]

        if not re.match(r'^\d{6}$', cutoff_date_str):
            print(f"{C.RED}-> Error: Invalid date '{cutoff_date_str}'. Expected 6-digit YYMMDD format.{C.RESET}")
            return
        try:
            datetime.strptime(cutoff_date_str, "%y%m%d")
        except ValueError:
            print(f"{C.RED}-> Error: Calendar date '{cutoff_date_str}' is invalid.{C.RESET}")
            return

    files_to_delete, dirs_to_delete = [], []
    if target_type in ("cache", "cache_addons"):
        if target_type == "cache":
            root_dir = get_project_root_dir()
            for pycache_dir in (os.path.join(root_dir, "__pycache__"), os.path.join(root_dir, "src", "__pycache__")):
                if os.path.isdir(pycache_dir):
                    for root, dirs, files in os.walk(pycache_dir, topdown=False):
                        for fn in files:
                            files_to_delete.append(os.path.join(root, fn))
                        for dn in dirs:
                            dirs_to_delete.append(os.path.join(root, dn))
                    dirs_to_delete.append(pycache_dir)
            fl_cache = os.path.join(CACHE_DIR, "filelist.json")
            if os.path.isfile(fl_cache):
                files_to_delete.append(os.path.abspath(fl_cache))

        dep_cache = os.path.join(CACHE_DIR, "dependency_globals_cache.json")
        if os.path.isfile(dep_cache):
            files_to_delete.append(os.path.abspath(dep_cache))

        if os.path.isdir(CACHE_ADDONS_DIR):
            for root, dirs, files in os.walk(CACHE_ADDONS_DIR, topdown=False):
                for fn in files:
                    files_to_delete.append(os.path.join(root, fn))
                for dn in dirs:
                    dirs_to_delete.append(os.path.join(root, dn))
            dirs_to_delete.append(os.path.abspath(CACHE_ADDONS_DIR))

    else:
        base_target_dir = ZIP_FOLDER if target_type == "zips" else REPORTS_BASE_DIR
        if os.path.isdir(base_target_dir):
            for entry_name in sorted(os.listdir(base_target_dir)):
                entry_path = os.path.join(base_target_dir, entry_name)
                if os.path.isdir(entry_path):
                    if cutoff_date_str is not None and (not re.match(r'^\d{6}$', entry_name) or entry_name > cutoff_date_str):
                        continue
                    for root, dirs, files in os.walk(entry_path, topdown=False):
                        for fn in files:
                            files_to_delete.append(os.path.join(root, fn))
                        for dn in dirs:
                            dirs_to_delete.append(os.path.join(root, dn))
                    dirs_to_delete.append(entry_path)
                elif os.path.isfile(entry_path) and cutoff_date_str is None:
                    files_to_delete.append(entry_path)

    if not files_to_delete and not dirs_to_delete:
        scope_note = f" up to {cutoff_date_str}" if cutoff_date_str else ""
        print(f"{C.CYAN}-> Nothing to delete for 'clear {target_type}{scope_note}'.{C.RESET}")
        return

    scope_desc = f" (up to and including {cutoff_date_str})" if cutoff_date_str else " (all)"
    print(
        f"\n{C.YELLOW}[CONFIRM DELETE]{C.RESET} Found {C.WHITE}{len(files_to_delete)}{C.RESET} file(s) "
        f"and {C.WHITE}{len(dirs_to_delete)}{C.RESET} folder(s) for '{C.WHITE}clear {target_type}{scope_desc}{C.RESET}'."
    )
    answer = read_cli_input_with_esc("Do you really want to permanently delete these files and folders? (y/n): ").strip().lower()
    if answer not in ("y", "yes"):
        print(f"{C.CYAN}-> Deletion cancelled.{C.RESET}\n")
        return

    deleted_files = 0
    deleted_dirs = 0

    for f_path in files_to_delete:
        try:
            os.remove(f_path)
            deleted_files += 1
            print(f"  {C.RED}[DELETED FILE]{C.RESET}   {f_path}")
        except Exception as e:
            print(f"  {C.YELLOW}[ERROR FILE]{C.RESET}     {f_path} ({e})")

    for d_path in dirs_to_delete:
        try:
            if os.path.isdir(d_path):
                os.rmdir(d_path)
                deleted_dirs += 1
                print(f"  {C.RED}[DELETED FOLDER]{C.RESET} {d_path}")
        except Exception as e:
            print(f"  {C.YELLOW}[ERROR FOLDER]{C.RESET}   {d_path} ({e})")

    if target_type in ("cache", "cache_addons"):
        try:
            from src.esoui_ram_index import reset_dependency_globals_cache
            reset_dependency_globals_cache()
        except Exception:
            pass

    print(
        f"{C.GREEN}-> Cleanup finished: deleted {C.WHITE}{deleted_files}{C.GREEN} file(s) "
        f"and {C.WHITE}{deleted_dirs}{C.GREEN} folder(s).{C.RESET}\n"
    )

