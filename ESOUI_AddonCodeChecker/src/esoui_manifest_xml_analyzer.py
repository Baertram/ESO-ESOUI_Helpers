"""
Statische Validierung für ESO-Manifeste (.addon / .txt), XML-Schemas (XSD) und Inline-Lua in XML.
"""

import os
import re

from src.esoui_config import (
    C,
    ESO_BINDINGS_SCHEMA_FILE,
    ESO_XML_SCHEMA_FILE,
    EXTRACT_FOLDER,
    NON_LANG_TWO_LETTER_STEMS,
    resolve_config_file_path,
)
from src.esoui_config import CACHE_ADDONS_EXTRACTED_DIR, ESO_ADDONS_DIR
from src.esoui_filelist_search import (
    annotate_depends_on_line,
    is_standalone_online_addon,
    resolve_dependency_online_package,
)
from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

from src.esoui_ram_index import (
    ESOUI_RAM_DICTIONARY,
    ESOUI_UNDOCUMENTED_SET,
    build_esoui_index_once,
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


def _check_manifest_line_lengths(content, manifest_issues):
    for line_num, line in enumerate(content.splitlines(), 1):
        byte_len = len(line.encode("utf-8"))
        if byte_len > 301:
            manifest_issues.append(
                f"Manifest line {line_num} exceeds 301 bytes ({byte_len} bytes). ESO truncates or ignores lines longer than 301 bytes."
            )


def _is_unique_addon_identifier(ident_name, addon_ctx=None, fallback_stem=None):
    """Returns True if ident_name is >= 6 chars and clearly anchored to the addon/manifest/global-table name."""
    if not ident_name or len(ident_name) < 6:
        return False
    norm_id = re.sub(r"[^a-z0-9]", "", ident_name.lower())
    if len(norm_id) < 6:
        return False

    anchors = set()
    if fallback_stem:
        anchors.add(fallback_stem)
    if addon_ctx:
        for mf in (addon_ctx.get("root_addon_manifests") or []) + (addon_ctx.get("root_txt_manifests") or []):
            anchors.add(os.path.splitext(os.path.basename(mf))[0])
        for gt in (addon_ctx.get("all_global_tables") or ()):
            if len(gt) >= 6:
                anchors.add(gt)

    norm_anchors = set()
    for anc in anchors:
        clean_a = re.sub(r"[^a-z0-9]", "", str(anc).lower())
        if len(clean_a) >= 4:
            norm_anchors.add(clean_a)
            stripped_digits = re.sub(r"\d+$", "", clean_a)
            if len(stripped_digits) >= 4:
                norm_anchors.add(stripped_digits)

    return any(anc in norm_id for anc in norm_anchors)


def _check_manifest_saved_variables(file_name, line_num, line_str, manifest_issues, addon_ctx=None):
    """Flags SavedVariables that are shorter than 6 chars or lack the addon/global-table name."""
    m_sv = re.match(r"^##\s*SavedVariables\s*:\s*(.+)$", line_str, flags=re.IGNORECASE)
    if not m_sv:
        return
    sv_rhs = re.split(r"[#;]", m_sv.group(1), maxsplit=1)[0]
    sv_names = re.findall(r"\b([A-Za-z_][A-Za-z0-9_]*)\b", sv_rhs)
    if not sv_names:
        return
    manifest_stem = os.path.splitext(os.path.basename(file_name))[0]
    bad_vars = [sv for sv in sv_names if not _is_unique_addon_identifier(sv, addon_ctx=addon_ctx, fallback_stem=manifest_stem)]
    if bad_vars:
        manifest_issues.append(
            f"Non-unique / too short SavedVariables (use e.g. <AddonName>_SV): {', '.join(bad_vars)} (line {line_num}): (-- {line_str})"
        )


def _check_manifest_folder_match(file_name, manifest_issues):
    parts = file_name.replace("\\", "/").split("/")
    if len(parts) >= 2:
        parent_folder = parts[-2]
        manifest_base, _ = os.path.splitext(parts[-1])
        if parent_folder != manifest_base:
            manifest_issues.append(
                f"Manifest Filename Mismatch: Manifest '{parts[-1]}' does not match its parent folder name '{parent_folder}' (case-sensitive!)."
            )

def _check_manifest_dependencies(line_num, line_str, manifest_issues, manifest_suggestions, addon_ctx=None):
    bundled_subs = set((addon_ctx or {}).get("bundled_sub_addons") or ())
    for tag in ["DependsOn", "PCDependsOn", "ConsoleDependsOn"]:
        if line_str.startswith("## " + tag + ":") or line_str.startswith("## " + tag + " "):
            if ":" in line_str:
                _, dep_raw = line_str.split(":", 1)
                dep_part = dep_raw.strip()
                if "," in dep_part or ";" in dep_part:
                    manifest_issues.append(
                        f"Invalid delimiter in {tag} (line {line_num}): Use spaces instead of commas or semicolons (-- {line_str})."
                    )
                internal_only = [
                    next(iter(tok.split(">=", 1))).strip()
                    for tok in dep_part.split()
                    if ">=" not in tok
                    and tok.strip().lower() in bundled_subs
                    and not is_standalone_online_addon(tok.strip())
                ]
                annotated_line, has_missing, has_outdated = annotate_depends_on_line(
                    line_str, bundled_internal_deps=internal_only
                )
                if has_missing:
                    manifest_issues.append(
                        f"Mandatory version check >= missing for non-optional dependency (line {line_num}): ({annotated_line})"
                    )
                if has_outdated:
                    manifest_suggestions.append(
                        f"Mandatory version check >= outdated - consider an update (line {line_num}): ({annotated_line})"
                    )
                for tok in dep_part.split():
                    dep_clean = next(iter(tok.split(">=", 1))).strip()
                    if not dep_clean or dep_clean.lower() in bundled_subs:
                        continue
                    in_live = os.path.isdir(os.path.join(ESO_ADDONS_DIR, dep_clean))
                    in_cache = os.path.isdir(os.path.join(CACHE_ADDONS_EXTRACTED_DIR, dep_clean))
                    in_online = resolve_dependency_online_package(dep_clean) is not None
                    if not in_live and not in_cache and not in_online:
                        manifest_issues.append(
                            f"Non-existent dependency '{dep_clean}' (not found in ZIP, live/AddOns, Cache, or ESOUI) (line {line_num}): (-- {line_str})"
                        )


    if line_str.startswith("## OptionalDependsOn:") or line_str.startswith("## OptionalDependsOn "):
        if ":" in line_str:
            _, opt_raw = line_str.split(":", 1)
            opt_part = opt_raw.strip()
            if "," in opt_part or ";" in opt_part:
                manifest_issues.append(
                    f"Invalid delimiter in OptionalDependsOn (line {line_num}): Use spaces instead of commas or semicolons (-- {line_str})."
                )
            bad_opt_deps = [dep for dep in opt_part.split() if ">=" in dep]
            if bad_opt_deps:
                manifest_issues.append(
                    f"Invalid '>=' operator in OptionalDependsOn (line {line_num}): Version checks are NOT supported here (-- {' '.join(bad_opt_deps)})."
                )

def analyze_manifest_file(file_name, content, ext, addon_ctx):
    manifest_issues = []
    manifest_suggestions = []
    current_api = get_current_api_version()
    detected_api_line = None

    _check_manifest_line_lengths(content, manifest_issues)
    _check_manifest_folder_match(file_name, manifest_issues)

    for line_num, line in enumerate(content.splitlines(), 1):
        line_str = line.strip()
        if not line_str.startswith("##"):
            continue
        if re.match(r'^##\s*SavedVariablesPerCharacter\s*:', line_str, flags=re.IGNORECASE):
            manifest_issues.append(
                f"Non supported SavedVariable definition (line {line_num}): Use '## SavedVariables:' instead (-- {line_str})."
            )
        _check_manifest_saved_variables(file_name, line_num, line_str, manifest_issues, addon_ctx=addon_ctx)
        if ":" in line_str:
            left_part, _ = line_str.split(":", 1)
            if left_part.endswith(" "):
                manifest_issues.append(
                    f"Invalid space before colon in manifest tag (line {line_num}): (-- {line_str})"
                )

        if line_str.startswith("## APIVersion:"):
            _, api_raw = line_str.split(":", 1)
            api_part = api_raw.strip()
            detected_api_line = api_part
            api_versions = api_part.split()
            if not api_versions or any(not v.isdigit() for v in api_versions):
                manifest_issues.append(
                    f"Invalid APIVersion syntax (line {line_num}): APIVersion must contain valid numerical API versions (-- {line_str})."
                )
                continue
            if len(api_versions) > 2:
                manifest_issues.append(
                    f"Invalid APIVersion count (line {line_num}): Maximum of TWO API versions is allowed (-- {line_str})."
                )
            if current_api and (current_api not in api_versions):
                manifest_issues.append(
                    f"Outdated APIVersion (missing current live API {current_api}) (line {line_num}): (-- {line_str})"
                )

        _check_manifest_dependencies(line_num, line_str, manifest_issues, manifest_suggestions, addon_ctx=addon_ctx)

    if detected_api_line is not None:
        print(f"    ├── Detected ## APIVersion: {detected_api_line} {C.CYAN}(Current Live API: {current_api or 'Unknown'}){C.RESET}")

    explicit_dds_lines = []
    lang_code_candidates = []
    for raw_line in content.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith(("#", ";")):
            continue
        if stripped.lower().endswith(".dds"):
            explicit_dds_lines.append(stripped)
            continue
        norm_entry = stripped.replace("\\", "/")
        base_file = norm_entry.rsplit("/", 1)[-1]
        stem, f_ext = os.path.splitext(base_file)
        if f_ext.lower() in (".lua", ".xml") and re.match(r"^[A-Za-z]{2}$", stem) and stem.lower() not in NON_LANG_TWO_LETTER_STEMS:
            dir_part = norm_entry.rsplit("/", 1)[0].lower() if "/" in norm_entry else ""
            lang_code_candidates.append((dir_part, stripped))

    # Flag if > 1 fixed 2-letter language file is hardcoded in the same directory (or across translation folders)
    by_lang_dir = {}
    for d_part, orig_entry in lang_code_candidates:
        by_lang_dir.setdefault(d_part, []).append(orig_entry)

    hardcoded_lang_lines = []
    for d_part, entries_in_dir in by_lang_dir.items():
        if len(entries_in_dir) > 1:
            hardcoded_lang_lines.extend(entries_in_dir)

    if hardcoded_lang_lines:
        print(f"    ├── {C.YELLOW}[Best Practice] Hardcoded language files detected ({len(hardcoded_lang_lines)}) - Use dynamic $(language):{C.RESET}")
        for lang_entry in hardcoded_lang_lines:
            print(f"    │     {C.YELLOW}- {lang_entry}{C.RESET}")
        manifest_suggestions.append(
            "Hardcoded language files - Use dynamic $(language): " + ", ".join(hardcoded_lang_lines)
        )

    if explicit_dds_lines:
        print(f"    ├── {C.ORANGE}[Not needed] Texture files loaded explicitly in manifest's lines ({len(explicit_dds_lines)}):{C.RESET}")
        for dds_entry in explicit_dds_lines:
            print(f"    │     {C.ORANGE}- {dds_entry}{C.RESET}")

    addon_manifests = addon_ctx["root_addon_manifests"]
    txt_manifests = addon_ctx["root_txt_manifests"]
    if addon_manifests and txt_manifests:
        manifest_issues.append(
            "Only 1 manifest file allowed! Use .txt for PC only, and .addon for Console addons (or which will properly work on PC's ForceConsoleFlow emulation too)"
        )
    elif ext == '.addon' and addon_manifests and not txt_manifests:
        addon_notice = (
            "Manifest .addon found: Please assure your addon was developed compatible with ESO's console UI, "
            "or else (if you only support the keyboard or gamepad UI on PC) use the .txt manifest extension "
            "-> This assures your addon never loads on PC's \"force console flow\" and thus does not raise any error or consume rare memory"
        )
        print(f"    ├── {C.YELLOW}[INFO]{C.RESET} {addon_notice}")
        manifest_suggestions.append(addon_notice)

    dds_report_block = ("\nExplicitly loaded texture files - Not needed\n" + "\n".join([f"  - {item}" for item in explicit_dds_lines])) if explicit_dds_lines else ""

    if manifest_issues:
        issues_str = "\n".join(["  - " + issue for issue in manifest_issues])
        sugg_str = "\n".join(["  - " + s for s in manifest_suggestions]) if manifest_suggestions else "None"
        return "[STATUS] FAIL\n[CRITICAL VIOLATIONS]\n" + issues_str + "\n[BEST PRACTICE SUGGESTIONS]\n" + sugg_str + dds_report_block
    if manifest_suggestions:
        return "[STATUS] PASS\n[CRITICAL VIOLATIONS] None\n[BEST PRACTICE SUGGESTIONS]\n" + "\n".join(["  - " + s for s in manifest_suggestions]) + dds_report_block
    return "[STATUS] PASS" + dds_report_block
def _get_xml_schema_validator(schema_setting):
    if not LXML_AVAILABLE or lxml_etree is None:
        if "lxml_missing" not in XML_SCHEMA_WARNED:
            print(f"{C.CYAN}       [INFO] Python library 'lxml' is not installed. Skipping XSD schema validation (install via: pip install lxml).{C.RESET}")
            XML_SCHEMA_WARNED.add("lxml_missing")
        return None
    resolved_path = resolve_config_file_path(schema_setting)
    if not resolved_path or not os.path.exists(resolved_path):
        if schema_setting not in XML_SCHEMA_WARNED:
            print(f"{C.CYAN}       [INFO] XSD schema file not found, skipping XSD validation: {resolved_path}{C.RESET}")
            XML_SCHEMA_WARNED.add(schema_setting)
        return None
    if resolved_path in XML_SCHEMA_CACHE:
        return XML_SCHEMA_CACHE[resolved_path]
    try:
        validator = lxml_etree.XMLSchema(lxml_etree.parse(resolved_path))
        XML_SCHEMA_CACHE[resolved_path] = validator
        return validator
    except Exception as e:
        if schema_setting not in XML_SCHEMA_WARNED:
            print(f"{C.RED}       [ERROR] Failed to parse XSD schema '{resolved_path}': {str(e)}{C.RESET}")
            XML_SCHEMA_WARNED.add(schema_setting)
        return None


def _extract_xml_inline_lua_leaks(content, addon_ctx):
    leaks = []
    if not is_index_built():
        build_esoui_index_once()
    allowed_globals = set(addon_ctx.get("all_global_tables", set())) | set(ESOUI_RAM_DICTIONARY.keys()) | ESOUI_UNDOCUMENTED_SET

    handler_pat = re.compile(r'<(On[A-Za-z0-9_]+|UpdateFunction|EasingFunction|Callback|Down|Up)\b[^>]*>(.*?)</\1>', flags=re.DOTALL)
    assign_pat = re.compile(r'^\s*(?!local\s)([A-Za-z_][A-Za-z0-9_]*)\s*=[^=]', flags=re.MULTILINE)
    func_def_pat = re.compile(r'^\s*(?!local\s)function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', flags=re.MULTILINE)

    raw_lines = content.splitlines()
    for match in handler_pat.finditer(content):
        tag_name, lua_snippet = str(match.group(1)), str(match.group(2))
        snippet_start_offset = match.start(2)
        declared_locals = {"self"}
        for decl in re.findall(r'\blocal\s+([A-Za-z_][A-Za-z0-9_]*(?:\s*,\s*[A-Za-z_][A-Za-z0-9_]*)*)', lua_snippet):
            for item in decl.split(","):
                if item.strip():
                    declared_locals.add(item.strip())
        for am in assign_pat.finditer(lua_snippet):
            var_name = str(am.group(1))
            if var_name not in declared_locals and var_name not in allowed_globals:
                abs_pos = snippet_start_offset + am.start(1)
                ln_no = content.count("\n", 0, abs_pos) + 1
                orig = raw_lines[ln_no - 1].strip() if (ln_no - 1) < len(raw_lines) else ""
                leaks.append(f"Inline XML Lua global variable leak in <{tag_name}> (line {ln_no}): (-- {orig})")
        for fm in func_def_pat.finditer(lua_snippet):
            fn_name = str(fm.group(1))
            if fn_name not in declared_locals and fn_name not in allowed_globals:
                abs_pos = snippet_start_offset + fm.start(1)
                ln_no = content.count("\n", 0, abs_pos) + 1
                orig = raw_lines[ln_no - 1].strip() if (ln_no - 1) < len(raw_lines) else ""
                leaks.append(f"Inline XML Lua global function leak in <{tag_name}> (line {ln_no}): (-- {orig})")
    return leaks

def analyze_xml_file(file_name, content, addon_ctx):
    is_bindings = (os.path.basename(file_name).lower() == "bindings.xml")
    schema_setting = ESO_BINDINGS_SCHEMA_FILE if is_bindings else ESO_XML_SCHEMA_FILE
    xml_issues = []

    if LXML_AVAILABLE and lxml_etree is not None:
        try:
            doc = lxml_etree.fromstring(content.encode("utf-8"), parser=lxml_etree.XMLParser(recover=False))
            validator = _get_xml_schema_validator(schema_setting)
            if validator is not None:
                if not validator.validate(doc):
                    grouped_xsd = {}
                    for err in validator.error_log:
                        err_ln = int(err.line) if getattr(err, "line", None) else 0
                        err_msg = str(err.message).strip()
                        grouped_xsd.setdefault(err_ln, [])
                        if err_msg not in grouped_xsd[err_ln]:
                            grouped_xsd[err_ln].append(err_msg)
                    for err_ln in sorted(grouped_xsd.keys()):
                        combined_msg = " | ".join(grouped_xsd[err_ln])
                        xml_issues.append(f"XSD Validation Error (line {err_ln}): ({combined_msg})")
                else:

                    print(f"    ├── {C.GREEN}XSD schema validation passed{C.RESET} ({os.path.basename(schema_setting)}).")
        except Exception as e:
            xml_issues.append(f"XML Syntax/Parse Error: {str(e)}")

    xml_issues.extend(_extract_xml_inline_lua_leaks(content, addon_ctx))
    if xml_issues:
        return "[STATUS] FAIL\n[CRITICAL VIOLATIONS]\n" + "\n".join(["  - " + issue for issue in xml_issues]) + "\n[BEST PRACTICE SUGGESTIONS] None"
    return content


def analyze_file_content(file_name, content, extract_dir=None, addon_ctx=None):
    """Dispatches a single extracted file to its appropriate static analyzer."""
    _, ext = os.path.splitext(file_name.lower())
    active_extract_dir = extract_dir if extract_dir is not None else EXTRACT_FOLDER
    if addon_ctx is None:
        addon_ctx = collect_addon_context(active_extract_dir)

    if file_name == "[ZIP ARCHIVE STRUCTURE]":
        return content
    if ext == '.lua':
        return analyze_lua_file(file_name, content, active_extract_dir, addon_ctx)
    if ext == '.xml':
        return analyze_xml_file(file_name, content, addon_ctx)
    if ext in ('.addon', '.txt'):
        return analyze_manifest_file(file_name, content, ext, addon_ctx)
    return content
