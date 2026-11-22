#!/usr/bin/env python3
"""
Hilfsmodul für den Zugriff auf und die Suche in der MMOUI/ESOUI filelist.json.
"""

import json
import os
import re
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

from src.esoui_config import MMOUI_FILELIST_URL

# MMOUI v4 live add-on catalog endpoint and 15-minute RAM/Disk cache state
FILELIST_URL = MMOUI_FILELIST_URL
DEFAULT_CACHE_PATH = Path("Cache") / "filelist.json"
CACHE_TTL_SECONDS = 15 * 60  # 15 minutes

_RAM_CACHE: Dict[str, Any] = {
    "timestamp": 0.0,
    "data": None,
}


def parse_selection_spec(spec: str, max_index: int) -> List[int]:
    """
    Parst eine 1-basierte Auswahl-Spezifikation (z. B. '1-5, 8, 10-12')
    und gibt eine deduplizierte Liste 1-basierter Indizes in Eingabereihenfolge zurück.
    """
    if not spec or not spec.strip():
        return []
    result: List[int] = []
    seen = set()
    for part in spec.split(","):
        token = part.strip()
        if not token:
            continue
        if "-" in token:
            bounds = token.split("-", 1)
            if len(bounds) != 2 or not bounds[0].strip().isdigit() or not bounds[1].strip().isdigit():
                raise ValueError(f"Ungültiger Bereich: '{token}'")
            start, end = int(bounds[0].strip()), int(bounds[1].strip())
            if start < 1 or end < start:
                raise ValueError(f"Ungültige Bereichsgrenzen: '{token}'")
            for idx in range(start, min(end, max_index) + 1):
                if idx not in seen:
                    seen.add(idx)
                    result.append(idx)
        else:
            if not token.isdigit():
                raise ValueError(f"Ungültiger Index: '{token}'")
            idx = int(token)
            if idx < 1:
                raise ValueError(f"Index muss >= 1 sein: '{token}'")
            if idx <= max_index and idx not in seen:
                seen.add(idx)
                result.append(idx)
    return result


def _fetch_remote_filelist(url: str = FILELIST_URL, timeout: float = 20.0) -> List[Dict[str, Any]]:
    """Downloads and parses the raw MMOUI v4 filelist.json array from the remote API."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "esoui_codecheck/1.0"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("Unerwartetes Format der MMOUI filelist.json (Liste erwartet).")
    return data


def get_filelist(
    force: bool = False,
    cache_path: Path = DEFAULT_CACHE_PATH,
    ttl_seconds: int = CACHE_TTL_SECONDS,
    fetcher: Optional[Callable[[], List[Dict[str, Any]]]] = None,
) -> List[Dict[str, Any]]:
    """
    Lädt die ESOUI-Filelist aus RAM-Cache, Disk-Cache oder Remote-API.
    Umgeht beide Caches, wenn force=True gesetzt ist.
    """
    now = time.time()
    fetch_fn = fetcher or _fetch_remote_filelist

    if not force and _RAM_CACHE["data"] is not None:
        if (now - float(_RAM_CACHE["timestamp"])) < ttl_seconds:
            return _RAM_CACHE["data"]

    cache_file = Path(cache_path)
    if not force and cache_file.exists():
        try:
            mtime = cache_file.stat().st_mtime
            if (now - mtime) < ttl_seconds:
                with cache_file.open("r", encoding="utf-8") as fh:
                    disk_data = json.load(fh)
                if isinstance(disk_data, list):
                    _RAM_CACHE["data"] = disk_data
                    _RAM_CACHE["timestamp"] = mtime
                    return disk_data
        except (OSError, json.JSONDecodeError):
            pass
    fresh_data = fetch_fn()
    _RAM_CACHE["data"] = fresh_data
    _RAM_CACHE["timestamp"] = now

    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        tmp_file = cache_file.with_suffix(".tmp")
        with tmp_file.open("w", encoding="utf-8") as fh:
            json.dump(fresh_data, fh, ensure_ascii=False)
        os.replace(tmp_file, cache_file)
    except OSError:
        pass

    return fresh_data
def _extract_id(entry: Dict[str, Any]) -> str:
    """Returns the normalized string add-on ID from a v4 or legacy filelist entry."""
    return str(entry.get("id") or entry.get("UID") or entry.get("addon_id") or "").strip()


def _extract_title(entry: Dict[str, Any]) -> str:
    """Returns the add-on title from a filelist entry."""
    return str(entry.get("title") or entry.get("UIName") or entry.get("name") or "").strip()


def _extract_author(entry: Dict[str, Any]) -> str:
    """Returns the author name from a filelist entry."""
    return str(entry.get("author") or entry.get("UIAuthorName") or entry.get("authorName") or "").strip()


def _extract_version(entry: Dict[str, Any]) -> str:
    """Returns the display version string from a filelist entry."""
    return str(entry.get("version") or entry.get("UIVersion") or "").strip()


def extract_primary_api_version(entry: Dict[str, Any]) -> str:
    """
    Liefert ausschließlich die APIVersion des Haupt-Addons aus entry['addons']
    (ignoriert eingebettete Sub-Addons / mitgelieferte Libraries in Unterordnern).
    """
    sub_addons = entry.get("addons")
    if isinstance(sub_addons, list) and sub_addons:
        valid_subs = [s for s in sub_addons if isinstance(s, dict) and str(s.get("apiVersion") or "").strip()]
        if valid_subs:
            pkg_title_clean = re.sub(r"[^a-z0-9]", "", _extract_title(entry).lower())
            pkg_is_lib = bool(entry.get("library"))

            def _score(sub: Dict[str, Any]) -> Tuple[int, int, int]:
                raw_path = str(sub.get("path") or "").replace("\\", "/").strip("/")
                is_root_folder = 0 if "/" not in raw_path else 1
                sub_is_lib = bool(sub.get("library"))
                lib_mismatch = 0 if (pkg_is_lib or not sub_is_lib) else 1
                path_clean = re.sub(r"[^a-z0-9]", "", raw_path.lower())
                title_match = 0 if (pkg_title_clean and (path_clean in pkg_title_clean or pkg_title_clean in path_clean)) else 1
                return (is_root_folder, lib_mismatch, title_match)

            best_sub = min(valid_subs, key=_score)
            return str(best_sub.get("apiVersion") or "").strip()

    for key in ("apiversion", "apiVersion", "compatible", "compatibility"):
        val = entry.get(key)
        if isinstance(val, list):
            return ", ".join(str(x) for x in val if x is not None)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def _extract_api_version(entry: Dict[str, Any]) -> str:
    """Alias for extract_primary_api_version()."""
    return extract_primary_api_version(entry)


def _extract_last_update(entry: Dict[str, Any]) -> int:
    """Returns the Unix timestamp (ms) of the add-on's last update."""
    val = entry.get("lastUpdate") or entry.get("lastupdate") or entry.get("UIDate") or 0
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _is_live_addon(entry: Dict[str, Any]) -> bool:
    """Returns True if the add-on status is 'Live' (excluding archived/unapproved entries)."""
    status = str(entry.get("addonStatus") or entry.get("status") or entry.get("state") or "Live").strip().lower()
    return status == "live"


# MMOUI category ID for 'Discontinued & Outdated' add-ons
DISCONTINUED_OUTDATED_CATEGORY_IDS = {157}


def is_discontinued_or_outdated(entry: Dict[str, Any]) -> bool:
    """Returns True if the MMOUI v4 entry belongs to the 'Discontinued & Outdated' category (categoryId 157)."""
    raw_cat_id = entry.get("categoryId")
    if raw_cat_id is not None:
        try:
            if int(str(raw_cat_id).strip()) in DISCONTINUED_OUTDATED_CATEGORY_IDS:
                return True
        except ValueError:
            pass

    cat_vals = []
    for key in ("category", "categoryName", "catName"):
        val = entry.get(key)
        if val is not None:
            cat_vals.append(str(val).lower())
    combined = " ".join(cat_vals)
    return ("discontinued" in combined) or ("outdated" in combined)


def lookup_addon_metadata(
    addon_id: str | int,
    filelist: Optional[List[Dict[str, Any]]] = None,
    force: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Sucht ein Addon anhand seiner ID und liefert normalisierte Metadaten zurück.
    """
    target_id = str(addon_id).strip()
    items = filelist if filelist is not None else get_filelist(force=force)
    for entry in items:
        if _extract_id(entry) == target_id:
            return {
                "addon_id": target_id,
                "title": _extract_title(entry),
                "author": _extract_author(entry),
                "version": _extract_version(entry),
                "api_version": _extract_api_version(entry),
                "last_update": _extract_last_update(entry),
                "raw": entry,
            }
    return None
def get_last_updated_addons(
    spec: str = "1-20",
    limit: int = 200,
    filelist: Optional[List[Dict[str, Any]]] = None,
    force: bool = False,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Filtert 'Live'-Addons, sortiert nach lastUpdate absteigend (Top `limit`),
    und wählt daraus die Einträge gemäß `spec` (z. B. '1-5, 8, 10-12') aus.
    Rückgabe: (selected_items, top_ranked_items)
    """
    items = filelist if filelist is not None else get_filelist(force=force)
    live_items = [item for item in items if _is_live_addon(item)]
    live_items.sort(key=_extract_last_update, reverse=True)
    top_items = live_items[:limit]

    if not spec or not spec.strip():
        return top_items, top_items

    indices = parse_selection_spec(spec, len(top_items))
    selected = [top_items[i - 1] for i in indices]
    return selected, top_items


def _compile_three_stage_patterns(query: str) -> List[Tuple[int, re.Pattern[str]]]:
    """
    Erzeugt bis zu 3 Regex-Stufen für Queries mit '+':
      Stufe 1: Regex unverändert (inkl. '+' als Quantifier)
      Stufe 2: '+' durch literales '\\+' ersetzt
      Stufe 3: '+' durch Wildcard '.*' ersetzt
    """
    q = query.strip()
    candidates: List[Tuple[int, str]] = [(1, q)]
    if "+" in q:
        candidates.append((2, q.replace("+", r"\+")))
        candidates.append((3, q.replace("+", ".*")))

    compiled: List[Tuple[int, re.Pattern[str]]] = []
    seen_patterns = set()
    for stage, pat_str in candidates:
        if pat_str in seen_patterns:
            continue
        try:
            rx = re.compile(pat_str, re.IGNORECASE)
            seen_patterns.add(pat_str)
            compiled.append((stage, rx))
        except re.error:
            continue
    return compiled


def _entry_dependencies_text(entry: Dict[str, Any]) -> str:
    """Concatenates all required and optional dependency tokens of a filelist entry for search matching."""
    tokens: List[str] = []
    sub_addons = entry.get("addons")
    if isinstance(sub_addons, list):
        for sub in sub_addons:
            if not isinstance(sub, dict):
                continue
            for key in ("requiredDependencies", "optionalDependencies"):
                dep_list = sub.get(key)
                if isinstance(dep_list, list):
                    tokens.extend(str(d) for d in dep_list if d)
    for key in ("dependencies", "depends", "required"):
        deps = entry.get(key)
        if isinstance(deps, list):
            tokens.extend(str(d) for d in deps if d)
        elif deps:
            tokens.append(str(deps))
    return " ".join(tokens)


def search_addons(
    queries_csv: str,
    search_mode: str = "all",
    dep_mode: bool = False,
    filelist: Optional[List[Dict[str, Any]]] = None,
    force: bool = False,
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Sucht Addons per kommagetrennten Suchbegriffen (OR-Verknüpfung über Begriffe):
      - search_mode='all': Titel, Autor & ID
      - search_mode='dep' (oder dep_mode=True): Dependencies
      - search_mode='author': Ausschließlich Autor
      - search_mode='api': API-Version (unterstützt auch '!101043' für veraltete Addons)
    Nutzt den 3-stufigen '+'-Fallback und gibt (Trefferliste, genutzte_Stufe) zurück.
    """
    mode = "dep" if dep_mode else (search_mode or "all").strip().lower()
    if mode not in ("all", "dep", "author", "api"):
        raise ValueError(f"Unbekannter Suchmodus: '{mode}' (erlaubt: all, dep, author, api)")

    terms = [t.strip() for t in queries_csv.split(",") if t.strip()]
    if not terms:
        return [], 1

    items = filelist if filelist is not None else get_filelist(force=force)
    live_items = [item for item in items if _is_live_addon(item)]

    if mode == "api":
        matches: List[Dict[str, Any]] = []
        for entry in live_items:
            api_text = _extract_api_version(entry)
            api_tokens = {tok.strip() for tok in re.split(r'[,\s]+', api_text) if tok.strip()}
            matched_any = False
            for term in terms:
                if term.startswith("!"):
                    neg_val = term.lstrip("!").strip()
                    if neg_val and neg_val not in api_tokens:
                        matched_any = True
                        break
                else:
                    if term in api_tokens or term in api_text:
                        matched_any = True
                        break
            if matched_any:
                matches.append(entry)
        matches.sort(key=_extract_last_update, reverse=True)
        return matches, 1
    stage_buckets: Dict[int, List[re.Pattern[str]]] = {1: [], 2: [], 3: []}
    for term in terms:
        for stage, rx in _compile_three_stage_patterns(term):
            stage_buckets[stage].append(rx)

    for stage in (1, 2, 3):
        patterns = stage_buckets.get(stage, [])
        if not patterns:
            continue
        matches = []
        for entry in live_items:
            if mode == "dep":
                haystack = _entry_dependencies_text(entry)
            elif mode == "author":
                haystack = _extract_author(entry)
            else:
                haystack = f"{_extract_title(entry)} {_extract_author(entry)} {_extract_id(entry)}"
            if any(rx.search(haystack) for rx in patterns):
                matches.append(entry)
        if matches:
            matches.sort(key=_extract_last_update, reverse=True)
            return matches, stage

    return [], 3


def select_search_results(results: Sequence[Dict[str, Any]], selection_spec: str) -> List[Dict[str, Any]]:
    """
    Wählt aus einer Suchergebnisliste Einträge anhand einer Nummern-Auswahl ('1', '1-3', '2, 5') aus.
    """
    indices = parse_selection_spec(selection_spec, len(results))
    return [results[i - 1] for i in indices]


def _parse_numeric_addon_version(raw_val: Any) -> Optional[int]:
    """Parst ein v4-'addOnVersion'-Feld (z. B. '43', '350', '0901') in eine Ganzzahl."""
    if raw_val is None:
        return None
    clean = str(raw_val).strip().lstrip("\ufeff")
    if not clean:
        return None
    if clean.isdigit():
        return int(clean)
    digits = re.sub(r"\D", "", clean)
    return int(digits) if digits else None


def lookup_dependency_addon_version(
    dep_name: str,
    filelist: Optional[List[Dict[str, Any]]] = None,
) -> Optional[int]:
    """
    Sucht eine Dependency in der MMOUI v4 filelist.json über sub['path'] / dir / name / title
    und liefert deren exakte numerische 'addOnVersion' / 'addonVersion' zurück
    (oder None, falls leer/nicht gesetzt -> [AddOnVersion unknown]).
    """
    target = dep_name.strip().lower()
    if not target:
        return None
    try:
        items = filelist if filelist is not None else get_filelist(force=False)
    except Exception:
        return None

    fallback_title_ver: Optional[int] = None

    for entry in items:
        if not _is_live_addon(entry):
            continue
        sub_addons = entry.get("addons")
        if isinstance(sub_addons, list):
            for sub in sub_addons:
                if not isinstance(sub, dict):
                    continue
                candidates = set()
                for key in ("path", "dir", "folder", "name", "manifest"):
                    raw_id = str(sub.get(key) or "").replace("\\", "/").strip().lower()
                    if raw_id:
                        stem = os.path.splitext(raw_id)[0]
                        candidates.add(raw_id)
                        candidates.add(stem)
                        candidates.add(raw_id.rsplit("/", 1)[-1])
                        candidates.add(stem.rsplit("/", 1)[-1])
                if target in candidates:
                    ver = _parse_numeric_addon_version(
                        sub.get("addOnVersion") if sub.get("addOnVersion") is not None else sub.get("addonVersion")
                    )
                    if ver is not None:
                        return ver
        raw_title = _extract_title(entry).lower()
        entry_ver = _parse_numeric_addon_version(
            entry.get("addOnVersion") if entry.get("addOnVersion") is not None else entry.get("addonVersion")
        )
        if entry_ver is None and isinstance(sub_addons, list):
            for sub in sub_addons:
                if isinstance(sub, dict):
                    entry_ver = _parse_numeric_addon_version(
                        sub.get("addOnVersion") if sub.get("addOnVersion") is not None else sub.get("addonVersion")
                    )
                    if entry_ver is not None:
                        break

        if raw_title == target and entry_ver is not None:
            return entry_ver
        if fallback_title_ver is None and entry_ver is not None:
            title_base = re.split(r"\s+[-–:|(]\s*", raw_title, maxsplit=1)[0].strip()
            if title_base == target:
                fallback_title_ver = entry_ver

    return fallback_title_ver


def is_standalone_online_addon(
    dep_name: str,
    filelist: Optional[List[Dict[str, Any]]] = None,
) -> bool:
    """Returns True if dep_name exists as a standalone (non-embedded) Live add-on/library in filelist.json."""
    pkg = resolve_dependency_online_package(dep_name, filelist=filelist)
    return bool(pkg and not pkg.get("is_embedded"))


def annotate_depends_on_line(
    raw_line: str,
    filelist: Optional[List[Dict[str, Any]]] = None,
    bundled_internal_deps: Optional[Sequence[str]] = None,
) -> Tuple[str, bool, bool]:
    """
    Annotiert alle Dependencies in einer '## DependsOn:'-Zeile anhand der v4 filelist.json:
      ## DependsOn: LibAddonMenu-2.0>=38 [current: 43] LibFilters-3.0 [current: 350] LibWhatever [AddOnVersion unknown]
    Gibt (annotierte_zeile, has_missing_required_ver, has_outdated_ver) zurück.
    """
    lb, rb = chr(91), chr(93)
    stripped = raw_line.strip()
    if ":" not in stripped:
        return stripped, False, False

    header, rhs = stripped.split(":", 1)
    tokens = rhs.split()
    annotated_tokens: List[str] = []
    has_missing = False
    has_outdated = False
    bundled_lower = {d.strip().lower() for d in (bundled_internal_deps or ()) if d and d.strip()}

    for token in tokens:
        if ">=" in token:
            dep_name, ver_part = token.split(">=", 1)
            dep_name = dep_name.strip()
            ver_digits = re.sub(r"\D", "", ver_part)
            declared_ver = int(ver_digits) if ver_digits else None
            has_ge = True
        else:
            dep_name = token.strip()
            declared_ver = None
            has_ge = False

        if not has_ge and dep_name.lower() in bundled_lower:
            annotated_tokens.append(token)
            continue

        latest_ver = lookup_dependency_addon_version(dep_name, filelist=filelist)
        if latest_ver is not None:
            entry_str = f"{token} {lb}current: {latest_ver}{rb}"
            if not has_ge:
                has_missing = True
                annotated_tokens.append(f'{lb}color="Red"{rb}{entry_str}{lb}/color{rb}')
            elif declared_ver is not None and declared_ver < latest_ver:
                has_outdated = True
                annotated_tokens.append(f'{lb}color="Red"{rb}{entry_str}{lb}/color{rb}')
            else:
                annotated_tokens.append(token)
        else:
            annotated_tokens.append(f"{token} {lb}AddOnVersion unknown{rb}")

    return f"{header.strip()}: {' '.join(annotated_tokens)}", has_missing, has_outdated


def _version_to_tuple(ver_val: Any) -> Tuple[int, ...]:
    """Wandelt nur reine Zahlen ('43') oder punktgetrennte Versionen ('3.8.34') in ein Zahlen-Tupel um."""
    if ver_val is None:
        return ()
    if isinstance(ver_val, int):
        return (ver_val,)
    clean = str(ver_val).strip()
    if not re.match(r"^\d+(?:\.\d+)*$", clean):
        return ()
    return tuple(int(part) for part in clean.split("."))
def compare_version_values(local_ver: Any, remote_ver: Any) -> int:
    """
    Vergleicht zwei Versionswerte:
    Numerisch nur bei Ganzzahlen ('43') oder rein punktgetrennten Nummern ('3.8.34').
    Bei Freitext-Versionen ('2.0 r43') wird 0 zurückgegeben (kein Raten).
    """
    if isinstance(local_ver, int) and isinstance(remote_ver, int):
        return -1 if local_ver < remote_ver else (1 if local_ver > remote_ver else 0)
    t_loc = _version_to_tuple(local_ver)
    t_rem = _version_to_tuple(remote_ver)
    if t_loc and t_rem:
        max_len = max(len(t_loc), len(t_rem))
        p_loc = t_loc + (0,) * (max_len - len(t_loc))
        p_rem = t_rem + (0,) * (max_len - len(t_rem))
        return -1 if p_loc < p_rem else (1 if p_loc > p_rem else 0)
    return 0


def resolve_dependency_online_package(
    dep_name: str,
    filelist: Optional[List[Dict[str, Any]]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Sucht alle Live-Pakete in der MMOUI v4 filelist.json, die `dep_name` entweder als
    eigenständiges Addon oder als eingebettete Library (z. B. 'MasterMerchant/Libs/LibGuildStore')
    enthalten, und wählt den Eintrag mit der höchsten Version (bei Gleichstand Standalone bevorzugt).
    """
    target = dep_name.strip().lower()
    if not target:
        return None
    try:
        items = filelist if filelist is not None else get_filelist(force=False)
    except Exception:
        return None

    candidates: List[Tuple[int, Tuple[int, ...], int, int, Dict[str, Any]]] = []

    from src.esoui_config import EXCLUDED_EMBEDDED_DEPENDENCY_ADDONS

    for entry in items:
        if not _is_live_addon(entry) or is_discontinued_or_outdated(entry):
            continue
        addon_id = _extract_id(entry)
        if not addon_id:
            continue
        pkg_title = _extract_title(entry)
        skip_embedded_for_pkg = (
            addon_id.lower() in EXCLUDED_EMBEDDED_DEPENDENCY_ADDONS
            or pkg_title.lower() in EXCLUDED_EMBEDDED_DEPENDENCY_ADDONS
        )
        pkg_ver_str = _extract_version(entry)
        pkg_addon_ver = _parse_numeric_addon_version(
            entry.get("addOnVersion") if entry.get("addOnVersion") is not None else entry.get("addonVersion")
        )
        sub_addons = entry.get("addons")
        matched_sub = False

        if isinstance(sub_addons, list):
            for sub in sub_addons:
                if not isinstance(sub, dict):
                    continue
                raw_path = str(sub.get("path") or sub.get("dir") or sub.get("folder") or "").replace("\\", "/").strip("/")
                names_to_check = set()
                for key in ("path", "dir", "folder", "name", "manifest"):
                    raw_id = str(sub.get(key) or "").replace("\\", "/").strip("/").lower()
                    if raw_id:
                        stem = os.path.splitext(raw_id)[0]
                        names_to_check.add(raw_id)
                        names_to_check.add(stem)
                        names_to_check.add(raw_id.rsplit("/", 1)[-1])
                        names_to_check.add(stem.rsplit("/", 1)[-1])

                if target in names_to_check:
                    sub_path = raw_path if raw_path else dep_name.strip()
                    is_embedded = "/" in sub_path
                    if is_embedded and skip_embedded_for_pkg:
                        continue
                    matched_sub = True
                    sub_ver = _parse_numeric_addon_version(
                        sub.get("addOnVersion") if sub.get("addOnVersion") is not None else sub.get("addonVersion")
                    )
                    eff_num_ver = sub_ver if sub_ver is not None else pkg_addon_ver
                    has_num_av = 1 if eff_num_ver is not None else 0
                    ver_tuple = (eff_num_ver,) if eff_num_ver is not None else _version_to_tuple(pkg_ver_str)
                    standalone_bonus = 0 if is_embedded else 1
                    has_ver_bonus = 1 if ver_tuple else 0
                    info = {
                        "addon_id": addon_id,
                        "title": pkg_title,
                        "add_on_version": eff_num_ver,
                        "version_str": pkg_ver_str,
                        "sub_path": sub_path,
                        "is_embedded": is_embedded,
                    }
                    candidates.append((has_num_av, ver_tuple, standalone_bonus, has_ver_bonus, info))

        if not matched_sub:
            raw_title = pkg_title.lower()
            title_base = re.split(r"\s+[-–:|(]\s*", raw_title, maxsplit=1)[0].strip()
            if raw_title == target or title_base == target:
                has_num_av = 1 if pkg_addon_ver is not None else 0
                ver_tuple = (pkg_addon_ver,) if pkg_addon_ver is not None else _version_to_tuple(pkg_ver_str)
                has_ver_bonus = 1 if ver_tuple else 0
                info = {
                    "addon_id": addon_id,
                    "title": pkg_title,
                    "add_on_version": pkg_addon_ver,
                    "version_str": pkg_ver_str,
                    "sub_path": dep_name.strip(),
                    "is_embedded": False,
                }
                candidates.append((has_num_av, ver_tuple, 1, has_ver_bonus, info))

    if not candidates:
        return None

    candidates.sort(
        key=lambda item: (item.__getitem__(2), item.__getitem__(0), item.__getitem__(1), item.__getitem__(3)),
        reverse=True,
    )
    _, _, _, _, best_info = next(iter(candidates))
    return best_info
