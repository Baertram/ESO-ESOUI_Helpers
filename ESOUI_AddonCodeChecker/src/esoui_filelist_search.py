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

FILELIST_URL = "https://api.mmoui.com/v3/game/ESO/filelist.json"
DEFAULT_CACHE_PATH = Path("Cache") / "filelist.json"
CACHE_TTL_SECONDS = 15 * 60  # 15 Minuten

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
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "esoui_codecheck/1.0 (+https://github.com)"},
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
    return str(entry.get("id") or entry.get("UID") or entry.get("addon_id") or "").strip()


def _extract_title(entry: Dict[str, Any]) -> str:
    return str(entry.get("title") or entry.get("name") or "").strip()


def _extract_author(entry: Dict[str, Any]) -> str:
    return str(entry.get("author") or entry.get("authorName") or "").strip()


def _extract_version(entry: Dict[str, Any]) -> str:
    return str(entry.get("version") or "").strip()


def _extract_api_version(entry: Dict[str, Any]) -> str:
    for key in ("apiversion", "apiVersion", "compatible", "compatibility"):
        val = entry.get(key)
        if isinstance(val, list):
            return ", ".join(str(x) for x in val if x is not None)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def _extract_last_update(entry: Dict[str, Any]) -> int:
    val = entry.get("lastUpdate") or entry.get("lastupdate") or 0
    try:
        return int(val)
    except (TypeError, ValueError):
        return 0


def _is_live_addon(entry: Dict[str, Any]) -> bool:
    status = str(entry.get("status") or entry.get("state") or "Live").strip().lower()
    return status == "live"


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
    deps = entry.get("dependencies") or entry.get("depends") or entry.get("required") or []
    if isinstance(deps, list):
        return " ".join(str(d) for d in deps if d is not None)
    return str(deps or "")


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
