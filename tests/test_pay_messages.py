import importlib.util
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
    endstone_module.Player = type("Player", (), {})

    plugin_module = types.ModuleType("endstone.plugin")
    plugin_module.Plugin = type("Plugin", (), {})

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
    managed_modules = list(stubs) + ["endstone_umoney", "endstone_umoney.lang"]
    original_modules = {name: sys.modules.get(name) for name in managed_modules}
    original_cwd = os.getcwd()

    try:
        sys.modules.update(stubs)
        package_module = types.ModuleType("endstone_umoney")
        package_module.__path__ = [str(SRC_ROOT / "endstone_umoney")]
        sys.modules["endstone_umoney"] = package_module
        lang_module = load_module_from_path("endstone_umoney.lang", LANG_MODULE_PATH)

        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            os.mkdir("plugins")
            umoney_module = load_module_from_path("test_endstone_umoney_umoney", UMONEY_MODULE_PATH)

        return umoney_module, lang_module
    finally:
        os.chdir(original_cwd)

        for name, module in original_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module


class DummyLogger:
    def error(self, message):
        raise AssertionError(f"unexpected logger error: {message}")


class DummyPlayer:
    def __init__(self, name: str, locale: str):
        self.name = name
        self.locale = locale
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)


class DummyServer:
    def __init__(self, players: dict):
        self.players = players

    def get_player(self, player_name: str):
        return self.players.get(player_name)


class PayMessageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.umoney_module, cls.lang_module = load_umoney_module_with_endstone_stubs()

    def test_payee_success_message_is_formatted(self):
        plugin = self.umoney_module.umoney.__new__(self.umoney_module.umoney)
        plugin.money_data = {
            "payer": 100,
            "payee": 10
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            plugin.lang_data = self.lang_module.load_lang_data(temp_dir)
        plugin.logger = DummyLogger()
        plugin.save_money_data = lambda: None

        payer = DummyPlayer("payer", "zh_CN")
        payee = DummyPlayer("payee", "en_US")
        plugin.server = DummyServer({"payee": payee})

        plugin.pay_check_confirm("payee", 30)(payer)

        self.assertIn("Player: payer has paid 30 to you...", payee.messages[0])
        self.assertNotIn("{0}", payee.messages[0])
        self.assertNotIn("{1}", payee.messages[0])
        self.assertIn("Money: [WHITE]40", payee.messages[1])


if __name__ == "__main__":
    unittest.main()
