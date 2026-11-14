#!/usr/bin/env python3
"""
Smoke-Test für die modulare Struktur von esoui_codecheck.py und das src/-Paket.
Ausführung im Projekt-Hauptverzeichnis:
    python smoke_test.py
"""

import unittest
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
        self.assertEqual(esoui_config.ESOUI_LATEST_MAX_ITEMS, 200)
        self.assertIn(".lua", esoui_config.ALLOWED_EXTENSIONS)
        self.assertIn(".exe", esoui_config.BLOCKED_EXECUTABLE_EXTENSIONS)

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
        self.assertEqual(ranks, [1, 2, 3, 5, 10, 11])

        _, err_oob = parse_last_selection_spec("201", 200)
        self.assertIsNotNone(err_oob)

        self.assertTrue(is_authorized_esoui_url("https://esoui.com"))
        self.assertFalse(is_authorized_esoui_url("https://example.com"))
    def test_03_filelist_search_and_author_filter(self):
        from src.esoui_filelist_search import (
            get_last_updated_addons,
            lookup_addon_metadata,
            search_addons,
        )

        sample_list = [
            {
                "id": "101",
                "title": "LibAddonMenu-2.0",
                "author": "sirinsidiator",
                "version": "2.0r38",
                "apiversion": "101043",
                "lastUpdate": 1731500000,
                "status": "Live",
                "dependencies": ["LibStub"],
            },
            {
                "id": "202",
                "title": "Master Merchant",
                "author": "Sharlikran, Baertram",
                "version": "3.8.12",
                "apiversion": ["101042", "101043"],
                "lastUpdate": 1731600000,
                "status": "Live",
                "dependencies": ["LibAddonMenu-2.0", "LibGuildRoster"],
            },
            {
                "id": "303",
                "title": "Outdated Mod",
                "author": "Baertram",
                "version": "1.0",
                "apiversion": "101030",
                "lastUpdate": 1731700000,
                "status": "Archived",
                "dependencies": [],
            },
        ]

        selected, top = get_last_updated_addons(spec="1-2", filelist=sample_list)
        self.assertEqual(len(top), 2)
        self.assertEqual([x["id"] for x in selected], ["202", "101"])

        meta = lookup_addon_metadata("202", filelist=sample_list)
        self.assertIsNotNone(meta)
        self.assertEqual(meta["title"], "Master Merchant")
        self.assertEqual(meta["api_version"], "101042, 101043")

        hits_author, stage_a = search_addons("Baertram", search_mode="author", filelist=sample_list)
        self.assertEqual(stage_a, 1)
        self.assertEqual([x["id"] for x in hits_author], ["202"])

        hits_dep, stage_d = search_addons("LibAddonMenu-2.0", search_mode="dep", filelist=sample_list)
        self.assertEqual(stage_d, 1)
        self.assertEqual([x["id"] for x in hits_dep], ["202"])

        hits_api, stage_api = search_addons("101042", search_mode="api", filelist=sample_list)
        self.assertEqual(stage_api, 1)
        self.assertEqual([x["id"] for x in hits_api], ["202"])

        hits_api_neg, _ = search_addons("!101042", search_mode="api", filelist=sample_list)
        self.assertEqual([x["id"] for x in hits_api_neg], ["101"])

    def test_04_static_analyzers_lua_manifest_xml(self):
        from src import esoui_ram_index
        from src.esoui_manifest_xml_analyzer import analyze_file_content

        with patch.object(esoui_ram_index, "ESOUI_INDEX_BUILT", True):
            ctx = {
                "has_bindings_xml": False,
                "xml_content": "",
                "all_global_tables": {"MyAddon"},
                "saved_variables": set(),
                "root_addon_manifests": ["MyAddon.addon"],
                "root_txt_manifests": [],
            }

            bad_lua = 'local lib = LibStub("LibAddonMenu-2.0")\n'
            res_lua = analyze_file_content("MyAddon/MyAddon.lua", bad_lua, addon_ctx=ctx)
            self.assertIn("[STATUS] FAIL", res_lua)
            self.assertIn("Deprecated LibStub Usage", res_lua)

            bad_manifest = "## Title: MyAddon\n## OptionalDependsOn: LibAddonMenu-2.0>=38\n"
            res_man = analyze_file_content("MyAddon/MyAddon.addon", bad_manifest, addon_ctx=ctx)
            self.assertIn("[STATUS] FAIL", res_man)
            self.assertIn("OptionalDependsOn", res_man)

            bad_xml = "<GuiXml><Controls><Control><OnInitialized>leakedVar = 123</OnInitialized></Control></Controls></GuiXml>"
            res_xml = analyze_file_content("MyAddon/MyAddon.xml", bad_xml, addon_ctx=ctx)
            self.assertIn("[STATUS] FAIL", res_xml)
            self.assertIn("leakedVar", res_xml)


if __name__ == "__main__":
    unittest.main(verbosity=2)
