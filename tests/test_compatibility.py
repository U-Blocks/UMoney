import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
LANG_MODULE_PATH = SRC_ROOT / "endstone_umoney" / "lang.py"
UMONEY_MODULE_PATH = SRC_ROOT / "endstone_umoney" / "umoney.py"


def load_module_from_path(module_name: str, module_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


lang_module = load_module_from_path("test_endstone_umoney_lang", LANG_MODULE_PATH)
DEFAULT_EN_US_LANG = lang_module.DEFAULT_EN_US_LANG
DEFAULT_ZH_CN_LANG = lang_module.DEFAULT_ZH_CN_LANG
load_lang_data = lang_module.load_lang_data


def load_umoney_module_with_endstone_stubs():
    endstone_module = types.ModuleType("endstone")
    endstone_module.ColorFormat = types.SimpleNamespace(
        RED="[RED]",
        YELLOW="[YELLOW]",
        GREEN="[GREEN]",
        WHITE="[WHITE]",
        BOLD="[BOLD]",
        LIGHT_PURPLE="[LIGHT_PURPLE]"
    )

    class Player:
        pass

    endstone_module.Player = Player

    plugin_module = types.ModuleType("endstone.plugin")

    class Plugin:
        def __init__(self):
            pass

    plugin_module.Plugin = Plugin

    event_module = types.ModuleType("endstone.event")
    event_module.PlayerJoinEvent = type("PlayerJoinEvent", (), {})
    event_module.event_handler = lambda func: func

    command_module = types.ModuleType("endstone.command")
    command_module.Command = type("Command", (), {})
    command_module.CommandSender = type("CommandSender", (), {})

    form_module = types.ModuleType("endstone.form")
    form_module.ActionForm = type("ActionForm", (), {})
    form_module.ModalForm = type("ModalForm", (), {})
    form_module.Dropdown = type("Dropdown", (), {})
    form_module.TextInput = type("TextInput", (), {})

    stubs = {
        "endstone": endstone_module,
        "endstone.plugin": plugin_module,
        "endstone.event": event_module,
        "endstone.command": command_module,
        "endstone.form": form_module
    }

    original_modules = {name: sys.modules.get(name) for name in stubs}
    original_package = sys.modules.get("endstone_umoney")
    original_lang = sys.modules.get("endstone_umoney.lang")
    original_cwd = os.getcwd()

    try:
        sys.modules.update(stubs)
        package_module = types.ModuleType("endstone_umoney")
        package_module.__path__ = [str(SRC_ROOT / "endstone_umoney")]
        sys.modules["endstone_umoney"] = package_module
        sys.modules["endstone_umoney.lang"] = lang_module

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            return load_module_from_path("test_endstone_umoney_umoney", UMONEY_MODULE_PATH)
    finally:
        os.chdir(original_cwd)

        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

        if original_package is None:
            sys.modules.pop("endstone_umoney", None)
        else:
            sys.modules["endstone_umoney"] = original_package

        if original_lang is None:
            sys.modules.pop("endstone_umoney.lang", None)
        else:
            sys.modules["endstone_umoney.lang"] = original_lang


class LangCompatibilityTest(unittest.TestCase):
    def test_empty_lang_dir_creates_complete_official_languages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lang_data = load_lang_data(temp_dir)

            self.assertEqual(lang_data["zh_CN"], DEFAULT_ZH_CN_LANG)
            self.assertEqual(lang_data["en_US"], DEFAULT_EN_US_LANG)

            zh_cn_file = Path(temp_dir) / "zh_CN.json"
            en_us_file = Path(temp_dir) / "en_US.json"

            self.assertEqual(json.loads(zh_cn_file.read_text(encoding="utf-8")), DEFAULT_ZH_CN_LANG)
            self.assertEqual(json.loads(en_us_file.read_text(encoding="utf-8")), DEFAULT_EN_US_LANG)

    def test_old_official_lang_files_are_completed_without_overwriting_values(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            zh_cn_file = Path(temp_dir) / "zh_CN.json"
            en_us_file = Path(temp_dir) / "en_US.json"

            zh_cn_file.write_text(
                json.dumps(
                    {
                        "your_money": "旧余额",
                        "money_change": "旧余额变动",
                        "main_form.title": "自定义标题"
                    },
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )
            en_us_file.write_text(
                json.dumps(
                    {
                        "your_money": "Old money",
                        "money_change": "Old money change",
                        "money": "Coins"
                    },
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

            lang_data = load_lang_data(temp_dir)

            self.assertEqual(lang_data["zh_CN"]["main_form.title"], "自定义标题")
            self.assertEqual(lang_data["zh_CN"]["your_money"], "旧余额")
            self.assertEqual(lang_data["zh_CN"]["money"], DEFAULT_ZH_CN_LANG["money"])
            self.assertEqual(lang_data["zh_CN"]["money_changed"], DEFAULT_ZH_CN_LANG["money_changed"])
            self.assertEqual(lang_data["en_US"]["money"], "Coins")
            self.assertEqual(lang_data["en_US"]["money_changed"], DEFAULT_EN_US_LANG["money_changed"])

            self.assertEqual(json.loads(zh_cn_file.read_text(encoding="utf-8")), lang_data["zh_CN"])
            self.assertEqual(json.loads(en_us_file.read_text(encoding="utf-8")), lang_data["en_US"])

    def test_custom_lang_files_are_loaded_without_being_completed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_file = Path(temp_dir) / "ja_JP.json"
            custom_file.write_text(json.dumps({"money": "所持金"}, ensure_ascii=False), encoding="utf-8")

            lang_data = load_lang_data(temp_dir)

            self.assertEqual(lang_data["ja_JP"], {"money": "所持金"})
            self.assertEqual(json.loads(custom_file.read_text(encoding="utf-8")), {"money": "所持金"})


class ConfigCompatibilityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.umoney_module = load_umoney_module_with_endstone_stubs()

    def test_old_money_rank_display_num_is_migrated(self):
        config_data, changed = self.umoney_module.normalize_config_data(
            {
                "default_money": 5000,
                "money_rank_display_num": 15
            }
        )

        self.assertTrue(changed)
        self.assertEqual(config_data["rank_list_display_num"], 15)
        self.assertEqual(config_data["money_rank_display_num"], 15)

    def test_missing_config_keys_are_defaulted(self):
        config_data, changed = self.umoney_module.normalize_config_data({"custom": "kept"})

        self.assertTrue(changed)
        self.assertEqual(config_data["default_money"], 5000)
        self.assertEqual(config_data["rank_list_display_num"], 15)
        self.assertEqual(config_data["custom"], "kept")


class DummyLogger:
    def __init__(self):
        self.warnings = []

    def warning(self, message):
        self.warnings.append(message)


class TextFallbackTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.umoney_module = load_umoney_module_with_endstone_stubs()

    def test_get_text_falls_back_and_warns_once_for_unknown_keys(self):
        plugin = self.umoney_module.umoney.__new__(self.umoney_module.umoney)
        plugin.lang_data = {
            "zh_CN": {"money": "余额"},
            "en_US": {"money_changed": "Money changed"}
        }
        plugin.logger = DummyLogger()
        plugin._missing_lang_keys_warned = set()
        player = types.SimpleNamespace(locale="zh_CN")

        self.assertEqual(plugin.get_text(player, "money"), "余额")
        self.assertEqual(plugin.get_text(player, "money_changed"), "Money changed")
        self.assertEqual(plugin.get_text(player, "missing.key"), "missing.key")
        self.assertEqual(plugin.get_text(player, "missing.key"), "missing.key")
        self.assertEqual(len(plugin.logger.warnings), 1)


if __name__ == "__main__":
    unittest.main()
