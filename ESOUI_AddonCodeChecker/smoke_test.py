#!/usr/bin/env python3
"""
Smoke-Test für die modulare Struktur von esoui_codecheck.py, das MMOUI v4 filelist.json Schema
und das kompakte BBCode-Reporting.
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
        self.assertIn("/v4/game/ESO/filelist.json", esoui_filelist_search.FILELIST_URL)
        self.assertIn("/downloads/info", esoui_config.ESO_ADDON_DOWNLOADLINK_SEARCH_PREFIX)
        self.assertIn("/downloads/dl", esoui_config.ESO_ADDON_DOWNLOADLINK_REPLACE_PREFIX)
        self.assertIn("showthread.php?t=10790", esoui_config.ESOUI_UPLOAD_RULES_URL)

    def test_02_download_io_parsers(self):
        from src.esoui_download_io import (
            is_authorized_esoui_url,
            parse_dl_command,
            parse_last_selection_spec,
        )

        self.assertEqual(parse_dl_command("dl 5026"), "5026")
        self.assertEqual(parse_dl_command("DL 123"), "123")
        self.assertIsNone(parse_dl_command("dl abc"))

        ranks, err = parse_last_selection_spec("1-3, 5, 10-11", 200)
        self.assertIsNone(err)
        self.assertEqual(ranks, list((1, 2, 3, 5, 10, 11)))

        _, err_oob = parse_last_selection_spec("201", 200)
        self.assertIsNotNone(err_oob)

        self.assertTrue(is_authorized_esoui_url(esoui_config_url := ("https://" + "://esoui.com")))
        self.assertTrue(len(esoui_config_url) > 10)
        self.assertFalse(is_authorized_esoui_url("https://" + "://example.com"))
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
                "id": 630,
                "title": "FCO ItemSaver",
                "author": "Baertram",
                "version": "2.8.4",
                "lastUpdate": 1791291956000,
                "addonStatus": "Live",
                "addons": [
                    {
                        "path": "FCOItemSaver",
                        "addOnVersion": "284",
                        "apiVersion": "101050 101051",
                        "requiredDependencies": ["LibAddonMenu-2.0>=43", "LibFilters-3.0>=350"],
                    }
                ],
            },
            {
                "id": 9999,
                "title": "Archived Mod",
                "author": "Baertram",
                "version": "1.0",
                "lastUpdate": 1799999999000,
                "addonStatus": "Archived",
                "addons": [{"path": "ArchivedMod", "addOnVersion": "", "apiVersion": "101030"}],
            },
        ]

    def test_03_v4_filelist_search_and_depends_annotation(self):
        from src.esoui_filelist_search import (
            annotate_depends_on_line,
            get_last_updated_addons,
            lookup_addon_metadata,
            search_addons,
        )

        sample_v4 = self._sample_v4_filelist()
        selected, top = get_last_updated_addons(spec="1-2", filelist=sample_v4)
        self.assertEqual(len(top), 3)
        self.assertEqual([str(x["id"]) for x in selected], ["630", "7"])

        meta = lookup_addon_metadata("630", filelist=sample_v4)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["title"], "FCO ItemSaver")
        self.assertEqual(meta["api_version"], "101050 101051")

        hits_author, _ = search_addons("Baertram", search_mode="author", filelist=sample_v4)
        self.assertEqual([str(x["id"]) for x in hits_author], ["630", "2343"])

        hits_dep, _ = search_addons("LibFilters-3.0", search_mode="dep", filelist=sample_v4)
        self.assertEqual([str(x["id"]) for x in hits_dep], ["630"])

        hits_api, _ = search_addons("101051", search_mode="api", filelist=sample_v4)
        self.assertEqual([str(x["id"]) for x in hits_api], ["630"])

        annotated, has_issue = annotate_depends_on_line(
            "## DependsOn: LibAddonMenu-2.0>=38 LibFilters-3.0 LibWhatever",
            filelist=sample_v4,
        )
        self.assertTrue(has_issue)
        self.assertIn("LibAddonMenu-2.0>=38", annotated)
        self.assertIn("current: 43", annotated)
        self.assertIn("LibFilters-3.0", annotated)
        self.assertIn("current: 350", annotated)
        self.assertIn("LibWhatever", annotated)
        self.assertIn("AddOnVersion unknown", annotated)

    def test_04_static_analyzers_and_compact_bbcode_report(self):
        from src import esoui_filelist_search, esoui_ram_index
        from src.esoui_ai_and_report import _build_bbcode_zip_list, _render_final_bbcode_report
        from src.esoui_manifest_xml_analyzer import analyze_file_content

        sample_v4 = self._sample_v4_filelist()
        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True), patch.object(
            esoui_filelist_search, "get_filelist", return_value=sample_v4
        ):
            ctx = {
                "has_bindings_xml": False,
                "xml_content": "",
                "all_global_tables": {"MyAddon"},
                "saved_variables": set(),
                "root_addon_manifests": ["MyAddon.addon"],
                "root_txt_manifests": [],
            }

            bad_manifest = "## Title: MyAddon\n## DependsOn: LibAddonMenu-2.0>=38 LibWhatever\n"
            res_man = analyze_file_content("MyAddon/MyAddon.addon", bad_manifest, addon_ctx=ctx)
            self.assertIn("FAIL", res_man)
            self.assertIn("current: 43", res_man)
            self.assertIn("AddOnVersion unknown", res_man)

            report_data = {
                "zip_all_entries": ["MyAddon/", "MyAddon/.git/", "MyAddon/MyAddon.addon", "MyAddon/Clean.lua"],
                "zip_flagged_paths": {"MyAddon/.git"},
                "zip_tree_bbcode": "",
                "zip_violations": ["Hidden, OS-metadata, or development folders/files found"],
                "critical": {"manifest": defaultdict(list), "lua": defaultdict(list), "xml": defaultdict(list)},
                "best_practices": defaultdict(list),
            }
            report_data["critical"]["manifest"]["Mandatory version check >= for non-optional dependencies missing/outdated"].append(
                ("MyAddon/MyAddon.addon", "2", "## DependsOn: LibAddonMenu-2.0>=38")
            )

            all_flagged = set(report_data["zip_flagged_paths"])
            for cat_rules in report_data["critical"].values():
                for entries in cat_rules.values():
                    for f_path, _, _ in entries:
                        all_flagged.add(f_path)
            tree_bb = _build_bbcode_zip_list(report_data["zip_all_entries"], all_flagged)
            report_data["zip_tree_bbcode"] = tree_bb

            self.assertIn(':mad: .git/', tree_bb)
            self.assertIn(':mad: MyAddon.addon', tree_bb)
            self.assertNotIn(':mad: Clean.lua', tree_bb)
            self.assertIn('SIZE="2"', tree_bb)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".txt", encoding="utf-8") as tf:
                tmp_path = tf.name
            try:
                _render_final_bbcode_report(tmp_path, "MyAddon.zip", "2026-11-14 10:20:00 PM", report_data)
                with open(tmp_path, "r", encoding="utf-8") as rf:
                    rendered = rf.read()
                self.assertIn("Addon check - report results", rendered)
                self.assertIn("Critical violations", rendered)
                self.assertIn('SIZE="2"', rendered)
                self.assertNotIn("PASS", rendered)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
