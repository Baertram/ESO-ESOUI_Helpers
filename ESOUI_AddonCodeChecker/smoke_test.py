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

        valid_url = "https://" + ".".join(["www", "esoui", "com"]) + "/downloads/info5026-Test.html"
        evil_url = "https://" + ".".join(["evil", "example", "com"]) + "/downloads/info5026-Test.html"
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

            from src import esoui_ai_and_report
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tmp_path = tf.name
            try:
                with patch.object(esoui_ai_and_report, "SHOW_BP_MULTI_GLOBALS", True):
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
        self.assertEqual(resolved_gs["addon_id"], "9987")
        self.assertEqual(resolved_gs["sub_path"], "LibGuildStore")
        self.assertEqual(resolved_gs["add_on_version"], 14)

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


    def test_10_comma_locals_and_function_param_tables_not_global(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "Teleport")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "Teleport.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: Teleport\n## APIVersion: 101051\nTeleport.lua\nNodes.lua\n")

            file1_src = "Teleport = Teleport or {}\nfunction Teleport.Load(id, options)\n    options = options or {}\nend\n"
            file2_src = (
                "local dungeons, sortedDungeons, wayshrines, houseNodeIndices, wayshrinesByZoneIndexPoiIndex\n"
                "function Teleport.Init()\n"
                "    wayshrines = {}\n"
                "    houseNodeIndices = {}\n"
                "    wayshrinesByZoneIndexPoiIndex = {}\n"
                "end\n"
            )
            with open(os.path.join(addon_dir, "Teleport.lua"), "w", encoding="utf-8") as f1:
                f1.write(file1_src)
            with open(os.path.join(addon_dir, "Nodes.lua"), "w", encoding="utf-8") as f2:
                f2.write(file2_src)

            ctx = collect_addon_context(tmp_dir)
            self.assertEqual(ctx.get("all_global_tables"), {"Teleport"})

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res1 = analyze_lua_file("Teleport/Teleport.lua", file1_src, tmp_dir, ctx)
                res2 = analyze_lua_file("Teleport/Nodes.lua", file2_src, tmp_dir, ctx)

            self.assertNotIn("Multiple Global Addon Tables", res1)
            self.assertNotIn("Multiple Global Addon Tables", res2)


    def test_11_missing_local_reference_to_addon_or_lib_global(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _parse_findings_into_report_data, _render_final_bbcode_report
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            lib_dir = os.path.join(tmp_dir, "LibDeconValue")
            os.makedirs(lib_dir, exist_ok=True)
            with open(os.path.join(lib_dir, "LibDeconValue.txt"), "w", encoding="utf-8") as mf:
                mf.write(
                    "## Title: LibDeconValue\n## IsLibrary: TrUe\n## APIVersion: 101051\n"
                    "LibDeconValue.lua\nLibDeconValue_Main.lua\nLibDeconValue_Stats.lua\n"
                )

            lib_lua = (
                "local lib = {}\n"
                "LibDeconValue = lib\n"
                "function LibDeconValue.GetValue(itemLink)\n"
                "    return 42\n"
                "end\n"
            )
            lib_main = (
                "\ufeffLibDeconValue = LibDeconValue or { }\n"
                "local data = LibDeconValue.Data\n"
                "function LibDeconValue:GetDeconValue(itemLink)\n"
                "    return LibDeconValue.GetValue(itemLink)\n"
                "end\n"
            )
            lib_stats = (
                "LibDeconValue = LibDeconValue or {}\n"
                "local LDV = LibDeconValue\n"
                "function LDV.GetStats()\n"
                "    return 1\n"
                "end\n"
            )
            with open(os.path.join(lib_dir, "LibDeconValue.lua"), "w", encoding="utf-8") as lf:
                lf.write(lib_lua)
            with open(os.path.join(lib_dir, "LibDeconValue_Main.lua"), "w", encoding="utf-8") as lf2:
                lf2.write(lib_main)
            with open(os.path.join(lib_dir, "LibDeconValue_Stats.lua"), "w", encoding="utf-8") as lf3:
                lf3.write(lib_stats)

            ctx = collect_addon_context(tmp_dir)
            self.assertTrue(ctx.get("is_library"))
            self.assertIn("LibDeconValue", ctx.get("all_global_tables"))

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_lib = analyze_lua_file("LibDeconValue/LibDeconValue.lua", lib_lua, tmp_dir, ctx)
                res_main = analyze_lua_file("LibDeconValue/LibDeconValue_Main.lua", lib_main, tmp_dir, ctx)
                res_stats = analyze_lua_file("LibDeconValue/LibDeconValue_Stats.lua", lib_stats, tmp_dir, ctx)

            self.assertIn("Missing local reference to global addon table 'LibDeconValue' (lines 3)", res_lib)
            self.assertIn("Missing local reference to global addon table 'LibDeconValue' (lines 2, 3, 4)", res_main)
            self.assertNotIn("Missing local reference", res_stats)
            self.assertNotIn("Global Pollution", res_lib)

            report_data = {
                "zip_all_entries": [
                    "LibDeconValue/",
                    "LibDeconValue/LibDeconValue.txt",
                    "LibDeconValue/LibDeconValue.lua",
                    "LibDeconValue/LibDeconValue_Main.lua",
                    "LibDeconValue/LibDeconValue_Stats.lua",
                ],
                "zip_flagged_paths": set(),
                "zip_manifest_paths": {"LibDeconValue/LibDeconValue.txt"},
                "zip_tree_bbcode": "",
                "zip_violations": [],
                "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                "best_practices": defaultdict(list),
            }
            _parse_findings_into_report_data("LibDeconValue/LibDeconValue.lua", "lua", res_lib, report_data)
            _parse_findings_into_report_data("LibDeconValue/LibDeconValue_Main.lua", "lua", res_main, report_data)
            _parse_findings_into_report_data("LibDeconValue/LibDeconValue_Stats.lua", "lua", res_stats, report_data)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tmp_rep = tf.name
            try:
                _render_final_bbcode_report(tmp_rep, "LibDeconValue.zip", "2026-11-21 05:30:00 PM", report_data)
                with open(tmp_rep, "r", encoding="utf-8") as rf:
                    rendered = rf.read()
                self.assertIn("[u]Possible action: local reference to global missing?[/u]", rendered)
                self.assertIn("Consider adding a line local <globalName> = <globalName> at the top of your lua files", rendered)
                self.assertIn("[u][b]LibDeconValue[/b][/u]", rendered)
                self.assertIn("  \\LibDeconValue.lua: 3", rendered)
                self.assertIn("  \\LibDeconValue_Main.lua: 2, 3, 4", rendered)
                self.assertNotIn("  \\LibDeconValue_Stats.lua", rendered)
            finally:
                if os.path.exists(tmp_rep):
                    os.remove(tmp_rep)

    def test_12_lam_table_callbacks_with_for_do_loops_no_false_global(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import _check_lua_global_variable_leaks

        lua_src = (
            "local options = {}\n"
            "local function BuildOptions(CATEGORIES, sv)\n"
            "    for i, category in ipairs(CATEGORIES) do\n"
            "        table.insert(options, 1 + i, {\n"
            "            type = 'dropdown',\n"
            "            default = {},\n"
            "            getFunc = function()\n"
            "                local list = {}\n"
            "                for _, choice in ipairs(category.choices) do\n"
            "                    if sv.keep[category.key][choice.value] then list[#list + 1] = choice.value end\n"
            "                end\n"
            "                return list\n"
            "            end,\n"
            "            setFunc = function(values)\n"
            "                local keep = sv.keep[category.key]\n"
            "                for _, choice in ipairs(category.choices) do keep[choice.value] = false end\n"
            "                for _, value in ipairs(values or {}) do keep[value] = true end\n"
            "            end,\n"
            "        })\n"
            "    end\n"
            "end\n"
        )
        ctx = {"all_global_tables": set(), "saved_variables": set()}
        issues = []
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True):
            _check_lua_global_variable_leaks(lua_src, lua_src.splitlines(), ctx, issues)
        self.assertEqual(issues, [])


    def test_13_hardcoded_language_files_in_manifest(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _parse_findings_into_report_data, _render_final_bbcode_report
        from src.esoui_manifest_xml_analyzer import analyze_manifest_file

        ctx = {
            "has_bindings_xml": False,
            "xml_content": "",
            "all_global_tables": {"RPQuest"},
            "saved_variables": set(),
            "root_addon_manifests": [],
            "root_txt_manifests": ["RPQuest.txt"],
            "bundled_sub_addons": set(),
        }

        bad_manifest = (
            "## Title: RPQuest\n"
            "## APIVersion: 101051\n"
            "lang/en.lua\n"
            "lang/es.lua\n"
            "RPQuest.lua\n"
        )
        good_manifest = (
            "## Title: RPQuest\n"
            "## APIVersion: 101051\n"
            "lang/en.lua\n"
            "lang/$(language).lua\n"
            "RPQuest.lua\n"
        )

        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
            "src.esoui_manifest_xml_analyzer.get_current_api_version", return_value="101051"
        ):
            res_bad = analyze_manifest_file("RPQuest/RPQuest.txt", bad_manifest, ".txt", ctx)
            res_good = analyze_manifest_file("RPQuest/RPQuest.txt", good_manifest, ".txt", ctx)

        self.assertIn("Hardcoded language files - Use dynamic $(language): lang/en.lua, lang/es.lua", res_bad)
        self.assertNotIn("Hardcoded language files", res_good)

        report_data = {
            "zip_all_entries": ["RPQuest/", "RPQuest/RPQuest.txt", "RPQuest/RPQuest.lua"],
            "zip_flagged_paths": set(),
            "zip_manifest_paths": {"RPQuest/RPQuest.txt"},
            "zip_tree_bbcode": "",
            "zip_violations": [],
            "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
            "best_practices": defaultdict(list),
        }
        _parse_findings_into_report_data("RPQuest/RPQuest.txt", "manifest", res_bad, report_data)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
            tmp_rep = tf.name
        try:
            _render_final_bbcode_report(tmp_rep, "RPQuest.zip", "2026-11-21 08:00:00 PM", report_data)
            with open(tmp_rep, "r", encoding="utf-8") as rf:
                rendered = rf.read()
            self.assertIn("[u]Hardcoded language files - Use dynamic $(language)[/u]", rendered)
            self.assertIn("[spoiler]\nlang/en.lua\nlang/es.lua\n[/spoiler]", rendered)
        finally:
            if os.path.exists(tmp_rep):
                os.remove(tmp_rep)


    def test_14_zip_folder_structure_and_analysis_for_warning(self):
        import zipfile
        from src.esoui_ai_and_report import _check_zip_structure, _render_final_bbcode_report

        def _run_zip_case(zip_filename, files_dict):
            with tempfile.TemporaryDirectory() as tmp_dir:
                zp = os.path.join(tmp_dir, zip_filename)
                with zipfile.ZipFile(zp, "w") as zf:
                    for rel_n, body in files_dict.items():
                        zf.writestr(rel_n, body)
                rep = {
                    "zip_tree_bbcode": "",
                    "zip_violations": [],
                    "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                    "best_practices": defaultdict(list),
                }
                _check_zip_structure(zp, rep)
                out_txt = os.path.join(tmp_dir, "report.txt")
                _render_final_bbcode_report(out_txt, zip_filename, "2026-11-21 09:05:00 PM", rep)
                with open(out_txt, "r", encoding="utf-8") as rf:
                    return rf.read()

        # 1. Valid single matching folder (including bundled sub-addon with matching subfolder)
        ok_rep = _run_zip_case(
            "CollectiblesTracker.zip",
            {
                "CollectiblesTracker/CollectiblesTracker.addon": "## Title: CollectiblesTracker\n",
                "CollectiblesTracker/Core.lua": "local x = 1\n",
                "CollectiblesTracker/LibExtendedJournal/LibExtendedJournal.addon": "## Title: LibExtendedJournal\n",
            },
        )
        self.assertIn("[b]ANALYSIS FOR[/b]: CollectiblesTracker.zip", ok_rep)
        self.assertNotIn("Wrong addon zip", ok_rep)
        self.assertNotIn("Check addon zip", ok_rep)

        # 1b. Bundled sub-addon in mismatched subfolder name
        sub_mismatch_rep = _run_zip_case(
            "CollectiblesTracker.zip",
            {
                "CollectiblesTracker/CollectiblesTracker.addon": "## Title: CollectiblesTracker\n",
                "CollectiblesTracker/Libs/LibExtendedJournal.addon": "## Title: LibExtendedJournal\n",
            },
        )
        self.assertIn('[b]ANALYSIS FOR[/b]: [color="Red"]:mad: CollectiblesTracker.zip[/color]', sub_mismatch_rep)
        self.assertIn('[color="red"][b][u]Wrong addon zip[/u][/b][/color]', sub_mismatch_rep)

        # 2. No folder in ZIP (loose manifest in root)
        no_dir_rep = _run_zip_case("CompanionDashboard.zip", {"CompanionDashboard.txt": "## Title: CompanionDashboard\n"})
        self.assertIn('[b]ANALYSIS FOR[/b]: [color="Red"]:mad: CompanionDashboard.zip[/color]', no_dir_rep)
        self.assertIn('[color="red"][b][u]Wrong addon zip[/u][/b][/color]\nFoldername must match manifest (case-sensitive)', no_dir_rep)

        # 3. Case mismatch folder name
        case_rep = _run_zip_case("CompanionDashboard.zip", {"companiondashboard/CompanionDashboard.txt": "## Title: CompanionDashboard\n"})
        self.assertIn('[b]ANALYSIS FOR[/b]: [color="Red"]:mad: CompanionDashboard.zip[/color]', case_rep)
        self.assertIn('[color="red"][b][u]Wrong addon zip[/u][/b][/color]', case_rep)

        # 4. Multiple top-level folders
        multi_rep = _run_zip_case(
            "CompanionDashboard.zip",
            {
                "CompanionDashboard/CompanionDashboard.txt": "## Title: CompanionDashboard\n",
                "OtherAddon/OtherAddon.txt": "## Title: OtherAddon\n",
            },
        )
        self.assertIn('[b]ANALYSIS FOR[/b]: [color="Red"]:mad: CompanionDashboard.zip[/color]', multi_rep)
        self.assertIn(
            '[color="red"][b][u]Check addon zip[/u][/b][/color]\nContains multiple folders: DO NOT OVERWRITE OTHER ADDONS FROM WITHIN YOUR ADDON!',
            multi_rep,
        )


    def test_15_libstub_excluded_functions(self):
        from src.esoui_lua_analyzer import find_uncommented_libstub_hits

        lua_src = (
            'local NAME = "LibCodesCommonCode"\n'
            "local VERSION = 40\n"
            "local Lib = { version = VERSION }\n"
            "_G[NAME] = Lib\n"
            "\n"
            "function Lib.GetLibAddonMenu( )\n"
            "    if (LibStub and not ZO_IsConsoleOrGameCoreUI()) then\n"
            '        local version = select(2, LibStub("LibAddonMenu-2.0", true))\n'
            "        if (version and version < 36) then\n"
            "            return nil\n"
            "        end\n"
            "    end\n"
            "    return LibAddonMenu2\n"
            "end\n"
            "\n"
            "function Lib.OtherHelper()\n"
            '    return LibStub("LibSomething")\n'
            "end\n"
        )
        hits = find_uncommented_libstub_hits(lua_src)
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0][0], 17)


    def test_16_grouped_global_function_pollution_report(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _parse_findings_into_report_data, _render_final_bbcode_report
        from src.esoui_lua_analyzer import analyze_lua_file

        lua_src = (
            "function RedLedger_Keybind_Test()\n"
            "    return true\n"
            "end\n"
            "function RedLedger_WhatEver()\n"
            "    return false\n"
            "end\n"
        )
        ctx = {
            "has_bindings_xml": False,
            "xml_content": "",
            "all_global_tables": {"RedLedger"},
            "dynamic_globals": set(),
            "saved_variables": set(),
            "root_addon_manifests": ["RedLedger.txt"],
            "root_txt_manifests": [],
        }

        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
            "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
        ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
            res_lua = analyze_lua_file("RedLedger/RedLedger.lua", lua_src, ".", ctx)

        report_data = {
            "zip_all_entries": ["RedLedger/", "RedLedger/RedLedger.txt", "RedLedger/RedLedger.lua"],
            "zip_flagged_paths": set(),
            "zip_manifest_paths": {"RedLedger/RedLedger.txt"},
            "zip_tree_bbcode": "",
            "zip_violations": [],
            "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
            "best_practices": defaultdict(list),
        }
        _parse_findings_into_report_data("RedLedger/RedLedger.lua", "lua", res_lua, report_data)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
            tmp_rep = tf.name
        try:
            _render_final_bbcode_report(tmp_rep, "RedLedger.zip", "2026-11-22 12:00:00 AM", report_data)
            with open(tmp_rep, "r", encoding="utf-8") as rf:
                rendered = rf.read()
            self.assertIn("[u]Global Function Pollution (leaked into _G): Keep local or attach to your single addon table[/u]", rendered)
            self.assertIn('[*] \\RedLedger.lua [spoiler][SIZE="2"]1: function RedLedger_Keybind_Test()\n4: function RedLedger_WhatEver()[/SIZE][/spoiler]', rendered)
            self.assertNotIn("(-- functio", rendered)
        finally:
            if os.path.exists(tmp_rep):
                os.remove(tmp_rep)

    def test_17_single_file_addon_strict_local_pollution_message(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _parse_findings_into_report_data, _render_final_bbcode_report
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "RaffleGold")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "RaffleGold.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: RaffleGold\n## APIVersion: 101051\nRaffleGold.lua\n")
            lua_src = "RaffleGold = {\n    name = 'RaffleGold',\n}\n"
            with open(os.path.join(addon_dir, "RaffleGold.lua"), "w", encoding="utf-8") as lf:
                lf.write(lua_src)

            ctx = collect_addon_context(tmp_dir)
            self.assertEqual(ctx.get("lua_file_count"), 1)

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_lua = analyze_lua_file("RaffleGold/RaffleGold.lua", lua_src, tmp_dir, ctx)

            self.assertNotIn("Global Pollution: Created global table", res_lua)

            report_data = {
                "is_strict_local_addon": True,
                "zip_all_entries": ["RaffleGold/", "RaffleGold/RaffleGold.txt", "RaffleGold/RaffleGold.lua"],
                "zip_flagged_paths": set(),
                "zip_manifest_paths": {"RaffleGold/RaffleGold.txt"},
                "zip_tree_bbcode": "",
                "zip_violations": [],
                "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                "best_practices": defaultdict(list),
            }
            _parse_findings_into_report_data("RaffleGold/RaffleGold.lua", "lua", res_lua, report_data)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tmp_rep = tf.name
            try:
                _render_final_bbcode_report(tmp_rep, "RaffleGold.zip", "2026-11-22 12:25:00 AM", report_data)
                with open(tmp_rep, "r", encoding="utf-8") as rf:
                    rendered = rf.read()
                self.assertIn("Missing local definition? Single-file addon without Bindings/XML/API calls: keep everything 'local'!", rendered)
                self.assertNotIn("Else: Please define only 1 global table", rendered)
            finally:
                if os.path.exists(tmp_rep):
                    os.remove(tmp_rep)


    def test_18_addon_table_exported_at_end_of_file_is_legitimate(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "ArclightTaunt")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "ArclightTaunt.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: ArclightTaunt\n## APIVersion: 101051\nCore.lua\nUI.lua\n")

            core_src = (
                'local ADDON = "ArclightTaunt"\n'
                "local A = { targets = {}, rows = {}, demo = false }\n"
                "A.bossAlerts = { expired = { kind = 'expired' } }\n"
                "function A.Init()\n"
                "    for i = 1, 3 do\n"
                "        A.rows[i] = i\n"
                "    end\n"
                "end\n"
                "ArclightTaunt = A\n"
            )
            ui_src = "local A = ArclightTaunt\nfunction A.Show() end\n"
            with open(os.path.join(addon_dir, "Core.lua"), "w", encoding="utf-8") as cf:
                cf.write(core_src)
            with open(os.path.join(addon_dir, "UI.lua"), "w", encoding="utf-8") as uf:
                uf.write(ui_src)

            ctx = collect_addon_context(tmp_dir)
            self.assertEqual(ctx.get("all_global_tables"), {"ArclightTaunt"})

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_core = analyze_lua_file("ArclightTaunt/Core.lua", core_src, tmp_dir, ctx)

            self.assertNotIn("Global Variable Pollution", res_core)
            self.assertNotIn("Multiple Global Addon Tables", res_core)


    def test_19_inline_anonymous_function_local_not_leaked(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import _check_lua_global_variable_leaks

        lua_src = (
            'BMR.ProfileDiagnostic("COUNT", "categories=" .. tostring((function() local n=0 for _ in pairs(addedByCategory) do n=n+1 end return n end)()))\n'
        )
        ctx = {"all_global_tables": {"BMR"}, "saved_variables": set()}
        issues = []
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True):
            _check_lua_global_variable_leaks(lua_src, lua_src.splitlines(), ctx, issues)
        self.assertEqual(issues, [])


    def test_20_event_add_on_loaded_checks_and_pairing(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "HideFriendStatus")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "HideFriendStatus.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: HideFriendStatus\n## APIVersion: 101051\nHideFriendStatus.lua\n")

            bad_lua = (
                'local HideFriendStatus = { name = "HideFriendStatus" }\n'
                'function HideFriendStatus.Init(event, addonName)\n'
                '    HideFriendStatus.SuppressStatusMessages()\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent(HideFriendStatus.name, EVENT_ADD_ON_LOADED, HideFriendStatus.Init)\n'
            )
            with open(os.path.join(addon_dir, "HideFriendStatus.lua"), "w", encoding="utf-8") as lf:
                lf.write(bad_lua)

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_bad = analyze_lua_file("HideFriendStatus/HideFriendStatus.lua", bad_lua, tmp_dir, ctx)

            self.assertIn("Unregister EVENT_ADD_ON_LOADED is missing", res_bad)
            self.assertIn("EVENT_ADD_ON_LOADED addonName not compared against addon folder name (case-sensitive)", res_bad)

            mismatch_lua = (
                'local HideFriendStatus = { name = "HideFriendStatus" }\n'
                'function HideFriendStatus.Init(event, addonName)\n'
                '    if addonName ~= HideFriendStatus.name then return end\n'
                '    EVENT_MANAGER:UnregisterForEvent("WrongNamespace", EVENT_ADD_ON_LOADED)\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent(HideFriendStatus.name, EVENT_ADD_ON_LOADED, HideFriendStatus.Init)\n'
            )
            with open(os.path.join(addon_dir, "HideFriendStatus.lua"), "w", encoding="utf-8") as lf:
                lf.write(mismatch_lua)
            ctx_mm = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_mm = analyze_lua_file("HideFriendStatus/HideFriendStatus.lua", mismatch_lua, tmp_dir, ctx_mm)
            self.assertIn("Unregister EVENT_ADD_ON_LOADED does not match your register name", res_mm)

            slop_lua = (
                "if EVENT_MANAGER then end\n"
                "if ZO_ChatSystem_GetEventHandlers then end\n"
                "if ZO_NotificationManager then end\n"
                "if CHAT_ROUTER and CHAT_ROUTER.FormatAndAddChatMessage then end\n"
                "if ZO_ChatSystem and ZO_ChatSystem.AddMessageToWindow then end\n"
            )
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch.dict(
                esoui_ram_index.ESOUI_RAM_DICTIONARY,
                {
                    "EVENT_MANAGER": "stub",
                    "ZO_ChatSystem_GetEventHandlers": "stub",
                    "ZO_NotificationManager": "stub",
                    "CHAT_ROUTER": "stub",
                    "ZO_ChatSystem": "stub",
                },
                clear=False,
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_slop = analyze_lua_file("HideFriendStatus/HideFriendStatus.lua", slop_lua, tmp_dir, ctx)
            self.assertIn("1 (EVENT_MANAGER)", res_slop)
            self.assertIn("2 (ZO_ChatSystem_GetEventHandlers)", res_slop)
            self.assertIn("3 (ZO_NotificationManager)", res_slop)
            self.assertIn("4 (CHAT_ROUTER.FormatAndAddChatMessage)", res_slop)
            self.assertIn("5 (ZO_ChatSystem.AddMessageToWindow)", res_slop)

            good_lua = (
                'local HideFriendStatus = { name = "HideFriendStatus" }\n'
                'HideFriendStatus.EM = GetEventManager()\n'
                'function HideFriendStatus.Init(event, addonName)\n'
                '    if addonName ~= HideFriendStatus.name then return end\n'
                '    HideFriendStatus.EM:UnregisterForEvent(HideFriendStatus.name, EVENT_ADD_ON_LOADED)\n'
                'end\n'
                'HideFriendStatus.EM:RegisterForEvent(HideFriendStatus.name, EVENT_ADD_ON_LOADED, HideFriendStatus.Init)\n'
            )
            with open(os.path.join(addon_dir, "HideFriendStatus.lua"), "w", encoding="utf-8") as lf:
                lf.write(good_lua)
            ctx_good = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_good = analyze_lua_file("HideFriendStatus/HideFriendStatus.lua", good_lua, tmp_dir, ctx_good)

            self.assertNotIn("Unregister EVENT_ADD_ON_LOADED", res_good)
            self.assertNotIn("EVENT_ADD_ON_LOADED addonName", res_good)
            self.assertNotIn("EVENT_ADD_ON_LOADED check", res_good)
            self.assertNotIn("EVENT_ADD_ON_LOADED missing", res_good)

    def test_21_multi_drop_parsing_and_zip_before_txt_order(self):
        import esoui_codecheck

        with tempfile.TemporaryDirectory() as tmp_dir:
            spaced_dir = os.path.join(tmp_dir, "My Addons")
            os.makedirs(spaced_dir, exist_ok=True)
            z1 = os.path.join(spaced_dir, "AddonOne.zip")
            z2 = os.path.join(tmp_dir, "AddonTwo.zip")
            t1 = os.path.join(spaced_dir, "batch_list.txt")
            for fp in (z1, z2, t1):
                with open(fp, "w", encoding="utf-8") as fh:
                    fh.write("stub")

            win_drop_str = f'"{t1}" "{z1}" {z2}'
            parsed = esoui_codecheck._parse_multi_drop_paths(win_drop_str)
            self.assertEqual(parsed, [t1, z1, z2])

            comma_drop_str = f'{t1}, {z1}, {z2}'
            self.assertEqual(esoui_codecheck._parse_multi_drop_paths(comma_drop_str), [t1, z1, z2])

            single_with_spaces = f'"{z1}"'
            self.assertEqual(esoui_codecheck._parse_multi_drop_paths(single_with_spaces), [])

            execution_order = []
            with patch.object(
                esoui_codecheck, "handle_input", side_effect=lambda p, force_download=False: (p, os.path.basename(p))
            ), patch.object(
                esoui_codecheck, "process_addon", side_effect=lambda zp, zn, **kw: execution_order.append(("zip", zn))
            ), patch.object(
                esoui_codecheck, "_run_txt_batch_file", side_effect=lambda tp: execution_order.append(("txt", os.path.basename(tp)))
            ), patch.object(esoui_codecheck, "print_multi_addon_summary"):
                esoui_codecheck._process_multi_drop_targets(parsed)

            self.assertEqual(
                execution_order,
                [("zip", "AddonOne.zip"), ("zip", "AddonTwo.zip"), ("txt", "batch_list.txt")],
            )


    def test_22_inventory_slot_show_context_menu_hook_and_override(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _parse_findings_into_report_data, _render_final_bbcode_report
        from src.esoui_lua_analyzer import analyze_lua_file

        ctx = {
            "has_bindings_xml": False,
            "xml_content": "",
            "all_global_tables": {"MyInvAddon"},
            "dynamic_globals": set(),
            "saved_variables": set(),
            "root_addon_manifests": ["MyInvAddon.txt"],
            "root_txt_manifests": [],
        }

        bad_lua = (
            'ZO_PreHook("ZO_InventorySlot_ShowContextMenu", function(invSlot) end)\n'
            'local origShow = ZO_InventorySlot_ShowContextMenu\n'
            'ZO_InventorySlot_ShowContextMenu = function(invSlot)\n'
            '    origShow(invSlot)\n'
            'end\n'
        )
        safe_call_lua = (
            'local function OpenMenu(slot)\n'
            '    ZO_InventorySlot_ShowContextMenu(slot)\n'
            'end\n'
        )

        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
            "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
        ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
            res_bad = analyze_lua_file("MyInvAddon/ContextMenu.lua", bad_lua, ".", ctx)
            res_lcm = analyze_lua_file("MyInvAddon/Libs/LibCustomMenu/LibCustomMenu.lua", bad_lua, ".", ctx)
            res_safe = analyze_lua_file("MyInvAddon/SafeCall.lua", safe_call_lua, ".", ctx)

        self.assertIn("Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu (line 1)", res_bad)
        self.assertIn("Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu (line 3)", res_bad)
        self.assertNotIn("Inventory Context Menu Hook", res_lcm)
        self.assertNotIn("Inventory Context Menu Hook", res_safe)

        report_data = {
            "zip_all_entries": ["MyInvAddon/", "MyInvAddon/MyInvAddon.txt", "MyInvAddon/ContextMenu.lua"],
            "zip_flagged_paths": set(),
            "zip_manifest_paths": {"MyInvAddon/MyInvAddon.txt"},
            "zip_tree_bbcode": "",
            "zip_violations": [],
            "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
            "best_practices": defaultdict(list),
        }
        _parse_findings_into_report_data("MyInvAddon/ContextMenu.lua", "lua", res_bad, report_data)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
            tmp_rep = tf.name
        try:
            _render_final_bbcode_report(tmp_rep, "MyInvAddon.zip", "2026-11-24 12:00:00 AM", report_data)
            with open(tmp_rep, "r", encoding="utf-8") as rf:
                rendered = rf.read()
            self.assertIn("[u]Inventory Context Menu Hook, instead of LibCustomMenu:RegisterContextMenu[/u]", rendered)
            self.assertIn(
                '[*] \\ContextMenu.lua [spoiler][SIZE="2"]1: ZO_PreHook("ZO_InventorySlot_ShowContextMenu", function(invSlot) end)\n'
                '3: ZO_InventorySlot_ShowContextMenu = function(invSlot)[/SIZE][/spoiler]',
                rendered,
            )
        finally:
            if os.path.exists(tmp_rep):
                os.remove(tmp_rep)


    def test_23_multiline_local_declaration_not_flagged_as_global(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file

        ctx = {
            "has_bindings_xml": False,
            "xml_content": "",
            "all_global_tables": {"MyTradeAddon"},
            "dynamic_globals": set(),
            "saved_variables": set(),
            "root_addon_manifests": ["MyTradeAddon.txt"],
            "root_txt_manifests": [],
        }
        lua_code = (
            "local function UpdateRow(rowControl)\n"
            "    local profitMarginControl,\n"
            "        averagePricePerUnitControl,\n"
            "        averagePriceControl,\n"
            "        purchasePricePerUnit,\n"
            "        averagePrice,\n"
            "        averagePricePerUnit = GetControlsForSearchResults(rowControl)\n"
            "    return averagePricePerUnit\n"
            "end\n"
        )
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
            "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
        ), patch.dict(
            esoui_ram_index.ESOUI_RAM_DICTIONARY,
            {"GetControlsForSearchResults": "stub"},
            clear=False,
        ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
            res = analyze_lua_file("MyTradeAddon/Search.lua", lua_code, ".", ctx)

        self.assertNotIn("averagePricePerUnit", res)
        self.assertIn("[STATUS] PASS", res)


    def test_24_multiple_global_addon_tables_subclass_and_arbitrary_rhs(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "ArkadiusTradeTools")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "ArkadiusTradeTools.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: ArkadiusTradeTools\n## SavedVariables: ArkadiusTradeToolsSV\nTemplates.lua\n")

            tpl_src = (
                "ArkadiusTradeTools = {}\n"
                "ArkadiusTradeToolsSV = ArkadiusTradeToolsSV or {}\n"
                "ArkadiusTradeToolsObjectPool = ZO_Object:Subclass()\n"
                "ArkadiusTradeToolsToggleButton = {}\n"
                "ArkadiusTradeToolsSortFilterList = ZO_SortFilterList:Subclass()\n"
                "ArkadiusTradeToolsSlider = ZO_InitializingObject:Subclass()\n"
                "ArkadiusTradeToolsFilterBar = {}\n"
            )
            with open(os.path.join(addon_dir, "Templates.lua"), "w", encoding="utf-8") as lf:
                lf.write(tpl_src)

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                ctx = collect_addon_context(tmp_dir)
                self.assertEqual(
                    ctx.get("all_global_tables"),
                    {
                        "ArkadiusTradeTools",
                        "ArkadiusTradeToolsObjectPool",
                        "ArkadiusTradeToolsToggleButton",
                        "ArkadiusTradeToolsSortFilterList",
                        "ArkadiusTradeToolsSlider",
                        "ArkadiusTradeToolsFilterBar",
                    },
                )
                self.assertNotIn("ArkadiusTradeToolsSV", ctx.get("all_global_tables"))
                res = analyze_lua_file("ArkadiusTradeTools/Templates.lua", tpl_src, tmp_dir, ctx)

            self.assertIn("Multiple Global Addon Tables: Found 6 global tables across the addon", res)


    def test_25_local_assignment_with_inequality_operator_on_rhs(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import _check_lua_global_variable_leaks

        lua_src = (
            "local function Migrate(quest, version, targetVersion)\n"
            "    local didMigrate = (quest.schemaVersion ~= version)\n"
            "    while version < targetVersion do\n"
            "        version = version + 1\n"
            "        didMigrate = true\n"
            "    end\n"
            "    return didMigrate\n"
            "end\n"
        )
        ctx = {"all_global_tables": set(), "saved_variables": set()}
        issues = []
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True):
            _check_lua_global_variable_leaks(lua_src, lua_src.splitlines(), ctx, issues)
        self.assertEqual(issues, [])


    def test_26_table_literal_methods_for_addon_loaded_event_filters_and_libstub(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "SimpleDPS")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "SimpleDPS.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: SimpleDPS\n## APIVersion: 101051\nSimpleDPS.lua\nSimpleDPS_UI.lua\n")
            with open(os.path.join(addon_dir, "SimpleDPS_UI.lua"), "w", encoding="utf-8") as uf:
                uf.write("local SDPS = SimpleDPS\n")
            lua_src = (
                "SimpleDPS = {\n"
                '    name = "SimpleDPS",\n'
                "    GetLibAddonMenu = function()\n"
                '        return LibStub("LibAddonMenu-2.0", true)\n'
                "    end,\n"
                "    OnUnitCreated = function(self, eventCode, unitTag)\n"
                "        if unitTag == 'player' then end\n"
                "    end,\n"
                "    OnAddOnLoaded = function(self, event, addonName)\n"
                "        if addonName == self.name then\n"
                "            EVENT_MANAGER:UnregisterForEvent(self.name, EVENT_ADD_ON_LOADED)\n"
                "        end\n"
                "    end,\n"
                "}\n"
                "EVENT_MANAGER:RegisterForEvent(SimpleDPS.name, EVENT_UNIT_CREATED, SimpleDPS.OnUnitCreated)\n"
                "EVENT_MANAGER:AddFilterForEvent(SimpleDPS.name, EVENT_UNIT_CREATED, REGISTER_FILTER_UNIT_TAG, 'player')\n"
                "EVENT_MANAGER:RegisterForEvent(SimpleDPS.name, EVENT_ADD_ON_LOADED, function(event, addonName) SimpleDPS:OnAddOnLoaded(event, addonName) end)\n"
            )
            with open(os.path.join(addon_dir, "SimpleDPS.lua"), "w", encoding="utf-8") as lf:
                lf.write(lua_src)

            esoui_ram_index.parse_event_signatures_from_api_doc([
                "* EVENT_UNIT_CREATED (*string* _unitTag_)",
            ])

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res = analyze_lua_file("SimpleDPS/SimpleDPS.lua", lua_src, tmp_dir, ctx)

            self.assertNotIn("EVENT_ADD_ON_LOADED addonName", res)
            self.assertNotIn("Unregister EVENT_ADD_ON_LOADED", res)
            self.assertNotIn("Deprecated LibStub Usage", res)
            self.assertIn("redundant 'unitTag' check in callback", res)


    def test_27_inner_table_name_fields_do_not_shadow_addon_name_via_local_alias(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "FurysAccountSync")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "FurysAccountSync.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: Fury's Account Sync\n## APIVersion: 101051\nFurysAccountSync.lua\nWindow.lua\n")

            main_lua = (
                "FurysAccountSync = {\n"
                '    name = "FurysAccountSync",\n'
                '    version = "0.2.2",\n'
                "}\n"
                "local AS = FurysAccountSync\n"
                "local function OnLoaded(_, addonName)\n"
                "    if addonName ~= AS.name then return end\n"
                "    EVENT_MANAGER:UnregisterForEvent(AS.name, EVENT_ADD_ON_LOADED)\n"
                "end\n"
                "EVENT_MANAGER:RegisterForEvent(AS.name, EVENT_ADD_ON_LOADED, OnLoaded)\n"
            )
            window_lua = (
                "local AS = FurysAccountSync\n"
                "local ACTIONS = {\n"
                '    { name = "Open the window", key = "open" },\n'
                "}\n"
            )
            with open(os.path.join(addon_dir, "FurysAccountSync.lua"), "w", encoding="utf-8") as f1:
                f1.write(main_lua)
            with open(os.path.join(addon_dir, "Window.lua"), "w", encoding="utf-8") as f2:
                f2.write(window_lua)

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res = analyze_lua_file("FurysAccountSync/FurysAccountSync.lua", main_lua, tmp_dir, ctx)

            self.assertNotIn("EVENT_ADD_ON_LOADED check does not match", res)
            self.assertNotIn("Open the window", res)
            self.assertNotIn("Unregister EVENT_ADD_ON_LOADED", res)

    def test_28_embedded_sub_addon_own_manifest_addon_loaded(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            main_dir = os.path.join(tmp_dir, "FurysGuildToolset")
            sub_dir = os.path.join(main_dir, "FurysAddonMenu")
            nested_lib_dir = os.path.join(main_dir, "libs", "LibWhatever")
            os.makedirs(sub_dir, exist_ok=True)
            os.makedirs(nested_lib_dir, exist_ok=True)

            with open(os.path.join(main_dir, "FurysGuildToolset.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: Fury's Guild Toolset\n## APIVersion: 101051\nFurysGuildToolset.lua\n")
            with open(os.path.join(sub_dir, "FurysAddonMenu.txt"), "w", encoding="utf-8") as smf:
                smf.write("## Title: Fury's Addon Menu\n## IsLibrary: true\n## APIVersion: 101051\nFurysAddonMenu.lua\n")
            with open(os.path.join(nested_lib_dir, "LibWhatever.txt"), "w", encoding="utf-8") as lmf:
                lmf.write("## Title: LibWhatever\n## IsLibrary: true\n## APIVersion: 101051\nLibWhatever.lua\n")

            main_lua = (
                'local FGT = { name = "FurysGuildToolset" }\n'
                'local function OnLoaded(_, addonName)\n'
                '    if addonName ~= FGT.name then return end\n'
                '    EVENT_MANAGER:UnregisterForEvent(FGT.name, EVENT_ADD_ON_LOADED)\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent(FGT.name, EVENT_ADD_ON_LOADED, OnLoaded)\n'
            )
            sub_lua = (
                'if not rawget(_G, "FurysAddonMenu") then\n'
                '    _G["FurysAddonMenu"] = { entries = {}, lib = 0 }\n'
                'end\n'
                'local function OnLoaded(_, name)\n'
                '    if name ~= "FurysAddonMenu" then return end\n'
                '    EVENT_MANAGER:UnregisterForEvent("FurysAddonMenu", EVENT_ADD_ON_LOADED)\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent("FurysAddonMenu", EVENT_ADD_ON_LOADED, OnLoaded)\n'
            )
            nested_lib_lua = (
                'local function OnLoaded(_, name)\n'
                '    if name ~= "LibWhatever" then return end\n'
                '    EVENT_MANAGER:UnregisterForEvent("LibWhatever", EVENT_ADD_ON_LOADED)\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent("LibWhatever", EVENT_ADD_ON_LOADED, OnLoaded)\n'
            )

            with open(os.path.join(main_dir, "FurysGuildToolset.lua"), "w", encoding="utf-8") as f1:
                f1.write(main_lua)
            with open(os.path.join(sub_dir, "FurysAddonMenu.lua"), "w", encoding="utf-8") as f2:
                f2.write(sub_lua)
            with open(os.path.join(nested_lib_dir, "LibWhatever.lua"), "w", encoding="utf-8") as f3:
                f3.write(nested_lib_lua)

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_main = analyze_lua_file("FurysGuildToolset/FurysGuildToolset.lua", main_lua, tmp_dir, ctx)
                res_sub = analyze_lua_file("FurysGuildToolset/FurysAddonMenu/FurysAddonMenu.lua", sub_lua, tmp_dir, ctx)
                res_lib = analyze_lua_file("FurysGuildToolset/libs/LibWhatever/LibWhatever.lua", nested_lib_lua, tmp_dir, ctx)

            for r_out in (res_main, res_sub, res_lib):
                self.assertNotIn("EVENT_ADD_ON_LOADED check does not match", r_out)
                self.assertNotIn("EVENT_ADD_ON_LOADED addonName", r_out)
                self.assertNotIn("EVENT_ADD_ON_LOADED missing", r_out)
                self.assertNotIn("Unregister EVENT_ADD_ON_LOADED", r_out)

    def test_29_addon_table_name_not_overwritten_by_other_table_name(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "CrutchAlerts")
            os.makedirs(os.path.join(addon_dir, "main"), exist_ok=True)
            with open(os.path.join(addon_dir, "CrutchAlerts.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: CrutchAlerts\n## APIVersion: 101051\nmain/CrutchAlerts.lua\nmain/Bosses.lua\n")

            main_lua = (
                'CrutchAlerts = {\n'
                '    BossHealthBar = {},\n'
                '    name = "CrutchAlerts",\n'
                '    version = "2.29.0",\n'
                '}\n'
                'local Crutch = CrutchAlerts\n'
                'local function OnAddOnLoaded(_, addonName)\n'
                '    if (addonName == Crutch.name) then\n'
                '        EVENT_MANAGER:UnregisterForEvent(Crutch.name, EVENT_ADD_ON_LOADED)\n'
                '    end\n'
                'end\n'
                'EVENT_MANAGER:RegisterForEvent(Crutch.name, EVENT_ADD_ON_LOADED, OnAddOnLoaded)\n'
            )
            bosses_lua = (
                'local bossEntry = {\n'
                '    name = "Invulnerable Boss 5",\n'
                '}\n'
                'local function ShowOrHideBars()\n'
                '    local name = "Example Boss 1"\n'
                '    if true then\n'
                '        name = "Invulnerable Boss 5"\n'
                '    end\n'
                'end\n'
            )
            with open(os.path.join(addon_dir, "main", "CrutchAlerts.lua"), "w", encoding="utf-8") as f1:
                f1.write(main_lua)
            with open(os.path.join(addon_dir, "main", "Bosses.lua"), "w", encoding="utf-8") as f2:
                f2.write(bosses_lua)

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res = analyze_lua_file("CrutchAlerts/main/CrutchAlerts.lua", main_lua, tmp_dir, ctx)

            self.assertNotIn("EVENT_ADD_ON_LOADED check does not match", res)
            self.assertNotIn("EVENT_ADD_ON_LOADED addonName", res)
            self.assertNotIn("EVENT_ADD_ON_LOADED missing", res)
            self.assertNotIn("Unregister EVENT_ADD_ON_LOADED", res)

    def test_30_partial_addon_name_pattern_matching_for_sv_and_globals(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context
        from src.esoui_manifest_xml_analyzer import analyze_manifest_file

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "Ramaladni_buff_debuff_tracker")
            os.makedirs(addon_dir, exist_ok=True)
            manifest_txt = (
                "## Title: Ramaladni's Buff & Debuff Tracker\n"
                "## APIVersion: 101051\n"
                "## SavedVariables: RamaladniTrackerSaved\n"
                "RamaladniMastery.lua\n"
                "Core.lua\n"
            )
            bad_manifest_txt = (
                "## Title: Ramaladni's Buff & Debuff Tracker\n"
                "## APIVersion: 101051\n"
                "## SavedVariables: TrackerSaved\n"
                "RamaladniMastery.lua\n"
            )
            with open(os.path.join(addon_dir, "Ramaladni_buff_debuff_tracker.txt"), "w", encoding="utf-8") as mf:
                mf.write(manifest_txt)

            good_lua = "RamaladniMastery = {\n    version = 1,\n}\n"
            bad_lua = "TrackerCore = {\n    version = 1,\n}\n"
            with open(os.path.join(addon_dir, "RamaladniMastery.lua"), "w", encoding="utf-8") as f1:
                f1.write(good_lua)
            with open(os.path.join(addon_dir, "Core.lua"), "w", encoding="utf-8") as f2:
                f2.write(bad_lua)

            ctx = collect_addon_context(tmp_dir)
            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_manifest_xml_analyzer.get_current_api_version", return_value="101051"
            ), patch("src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True), patch(
                "src.esoui_lua_analyzer.collect_dependency_globals", return_value={}
            ):
                res_mf_ok = analyze_manifest_file(
                    "Ramaladni_buff_debuff_tracker/Ramaladni_buff_debuff_tracker.txt", manifest_txt, ".txt", ctx
                )
                res_mf_bad = analyze_manifest_file(
                    "Ramaladni_buff_debuff_tracker/Ramaladni_buff_debuff_tracker.txt", bad_manifest_txt, ".txt", ctx
                )
                res_lua_ok = analyze_lua_file(
                    "Ramaladni_buff_debuff_tracker/RamaladniMastery.lua", good_lua, tmp_dir, ctx
                )
                res_lua_bad = analyze_lua_file(
                    "Ramaladni_buff_debuff_tracker/Core.lua", bad_lua, tmp_dir, ctx
                )

            self.assertNotIn("Non-unique / too short SavedVariables", res_mf_ok)
            self.assertIn("Non-unique / too short SavedVariables", res_mf_bad)
            self.assertNotIn("Non-unique / too short global variable", res_lua_ok)
            self.assertIn("Non-unique / too short global variable 'TrackerCore'", res_lua_bad)

    def test_31_guarded_addon_table_and_vanilla_eso_function_override(self):
        from src import esoui_ram_index
        from src.esoui_lua_analyzer import analyze_lua_file, collect_addon_context

        with tempfile.TemporaryDirectory() as tmp_dir:
            addon_dir = os.path.join(tmp_dir, "LeoAltholic")
            os.makedirs(addon_dir, exist_ok=True)
            with open(os.path.join(addon_dir, "LeoAltholic.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: LeoAltholic\n## APIVersion: 101051\nLeoAltholicInit.lua\nLeoAltholic.lua\n")

            init_lua = (
                "if not LeoAltholic then\n"
                "    LeoAltholic = LeoAltholic or {}\n"
                "end\n"
            )
            main_lua = (
                "local LA = LeoAltholic\n"
                "function ZO_QuestJournalNavigationEntry_OnMouseUp(label, button, upInside)\n"
                "    return true\n"
                "end\n"
            )
            with open(os.path.join(addon_dir, "LeoAltholicInit.lua"), "w", encoding="utf-8") as f1:
                f1.write(init_lua)
            with open(os.path.join(addon_dir, "LeoAltholic.lua"), "w", encoding="utf-8") as f2:
                f2.write(main_lua)

            ctx = collect_addon_context(tmp_dir)
            self.assertIn("LeoAltholic", ctx.get("all_global_tables"))

            with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch(
                "src.esoui_lua_analyzer._WIKI_EVENT_FILTER_SESSION_LOADED", True
            ), patch("src.esoui_lua_analyzer.collect_dependency_globals", return_value={}):
                res_init = analyze_lua_file("LeoAltholic/LeoAltholicInit.lua", init_lua, tmp_dir, ctx)
                res_main = analyze_lua_file("LeoAltholic/LeoAltholic.lua", main_lua, tmp_dir, ctx)

            self.assertNotIn("Global Variable Pollution", res_init)
            self.assertIn(
                "Overriding global ESO function 'ZO_QuestJournalNavigationEntry_OnMouseUp' (line 2): Use ZO_PreHook / ZO_PostHook / SecurePostHook instead",
                res_main,
            )
            self.assertNotIn("Global Function Pollution", res_main)

    def test_32_bbcode_truncation_closes_open_tags_and_grave_table_fields(self):
        from src import esoui_ram_index
        from src.esoui_ai_and_report import _enforce_report_char_limit, _render_final_bbcode_report
        from src.esoui_lua_analyzer import _check_lua_global_variable_leaks

        # 1. Verify [trunc.] never leaves dangling unclosed BBCode tags ([b], [u], [spoiler], [list], [SIZE])
        lb, rb = chr(91), chr(93)
        long_spoiler = (
            f'{lb}spoiler{rb}{lb}SIZE="2"{rb}'
            f'{lb}u{rb}{lb}b{rb}\\kpui_core\\kpui_settings_very_long_filename_path.lua{lb}/b{rb}{lb}/u{rb}\n'
            f'  12: leakedAlpha = 1\n'
            f'{lb}u{rb}{lb}b{rb}\\kpui_core\\kpui_other.lua{lb}/b{rb}{lb}/u{rb}\n'
            f'  99: leakedBeta = 2'
            f'{lb}/SIZE{rb}{lb}/spoiler{rb}'
        )
        shrunk = _enforce_report_char_limit(long_spoiler, max_chars=75)
        self.assertLessEqual(len(shrunk), 75)
        self.assertIn(f'{lb}trunc.{rb}{lb}/b{rb}{lb}/u{rb}', shrunk)
        self.assertEqual(shrunk.count(f'{lb}b{rb}'), shrunk.count(f'{lb}/b{rb}'))
        self.assertEqual(shrunk.count(f'{lb}u{rb}'), shrunk.count(f'{lb}/u{rb}'))
        self.assertEqual(shrunk.count(f'{lb}spoiler{rb}'), shrunk.count(f'{lb}/spoiler{rb}'))

        # 2. Verify full report > 9999 chars keeps balanced tags after hard truncation
        huge_pollution = [
            (f"KpuiCore/modules/kpui_settings_module_{i:03d}.lua", i + 10, f"leakedVar{i}", f"leakedVar{i} = {i}")
            for i in range(1, 260)
        ]
        report_data = {
            "zip_all_entries": ["KpuiCore/", "KpuiCore/KpuiCore.txt"],
            "zip_flagged_paths": set(),
            "zip_manifest_paths": {"KpuiCore/KpuiCore.txt"},
            "zip_tree_bbcode": "",
            "zip_violations": [],
            "global_var_pollution": huge_pollution,
            "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
            "best_practices": defaultdict(list),
        }
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
            tmp_rep = tf.name
        try:
            _render_final_bbcode_report(tmp_rep, "KpuiCore.zip", "2026-11-27 07:45:00 PM", report_data)
            with open(tmp_rep, "r", encoding="utf-8") as rf:
                rendered = rf.read()
            self.assertLessEqual(len(rendered), 9999)
            self.assertIn(f"{lb}trunc.{rb}", rendered)
            for tag in ("b", "u", "i", "spoiler", "list"):
                self.assertEqual(
                    rendered.lower().count(f"{lb}{tag}{rb}"),
                    rendered.lower().count(f"{lb}/{tag}{rb}"),
                    f"Unbalanced BBCode tag [{tag}] after truncation",
                )
        finally:
            if os.path.exists(tmp_rep):
                os.remove(tmp_rep)

        # 3. Verify Grave()/Present() table constructor fields {rects = {}, labels = {}} are not flagged as global tables or leaks
        from src.esoui_lua_analyzer import collect_addon_context

        grave_lua = (
            "local graves = {}\n"
            "local presentControls = {}\n"
            "local graveAnimations = {}\n"
            "local function Grave(unitTag)\n"
            "    graves[unitTag] = {rects = {}, labels = {}}\n"
            "    presentControls[unitTag] = {rects = {}, labels = {}}\n"
            "    for _, rect in ipairs(graveRects)\n"
            "    do\n"
            "        CreateControlFromElement(rect, graves[unitTag].rects, graves[unitTag].labels)\n"
            "    end\n"
            "    graveAnimations[unitTag] = 1000\n"
            "end\n"
        )
        with tempfile.TemporaryDirectory() as tmp_addon_dir:
            ca_dir = os.path.join(tmp_addon_dir, "CrutchAlerts")
            os.makedirs(os.path.join(ca_dir, "main"), exist_ok=True)
            os.makedirs(os.path.join(ca_dir, "drawing", "model"), exist_ok=True)
            with open(os.path.join(ca_dir, "CrutchAlerts.txt"), "w", encoding="utf-8") as mf:
                mf.write("## Title: CrutchAlerts\nmain/CrutchAlerts.lua\ndrawing/model/Model.lua\n")
            with open(os.path.join(ca_dir, "main", "CrutchAlerts.lua"), "w", encoding="utf-8") as f1:
                f1.write('CrutchAlerts = { name = "CrutchAlerts" }\n')
            with open(os.path.join(ca_dir, "drawing", "model", "Model.lua"), "w", encoding="utf-8") as f2:
                f2.write(grave_lua)
            ctx_ca = collect_addon_context(tmp_addon_dir)
            self.assertEqual(ctx_ca.get("all_global_tables"), {"CrutchAlerts"})

        issues = []
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True):
            _check_lua_global_variable_leaks(
                grave_lua,
                grave_lua.splitlines(),
                {"all_global_tables": {"CrutchAlerts"}, "saved_variables": set()},
                issues,
            )
        self.assertEqual(issues, [])

    def test_33_dds_texture_dimensions_and_compression(self):
        import struct
        import zipfile
        from src.esoui_ai_and_report import _check_zip_structure, _render_final_bbcode_report

        def _make_dds_bytes(width, height, four_cc=b"DXT5", has_fourcc=True):
            pf_flags = 0x4 if has_fourcc else 0x41
            header_part1 = struct.pack("<4sIIII", b"DDS ", 124, 0x1007, height, width)
            pad_mid = b"\x00" * 56
            pf_block = struct.pack("<II4sIIIII", 32, pf_flags, four_cc, 0, 0, 0, 0, 0)
            pad_end = b"\x00" * 20
            return header_part1 + pad_mid + pf_block + pad_end

        with tempfile.TemporaryDirectory() as tmp_dir:
            zp = os.path.join(tmp_dir, "TextureTestAddon.zip")
            with zipfile.ZipFile(zp, "w") as zf:
                zf.writestr("TextureTestAddon/TextureTestAddon.txt", "## Title: TextureTestAddon\n")
                zf.writestr("TextureTestAddon/tex_ok_dxt5.dds", _make_dds_bytes(64, 64, b"DXT5", True))
                zf.writestr("TextureTestAddon/tex_ok_dxt3.dds", _make_dds_bytes(128, 32, b"DXT3", True))
                zf.writestr("TextureTestAddon/tex_bp_dxt1.dds", _make_dds_bytes(64, 64, b"DXT1", True))
                zf.writestr("TextureTestAddon/Arrowhead.dds", _make_dds_bytes(64, 64, b"\x00\x00\x00\x00", False))
                zf.writestr("TextureTestAddon/Chevron.dds", _make_dds_bytes(64, 64, b"\x00\x00\x00\x00", False))
                zf.writestr("TextureTestAddon/tex_bad_size.dds", _make_dds_bytes(30, 32, b"DXT5", True))

            rep = {
                "zip_tree_bbcode": "",
                "zip_violations": [],
                "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                "best_practices": defaultdict(list),
            }
            _check_zip_structure(zp, rep)
            out_txt = os.path.join(tmp_dir, "report.txt")
            _render_final_bbcode_report(out_txt, "TextureTestAddon.zip", "2026-11-27 08:15:00 PM", rep)
            with open(out_txt, "r", encoding="utf-8") as rf:
                rendered = rf.read()

            self.assertIn("dds textures' height/width must be divisible by 4", rendered)
            self.assertIn(':mad: tex_bad_size.dds', rendered)
            self.assertIn('[u]Possible action: DDS texture compression should be DXT5 or DXT3[/u]', rendered)
            self.assertIn('[*] DXT1 [spoiler][SIZE="2"]\\tex_bp_dxt1.dds (64x64)[/SIZE][/spoiler]', rendered)
            self.assertIn(
                '[*] Uncompressed RGBA/RGB [spoiler][SIZE="2"]\\Arrowhead.dds (64x64), \\Chevron.dds (64x64)[/SIZE][/spoiler]',
                rendered,
            )
            self.assertEqual(rendered.count('[*] Uncompressed RGBA/RGB'), 1)
            self.assertNotIn(':mad: tex_ok_dxt5.dds', rendered)
            self.assertNotIn(':mad: tex_ok_dxt3.dds', rendered)

if __name__ == "__main__":
    unittest.main(verbosity=2)
