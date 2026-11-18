#!/usr/bin/env python3
"""
Smoke-Test für die modulare Struktur von esoui_codecheck.py, das MMOUI v4 filelist.json Schema,
das kompakte BBCode-Reporting und die persistente repeat-Historie.
Ausführung im Projekt-Hauptverzeichnis:
    python smoke_test.py
"""

import os
import tempfile
import unittest
from collections import defaultdict
from unittest.mock import patch


class TestEsouiModularSmoke(unittest.TestCase):
    def test_01_imports_and_config(self):
        import esoui_codecheck
        from src import (
            esoui_ai_and_report,
            esoui_config,
            esoui_download_io,
            esoui_filelist_search,
            esoui_lua_analyzer,
            esoui_manifest_xml_analyzer,
            esoui_ram_index,
        )

        self.assertTrue(hasattr(esoui_codecheck, "main_cli"))
        self.assertTrue(hasattr(esoui_ai_and_report, "process_addon"))
        self.assertTrue(hasattr(esoui_ram_index, "build_esoui_index_once"))
        self.assertTrue(hasattr(esoui_lua_analyzer, "analyze_lua_file"))
        self.assertTrue(hasattr(esoui_filelist_search, "annotate_depends_on_line"))
        self.assertTrue(hasattr(esoui_filelist_search, "extract_primary_api_version"))
        self.assertIn("/v4/game/ESO/filelist.json", esoui_filelist_search.FILELIST_URL)
        self.assertIn("/downloads/info", esoui_config.ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX)
        self.assertIn("/downloads/dl", esoui_config.ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX)
        self.assertIn("showthread.php?t=10790", esoui_config.ESOUI_UPLOAD_RULES_URL)
        self.assertIn("AddFilterForEvent#Filter_Types", esoui_config.ESOUI_WIKI_EVENT_FILTERS_URL)

    def test_02_download_io_parsers(self):
        from src.esoui_download_io import (
            is_authorized_esoui_url,
            parse_dl_command,
            parse_last_selection_spec,
        )

        self.assertEqual(parse_dl_command("dl 5026"), ["5026"])
        self.assertEqual(parse_dl_command("DL 123 456, 789"), ["123", "456", "789"])
        self.assertIsNone(parse_dl_command("dl abc"))

        ranks, err = parse_last_selection_spec("1-3, 5 10-11", 200)
        self.assertIsNone(err)
        self.assertEqual(ranks, list((1, 2, 3, 5, 10, 11)))

        _, err_oob = parse_last_selection_spec("201", 200)
        self.assertIsNotNone(err_oob)

        valid_url = "https://" + "://esoui.com"
        evil_url = "https://" + "://example.com"
        self.assertTrue(is_authorized_esoui_url(valid_url))
        self.assertFalse(is_authorized_esoui_url(evil_url))
    def _sample_v4_filelist(self):
        return [
            {
                "id": 7,
                "title": "LibAddonMenu-2.0",
                "author": "sirinsidiator",
                "version": "2.0 r43",
                "lastUpdate": 1778599485000,
                "addonStatus": "Live",
                "addons": [
                    {
                        "path": "LibAddonMenu-2.0",
                        "addOnVersion": "43",
                        "apiVersion": "101049 101050",
                        "library": True,
                        "optionalDependencies": ["LibStub", "LibDebugLogger"],
                    }
                ],
                "library": True,
            },
            {
                "id": 2343,
                "title": "LibFilters-3.0",
                "author": "Baertram",
                "version": "3.0r5.0",
                "lastUpdate": 1772019887000,
                "addonStatus": "Live",
                "addons": [
                    {
                        "path": "LibFilters-3.0",
                        "addOnVersion": "350",
                        "apiVersion": "101048 101049",
                        "library": True,
                    }
                ],
                "library": True,
            },
            {
                "id": 3586,
                "title": "FCO Accessibility",
                "author": "Baertram",
                "version": "2.3",
                "lastUpdate": 1791291956000,
                "addonStatus": "Live",
                "addons": [
                    {
                        "path": "FCOAccessibility",
                        "addOnVersion": "23",
                        "apiVersion": "101050 101051",
                        "library": False,
                        "requiredDependencies": ["LibAddonMenu-2.0>=43", "LibFilters-3.0>=350"],
                    },
                    {
                        "path": "FCOAccessibility/Libs/EmbeddedSubLib",
                        "addOnVersion": "1",
                        "apiVersion": "101048 101049",
                        "library": True,
                    },
                ],
                "library": False,
            },
        ]

    def test_03_v4_filelist_primary_api_and_depends_split(self):
        from src.esoui_filelist_search import (
            annotate_depends_on_line,
            extract_primary_api_version,
            get_last_updated_addons,
            is_discontinued_or_outdated,
            lookup_addon_metadata,
            search_addons,
        )

        sample_v4 = self._sample_v4_filelist()
        selected, top = get_last_updated_addons(spec="1-2", filelist=sample_v4)
        self.assertEqual(len(top), 3)
        self.assertEqual([str(x["id"]) for x in selected], ["3586", "7"])

        meta = lookup_addon_metadata("3586", filelist=sample_v4)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["api_version"], "101050 101051")
        self.assertEqual(extract_primary_api_version(sample_v4[-1]), "101050 101051")

        hits_author, _ = search_addons("Baertram", search_mode="author", filelist=sample_v4)
        self.assertEqual([str(x["id"]) for x in hits_author], ["3586", "2343"])

        line_missing, has_missing, has_outdated = annotate_depends_on_line(
            "## DependsOn: LibAddonMenu-2.0>=43 LibFilters-3.0 LibWhatever",
            filelist=sample_v4,
        )
        self.assertTrue(has_missing)
        self.assertFalse(has_outdated)
        self.assertIn("LibFilters-3.0 [current: 350]", line_missing)
        self.assertIn("LibWhatever [AddOnVersion unknown]", line_missing)

        line_outdated, has_missing2, has_outdated2 = annotate_depends_on_line(
            "## DependsOn: LibAddonMenu-2.0>=38",
            filelist=sample_v4,
        )
        self.assertFalse(has_missing2)
        self.assertTrue(has_outdated2)
        self.assertIn("LibAddonMenu-2.0>=38 [current: 43]", line_outdated)

        self.assertTrue(is_discontinued_or_outdated({"id": 3864, "title": "pChat Gamepad", "categoryId": 157}))
        self.assertFalse(is_discontinued_or_outdated({"id": 630, "title": "FCO ItemSaver", "categoryId": 24}))
    def test_04_analyzers_leaks_and_grouped_bbcode_report(self):
        from src import esoui_filelist_search, esoui_ram_index
        from src.esoui_ai_and_report import (
            _build_bbcode_zip_list,
            _parse_findings_into_report_data,
            _render_final_bbcode_report,
        )
        from src.esoui_manifest_xml_analyzer import analyze_file_content

        sample_v4 = self._sample_v4_filelist()
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch.object(
            esoui_filelist_search, "get_filelist", return_value=sample_v4
        ), patch(
            "src.esoui_lua_analyzer.collect_dependency_globals", return_value={}
        ):
            ctx = {
                "has_bindings_xml": False,
                "xml_content": "",
                "all_global_tables": {"MyAddon"},
                "saved_variables": set(),
                "root_addon_manifests": ["MyAddon.addon"],
                "root_txt_manifests": [],
            }

            bad_lua = (
                "local function TestLeak()\n"
                "    leakedStatus = true\n"
                "    local a = next({})\n"
                "    local b = next({1})\n"
                "end\n"
            )
            res_lua = analyze_file_content("MyAddon/Core.lua", bad_lua, addon_ctx=ctx)
            self.assertIn("FAIL", res_lua)
            self.assertIn("Global Variable Pollution (missing 'local' for 'leakedStatus')", res_lua)

            bad_manifest = "## Title: MyAddon\n## DependsOn: LibAddonMenu-2.0>=38 LibFilters-3.0\n"
            res_man = analyze_file_content("MyAddon/MyAddon.addon", bad_manifest, addon_ctx=ctx)
            self.assertIn("FAIL", res_man)
            self.assertIn("Mandatory version check >= missing for non-optional dependency", res_man)
            self.assertIn("Mandatory version check >= outdated - consider an update", res_man)

            report_data = {
                "zip_all_entries": ["MyAddon/", "MyAddon/MyAddon.addon", "MyAddon/Core.lua", "MyAddon/Clean.lua"],
                "zip_flagged_paths": set(),
                "zip_manifest_paths": {"MyAddon/MyAddon.addon"},
                "zip_tree_bbcode": "",
                "zip_violations": [],
                "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                "best_practices": defaultdict(list),
            }
            _parse_findings_into_report_data("MyAddon/MyAddon.addon", "manifest", res_man, report_data)
            _parse_findings_into_report_data("MyAddon/Core.lua", "lua", res_lua, report_data)

            all_flagged = set(report_data["zip_flagged_paths"])
            for cat_rules in report_data["critical"].values():
                for entries in cat_rules.values():
                    for f_path, _, _ in entries:
                        all_flagged.add(f_path)
            report_data["zip_tree_bbcode"] = _build_bbcode_zip_list(
                report_data["zip_all_entries"],
                all_flagged,
                report_data["zip_manifest_paths"],
            )

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tmp_path = tf.name
            try:
                _render_final_bbcode_report(tmp_path, "MyAddon.zip", "2026-11-15 02:35:00 AM", report_data)
                with open(tmp_path, "r", encoding="utf-8") as rf:
                    rendered = rf.read()
                self.assertIn("MyAddon.addon [MANIFEST]", rendered)
                self.assertIn("Core.lua", rendered)
                self.assertNotIn(":mad: Clean.lua", rendered)
                self.assertIn("[b]next[/b] (used 2 times without local reference)", rendered)
                self.assertNotIn("[SIZE=\"2\"]-- ", rendered)
                pos_outdated = rendered.find("Mandatory version check >= outdated - consider an update")
                pos_next = rendered.find("Global variable used multiple times w/o a local reference")
                self.assertTrue(0 < pos_outdated < pos_next)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    def test_05_repeat_and_persistent_history(self):
        import esoui_codecheck

        with tempfile.TemporaryDirectory() as tmp_dir:
            hist_file = os.path.join(tmp_dir, "cmd_history.json")
            state = {"last_any": "dl 630", "last_dl": "dl 630", "last_search": "search author Baertram"}
            esoui_codecheck._save_cmd_history(state, history_path=hist_file)
            loaded = esoui_codecheck._load_cmd_history(history_path=hist_file)

            cmd_any, err_any = esoui_codecheck._resolve_repeat_command("repeat", loaded)
            self.assertIsNone(err_any)
            self.assertEqual(cmd_any, "dl 630")

            cmd_dl, err_dl = esoui_codecheck._resolve_repeat_command("repeat dl", loaded)
            self.assertIsNone(err_dl)
            self.assertEqual(cmd_dl, "dl 630")

            cmd_search, err_s = esoui_codecheck._resolve_repeat_command("repeat search", loaded)
            self.assertIsNone(err_s)
            self.assertEqual(cmd_search, "search author Baertram")

    def test_06_dependency_globals_hash_cache(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import extract_globals_from_lua_source

        with tempfile.TemporaryDirectory() as tmp_dir:
            addons_dir = os.path.join(tmp_dir, "AddOns")
            lib_dir = os.path.join(addons_dir, "LibFilters-3.0")
            extract_dir = os.path.join(tmp_dir, "Extract", "MyAddon")
            os.makedirs(lib_dir, exist_ok=True)
            os.makedirs(extract_dir, exist_ok=True)

            with open(os.path.join(lib_dir, "LibFilters-3.0.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: LibFilters-3.0\nLibFilters-3.0.lua\n")
            lib_lua = os.path.join(lib_dir, "LibFilters-3.0.lua")
            with open(lib_lua, "w", encoding="utf-8") as lf:
                lf.write(
                    'local filterNames = { "LF_SMITHING_DECONSTRUCT", "LF_SMITHING_IMPROVEMENT" }\n'
                    'for i, name in ipairs(filterNames) do _G[name] = i end\n'
                )

            with open(os.path.join(extract_dir, "MyAddon.txt"), "w", encoding="utf-8") as amf:
                amf.write("## Title: MyAddon\n## DependsOn: LibFilters-3.0>=350\n")

            cache_file = os.path.join(tmp_dir, "Cache", "dependency_globals_cache.json")
            with patch.object(esoui_ram_index, "ESO_ADDONS_DIR", addons_dir), patch.object(
                esoui_ram_index, "DEPENDENCY_CACHE_FILE", cache_file
            ), patch.object(esoui_ram_index, "DEPENDENCY_GLOBALS_CACHE", {}), patch.object(
                esoui_ram_index, "DEPENDENCY_DISK_CACHE_LOADED", False
            ):
                globals_map = esoui_ram_index.collect_dependency_globals(extract_dir, extract_globals_from_lua_source)
                self.assertIn("LF_SMITHING_DECONSTRUCT", globals_map)
                self.assertIn("LF_SMITHING_IMPROVEMENT", globals_map)
                self.assertTrue(os.path.isfile(cache_file))

                with open(lib_lua, "w", encoding="utf-8") as lf:
                    lf.write(
                        'local filterNames = { "LF_SMITHING_DECONSTRUCT", "LF_SMITHING_IMPROVEMENT", "LF_FENCE_SELL" }\n'
                        'for i, name in ipairs(filterNames) do _G[name] = i end\n'
                    )
                globals_map_updated = esoui_ram_index.collect_dependency_globals(extract_dir, extract_globals_from_lua_source)
                self.assertIn("LF_FENCE_SELL", globals_map_updated)


    def test_07_event_filters_and_dependency_repeated_globals(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file

        esoui_ram_index.parse_event_signatures_from_api_doc([
            "* EVENT_UNIT_CREATED (*string* _unitTag_)",
            "* EVENT_INVENTORY_SINGLE_SLOT_UPDATE (*Bag* _bagId_, *integer* _slotIndex_, *bool* _isNewItem_, *ItemUISoundCategory* _itemSoundCategory_, *integer* _inventoryUpdateReason_, *integer* _stackCountChange_)",
        ])

        lua_src = (
            "local NAME = 'ChillGiveaway'\n"
            "local A = {}\n"
            "function A.Init()\n"
            "    LibAddonMenu2:RegisterAddonPanel('P', {})\n"
            "    LibAddonMenu2:RegisterOptionControls('P', {})\n"
            "    EVENT_MANAGER:RegisterForEvent(NAME, EVENT_INVENTORY_SINGLE_SLOT_UPDATE, function(_, bag)\n"
            "        if bag == BAG_BACKPACK then A.Refresh() end\n"
            "    end)\n"
            "    EVENT_MANAGER:RegisterForEvent(NAME, EVENT_UNIT_CREATED, function(_, unitTag)\n"
            "        if unitTag == 'player' then A.Refresh() end\n"
            "    end)\n"
            "end\n"
        )
        ctx = {
            "has_bindings_xml": False,
            "xml_content": "",
            "all_global_tables": set(),
            "dynamic_globals": set(),
            "saved_variables": set(),
            "root_addon_manifests": ["ChillGiveaway.txt"],
            "root_txt_manifests": [],
        }
        dep_stub = {"LibAddonMenu2": "/live/AddOns/LibAddonMenu-2.0/LibAddonMenu-2.0.lua:1"}
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
            "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
        ), patch(
            "src.esoui_lua_analyzer.collect_dependency_globals", return_value=dep_stub
        ):
            res = analyze_lua_file("ChillGiveaway/ChillGiveaway.lua", lua_src, ".", ctx)
        self.assertIn("Use event filters for inventory items instead of checking code slower in lua: EVENT_INVENTORY_SINGLE_SLOT_UPDATE", res)
        self.assertIn("Use event filters for unit tags instead of checking code slower in lua: EVENT_UNIT_CREATED", res)
        self.assertIn("Global 'LibAddonMenu2' is used 2 times in this file without a local reference", res)

    def test_08_wiki_event_filter_html_parser_and_session_sync(self):
        from src import esoui_lua_analyzer

        sample_html = (
            "<table>"
            "<tr><th>filterType</th><th>eventNames (examples)</th></tr>"
            "<tr><td>REGISTER_FILTER_BAG_ID</td><td>EVENT_INVENTORY_SINGLE_SLOT_UPDATE</td></tr>"
            "<tr><td>REGISTER_FILTER_CUSTOM_TEST</td><td>EVENT_NEW_WIKI_TEST_EVENT</td></tr>"
            "<tr><td>REGISTER_FILTER_INVALID</td><td>EVENT_SHOULD_BE_IGNORED</td></tr>"
            "</table>"
        )
        parsed = esoui_lua_analyzer._parse_wiki_event_filter_html(sample_html)
        self.assertEqual(parsed["EVENT_INVENTORY_SINGLE_SLOT_UPDATE"], ["REGISTER_FILTER_BAG_ID"])
        self.assertEqual(parsed["EVENT_NEW_WIKI_TEST_EVENT"], ["REGISTER_FILTER_CUSTOM_TEST"])
        self.assertNotIn("EVENT_SHOULD_BE_IGNORED", parsed)

        class _FakeResp:
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return sample_html.encode("utf-8")

        with tempfile.TemporaryDirectory() as tmp_dir:
            cache_json = os.path.join(tmp_dir, "wiki_event_filters.json")
            with patch.object(esoui_lua_analyzer, "_WIKI_EVENT_FILTER_SESSION_LOADED", False), patch.object(
                esoui_lua_analyzer, "_WIKI_DYNAMIC_EVENT_RULES", {}
            ), patch.object(esoui_lua_analyzer, "WIKI_EVENT_FILTERS_CACHE_FILE", cache_json), patch(
                "urllib.request.urlopen", return_value=_FakeResp()
            ) as mock_open:
                filters_1, title_1 = esoui_lua_analyzer._get_event_filter_spec("EVENT_NEW_WIKI_TEST_EVENT")
                filters_2, _ = esoui_lua_analyzer._get_event_filter_spec("EVENT_NEW_WIKI_TEST_EVENT")
                self.assertEqual(mock_open.call_count, 1)
                self.assertEqual(filters_1, {"REGISTER_FILTER_CUSTOM_TEST"})
                self.assertEqual(filters_2, {"REGISTER_FILTER_CUSTOM_TEST"})
                self.assertIn("new wiki test event", title_1)
                self.assertTrue(os.path.isfile(cache_json))

    def test_09_cached_dependency_resolution_and_pc_folder_filters(self):
        import zipfile
        from src import esoui_download_io, esoui_filelist_search, esoui_ram_index
        from src.esoui_lua_analyzer import extract_globals_from_lua_source

        sample_v4 = self._sample_v4_filelist() + [
            {
                "id": 928,
                "title": "MasterMerchant",
                "author": "sharlikran",
                "version": "3.8.0",
                "lastUpdate": 1791292000000,
                "addonStatus": "Live",
                "addons": [
                    {"path": "MasterMerchant", "addOnVersion": "380", "apiVersion": "101051", "library": False},
                    {"path": "MasterMerchant/Libs/LibGuildStore", "addOnVersion": "15", "apiVersion": "101051", "library": True},
                ],
                "library": False,
            },
            {
                "id": 9987,
                "title": "LibGuildStore",
                "author": "sharlikran",
                "version": "1.0.14",
                "lastUpdate": 1770000000000,
                "addonStatus": "Live",
                "addons": [
                    {"path": "LibGuildStore", "addOnVersion": "14", "apiVersion": "101050", "library": True},
                ],
                "library": True,
            },
        ]

        # Embedded version 15 in MasterMerchant (928) must beat standalone version 14 (9987)
        resolved_gs = esoui_filelist_search.resolve_dependency_online_package("LibGuildStore", filelist=sample_v4)
        self.assertIsNotNone(resolved_gs)
        self.assertEqual(resolved_gs["addon_id"], "928")
        self.assertEqual(resolved_gs["sub_path"], "MasterMerchant/Libs/LibGuildStore")
        self.assertEqual(resolved_gs["add_on_version"], 15)

        # PCDependsOn is parsed, ConsoleDependsOn is ignored
        deps, _ = esoui_ram_index.parse_manifest_dependencies(
            "## PCDependsOn: LibFilters-3.0>=350\n## ConsoleDependsOn: LibConsoleOnly\n"
        )
        self.assertEqual(deps, ["LibFilters-3.0"])

        # PC ignored subdirectories (case-insensitive) vs PC-only folder
        self.assertTrue(esoui_ram_index._is_pc_ignored_rel_path("Console/ConsoleFile.lua"))
        self.assertTrue(esoui_ram_index._is_pc_ignored_rel_path("XB1/XboxFile.lua"))
        self.assertTrue(esoui_ram_index._is_pc_ignored_rel_path("Playstation/PsFile.lua"))
        self.assertTrue(esoui_ram_index._is_pc_ignored_rel_path("Internal/DevFile.lua"))
        self.assertTrue(esoui_ram_index._is_pc_ignored_rel_path("Future/NextFile.lua"))
        self.assertFalse(esoui_ram_index._is_pc_ignored_rel_path("PC/LibForgottenAddons.lua"))

        with tempfile.TemporaryDirectory() as tmp_dir:
            addons_dir = os.path.join(tmp_dir, "live", "AddOns")
            old_lib_dir = os.path.join(addons_dir, "LibFilters-3.0")
            cache_dir = os.path.join(tmp_dir, "Cache")
            cache_addons_dir = os.path.join(cache_dir, "AddOns")
            cache_extracted_dir = os.path.join(cache_addons_dir, "_extracted")
            stale_dir = os.path.join(cache_extracted_dir, "LibFilters-3.0")
            extract_dir = os.path.join(tmp_dir, "Extract", "CheckedAddon")
            os.makedirs(old_lib_dir, exist_ok=True)
            os.makedirs(stale_dir, exist_ok=True)
            os.makedirs(extract_dir, exist_ok=True)

            # Outdated local AddOnVersion 340 vs online 350
            with open(os.path.join(old_lib_dir, "LibFilters-3.0.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: LibFilters-3.0\n## AddOnVersion: 340\nLibFilters-3.0.lua\n")
            with open(os.path.join(old_lib_dir, "LibFilters-3.0.lua"), "w", encoding="utf-8") as lf:
                lf.write("OLD_LOCAL_GLOBAL = true\n")

            # Stale file that must be wiped before extracting new ZIP
            stale_file = os.path.join(stale_dir, "ObsoleteOldFile.lua")
            with open(stale_file, "w", encoding="utf-8") as sf:
                sf.write("STALE_GLOBAL = true\n")

            with open(os.path.join(extract_dir, "CheckedAddon.addon"), "w", encoding="utf-8") as amf:
                amf.write("## Title: CheckedAddon\n## PCDependsOn: LibFilters-3.0>=350\n")

            # Create fake downloaded ZIP with AddOnVersion 350, PC/LibForgottenAddons.lua, and Console/Ignored.lua
            source_zip = os.path.join(tmp_dir, "LibFilters-3.0_350.zip")
            with zipfile.ZipFile(source_zip, "w") as zf:
                zf.writestr(
                    "LibFilters-3.0/LibFilters-3.0.txt",
                    "## Title: LibFilters-3.0\n## AddOnVersion: 350\nPC/LibForgottenAddons.lua\nConsole/Ignored.lua\n",
                )
                zf.writestr("LibFilters-3.0/PC/LibForgottenAddons.lua", "FRESH_CACHED_PC_GLOBAL = true\n")
                zf.writestr("LibFilters-3.0/Console/Ignored.lua", "CONSOLE_ONLY_GLOBAL = true\n")

            dl_calls = []

            def _fake_download_zip(url, target_folder, force_download=False):
                dl_calls.append(url)
                os.makedirs(target_folder, exist_ok=True)
                dest = os.path.join(target_folder, "LibFilters-3.0.zip")
                with open(source_zip, "rb") as src_f, open(dest, "wb") as dst_f:
                    dst_f.write(src_f.read())
                return dest, "LibFilters-3.0.zip"

            cache_file = os.path.join(cache_dir, "dependency_globals_cache.json")
            with patch.object(esoui_ram_index, "ESO_ADDONS_DIR", addons_dir), patch.object(
                esoui_ram_index, "CACHE_ADDONS_DIR", cache_addons_dir
            ), patch.object(esoui_ram_index, "CACHE_ADDONS_EXTRACTED_DIR", cache_extracted_dir), patch.object(
                esoui_ram_index, "DEPENDENCY_CACHE_FILE", cache_file
            ), patch.object(esoui_ram_index, "DEPENDENCY_GLOBALS_CACHE", {}), patch.object(
                esoui_ram_index, "DEPENDENCY_DISK_CACHE_LOADED", False
            ), patch.object(esoui_ram_index, "LOCAL_ADDONS_MANIFEST_INDEX", None), patch.object(
                esoui_filelist_search, "get_filelist", return_value=sample_v4
            ), patch.object(esoui_download_io, "download_zip", side_effect=_fake_download_zip):
                g1 = esoui_ram_index.collect_dependency_globals(extract_dir, extract_globals_from_lua_source)
                self.assertEqual(len(dl_calls), 1)
                self.assertFalse(os.path.exists(stale_file))
                self.assertIn("FRESH_CACHED_PC_GLOBAL", g1)
                self.assertNotIn("OLD_LOCAL_GLOBAL", g1)
                self.assertNotIn("CONSOLE_ONLY_GLOBAL", g1)

                # Second run must reuse Cache/AddOns/_extracted without re-downloading
                esoui_ram_index.reset_dependency_globals_cache()
                g2 = esoui_ram_index.collect_dependency_globals(extract_dir, extract_globals_from_lua_source)
                self.assertEqual(len(dl_calls), 1)
                self.assertIn("FRESH_CACHED_PC_GLOBAL", g2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
