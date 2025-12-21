import os
import json

from endstone.plugin import Plugin
from endstone import ColorFormat, Player
from endstone.event import event_handler, PlayerJoinEvent
from endstone.command import Command, CommandSender
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput

from endstone_umoney.lang import load_lang_data


current_dir = os.getcwd()

first_dir = os.path.join(current_dir, "plugins", "umoney")

if not os.path.exists(first_dir):
    os.mkdir(first_dir)

money_data_file_path = os.path.join(first_dir, "money.json")

config_data_file_path = os.path.join(first_dir, "config.json")

lang_dir = os.path.join(first_dir, "lang")

if not os.path.exists(lang_dir):
    os.mkdir(lang_dir)


class umoney(Plugin):
    api_version = "0.10"

    def __init__(self):
        super().__init__()

        # load money data
        if not os.path.exists(money_data_file_path):
            with open(money_data_file_path, "w") as f:
                money_data = {}
                json_str = json.dumps(money_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(money_data_file_path, "r") as f:
                money_data = json.loads(f.read())

        self.money_data = money_data

        # load config data
        if not os.path.exists(config_data_file_path):
            with open(config_data_file_path, "w") as f:
                config_data = {
                    "default_money": 5000,
                    "rank_list_display_num": 15
                }
                json_str = json.dumps(config_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(config_data_file_path, "r") as f:
                config_data = json.loads(f.read())

        self.config_data = config_data

        # load lang
        self.lang_data = load_lang_data(lang_dir)

    commands = {
        "um": {
            "description": "Call out the main form of UMoney...",
            "usages": ["/um"],
            "permissions": ["umoney.command.um"]
        }
    }

    permissions = {
        "umoney.command.um": {
            "description": "Call out the main form of UMoney...",
            "default": True
        }
    }

    def on_enable(self):
        self.logger.info(
            f"{ColorFormat.YELLOW}"
            f"UMoney is enabled..."
        )

        self.register_events(self)

    def on_command(self, sender: CommandSender, command: Command, args: list[str]):
        if command.name == "um":
            if not isinstance(sender, Player):
                sender.send_message(
                    f"{ColorFormat.RED}"
                    f"This command can only be executed by a player..."
                )

                return

            money = self.money_data[sender.name]

            main_form = ActionForm(
                title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                      f"{self.get_text(sender, 'main_form.title')}",
                content=f"{ColorFormat.GREEN}"
                        f"{self.get_text(sender, 'money')}: "
                        f"{ColorFormat.WHITE}"
                        f"{money}\n"
                        f"\n"
                        f"{ColorFormat.GREEN}"
                        f"{self.get_text(sender, 'main_form.content')}",
            )

            main_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(sender, 'main_form.button.pay_online')}",
                icon="textures/ui/icon_steve",
                on_click=self.pay("online")
            )

            main_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(sender, 'main_form.button.pay_offline')}",
                icon="textures/ui/friend_glyph_desaturated",
                on_click=self.pay("offline")
            )

            main_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(sender, 'main_form.button.rank_list')}",
                icon="textures/ui/icon_best3",
                on_click=self.rank_list
            )

            if sender.is_op:
                main_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(sender, 'main_form.button.manage_players_money')}",
                    icon="textures/ui/op",
                    on_click=self.manage_players_money
                )

                main_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(sender, 'main_form.button.reload_config')}",
                    icon="textures/ui/icon_setting",
                    on_click=self.reload_configurations
                )

            if self.server.plugin_manager.get_plugin("zx_ui") is not None:
                main_form.on_close = self.back_to_zx_ui

                main_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(sender, 'button.back_to_zx_ui')}",
                    icon="textures/ui/refresh_light",
                    on_click=self.back_to_zx_ui
                )
            else:
                main_form.on_close = None

                main_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(sender, 'button.close')}",
                    icon="textures/ui/cancel",
                    on_click=None
                )

            sender.send_form(main_form)

    def pay(self, pay_type: str):
        def on_click(player: Player):
            player_name_list = []

            if pay_type == "online":
                for online_player in self.server.online_players:
                    if online_player.name != player.name:
                        player_name_list.append(online_player.name)
            else:
                for key in self.money_data.keys():
                    if self.server.get_player(key) is None:
                        player_name_list.append(key)

            if len(player_name_list) == 0:
                player.send_message(
                    f"{ColorFormat.RED}"
                    f"{self.get_text(player, f'pay.{pay_type}.message.fail')}"
                )

                return

            player_name_list.sort(key=lambda x:x[0].lower(), reverse=False)

            dropdown = Dropdown(
                label=f"{ColorFormat.GREEN}"
                      f"{self.get_text(player, 'pay_form.dropdown.label')}",
                options=player_name_list,
                default_index=0
            )

            money = self.money_data[player.name]

            textinput = TextInput(
                label=f"{ColorFormat.GREEN}"
                      f"{self.get_text(player, 'pay_form.textinput.label')}",
                placeholder=self.get_text(player, 'pay_form.textinput.placeholder').format(money)
            )

            pay_form = ModalForm(
                title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                      f"{self.get_text(player, f'pay_form.{pay_type}.title')}",
                controls=[
                    dropdown,
                    textinput
                ],
                submit_button=f"{ColorFormat.YELLOW}"
                              f"{self.get_text(player, 'pay_form.submit_button')}",
                on_close=self.back_to_main_form
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    money_to_pay = int(data[1])
                except:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                if money_to_pay > money or money_to_pay <= 0:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                target_player_name = player_name_list[data[0]]

                pay_check_form = ActionForm(
                    title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                          f"{self.get_text(p, 'pay_check_form.title')}",
                    content=f"{ColorFormat.GREEN}"
                            f"{self.get_text(p, 'pay_check_form.content').format(money_to_pay, target_player_name)}",
                    on_close=self.pay
                )

                pay_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'pay_check_form.button.confirm')}",
                    icon="textures/ui/check",
                    on_click=self.pay_check_confirm(target_player_name, money_to_pay)
                )

                pay_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'button.back_to_previous')}",
                    icon="textures/ui/refresh_light",
                    on_click=self.pay
                )

                p.send_form(pay_check_form)

            pay_form.on_submit = on_submit

            player.send_form(pay_form)

        return on_click

    def pay_check_confirm(self, target_player_name: str, money_to_pay: int):
        def on_click(player: Player):
            self.money_data[player.name] -= money_to_pay

            self.money_data[target_player_name] += money_to_pay

            self.save_money_data()

            player.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'pay.message.success1').format(money_to_pay, target_player_name)}"
            )

            player.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money_changed')}: "
                f"{ColorFormat.RED}"
                f"-{money_to_pay}\n"
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money')}: "
                f"{ColorFormat.WHITE}"
                f"{self.money_data[player.name]}"
            )

            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)

                target_player.send_message(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'pay.message.success2')}"
                )

                target_player.send_message(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'money_changed')}: "
                    f"{ColorFormat.GREEN}"
                    f"{money_to_pay}\n"
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(player, 'money')}: "
                    f"{ColorFormat.WHITE}"
                    f"{self.money_data[target_player_name]}"
                )

        return on_click

    def rank_list(self, player: Player):
        rank_list_form = ActionForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                  f"{self.get_text(player, 'rank_list_form.title')}",
            on_close=self.back_to_main_form
        )

        temple_list = list(self.money_data.items())

        temple_list.sort(key=lambda x:x[1], reverse=True)

        content = ""

        rank_list_display_num = self.config_data["rank_list_display_num"]

        if len(temple_list) < rank_list_display_num:
            range_len = len(temple_list)
        else:
            range_len = rank_list_display_num

        for i in range(range_len):
            content += (
                f"{ColorFormat.GREEN}"
                f"[{i+1}] {temple_list[i][0]}: "
                f"{ColorFormat.WHITE}"
                f"{temple_list[i][1]}\n"
            )

        for i in temple_list:
            if i[0] == player.name:
                content += (
                    f"\n"
                    f"{ColorFormat.GREEN}"
                    f"{self.get_text(player, 'rank_list_form.content').format(temple_list.index(i)+1)}"
                )

        rank_list_form.content = content

        rank_list_form.add_button(
            f"{ColorFormat.YELLOW}"
            f"{self.get_text(player, 'button.back_to_previous')}",
            icon="textures/ui/refresh_light",
            on_click=self.back_to_main_form
        )

        player.send_form(rank_list_form)

    def manage_players_money(self, player: Player):
        player_name_list = []

        for key, value in self.money_data.items():
            player_name_list.append(
                f"{key} - "
                f"{ColorFormat.GREEN}"
                f"{value}"
            )

        player_name_list.sort(key=lambda x:x[0].lower(), reverse=False)

        dropdown = Dropdown(
            label=f"{ColorFormat.GREEN}"
                  f"{self.get_text(player, 'manage_players_money_form.dropdown.label')}",
            options=player_name_list,
            default_index=0
        )

        manage_players_money_form = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                  f"{self.get_text(player, 'manage_players_money_form.title')}",
            controls=[dropdown],
            submit_button=f"{ColorFormat.YELLOW}"
                          f"{self.get_text(player, 'manage_players_money_form.submit_button')}",
            on_close=self.back_to_main_form
        )

        def on_submit(p: Player, json_str: str):
            data = json.loads(json_str)

            player_name = player_name_list[data[0]].split(" - ")[0]

            manage_players_money_sub_form = ActionForm(
                title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                      f"{self.get_text(p, 'manage_players_money_sub_form.title')}",
                content=f"{ColorFormat.GREEN}"
                        f"{self.get_text(p, 'manage_players_money_sub_form.content').format(player_name)}",
                on_close=self.manage_players_money
            )

            manage_players_money_sub_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(p, 'manage_players_money_sub_form.button.reset')}",
                icon="textures/ui/hammer_l",
                on_click=self.reset(player_name)
            )

            manage_players_money_sub_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(p, 'manage_players_money_sub_form.button.change')}",
                icon="textures/ui/hammer_l",
                on_click=self.change(player_name)
            )

            manage_players_money_sub_form.add_button(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(p, 'button.back_to_previous')}",
                icon="textures/ui/refresh_light",
                on_click=self.manage_players_money
            )

            p.send_form(manage_players_money_sub_form)

        manage_players_money_form.on_submit = on_submit

        player.send_form(manage_players_money_form)

    def reset(self, player_name: str):
        def on_click(player: Player):
            textinput = TextInput(
                label=f"{ColorFormat.GREEN}"
                      f"{self.get_text(player, 'reset_form.textinput.label1').format(player_name)}\n"
                      f"\n"
                      f"{self.get_text(player, 'reset_form.textinput.label2')}",
                placeholder=self.get_text(player, 'reset_form.textinput.placeholder')
            )

            reset_form = ModalForm(
                title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                      f"{self.get_text(player, 'reset_form.title')}",
                controls=[textinput],
                submit_button=f"{ColorFormat.YELLOW}"
                              f"{self.get_text(player, 'reset_form.submit_button')}",
                on_close=self.manage_players_money
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    reset_money = int(data[0])
                except:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                if reset_money < 0:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                reset_check_form = ActionForm(
                    title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                          f"{self.get_text(p, 'reset_check_form.title')}",
                    content=f"{ColorFormat.GREEN}"
                            f"{self.get_text(p, 'reset_check_form.content').format(player_name, reset_money)}",
                    on_close=self.reset(player_name)
                )

                reset_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'reset_check_form.button.confirm')}",
                    icon="textures/ui/check",
                    on_click=self.reset_check(player_name, reset_money)
                )

                reset_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'button.back_to_previous')}",
                    icon="textures/ui/refresh_light",
                    on_click=self.reset(player_name)
                )

                p.send_form(reset_check_form)

            reset_form.on_submit = on_submit

            player.send_form(reset_form)

        return on_click

    def reset_check(self, player_name: str, reset_money: int):
        def on_click(player: Player):
            self.money_data[player_name] = reset_money

            self.save_money_data()

            player.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'reset_check.message.success').format(player_name)}"
            )

            if self.server.get_player(player_name) is not None:
                target_player = self.server.get_player(player_name)

                target_player.send_message(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'money_reset')}\n"
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'money')}: "
                    f"{ColorFormat.WHITE}"
                    f"{self.money_data[player_name]}"
                )

        return on_click

    def change(self, player_name: str):
        def on_click(player: Player):
            textinput = TextInput(
                label=f"{ColorFormat.GREEN}"
                      f"{self.get_text(player, 'change_form.textinput.label1').format(player_name)}\n"
                      f"\n"
                      f"{self.get_text(player, 'change_form.textinput.label2')}",
                placeholder=self.get_text(player, 'change_form.textinput.placeholder')
            )

            change_form = ModalForm(
                title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                      f"{self.get_text(player, 'change_form.title')}",
                controls=[textinput],
                submit_button=f"{ColorFormat.YELLOW}"
                              f"{self.get_text(player, 'change_form.submit_button')}",
                on_close=self.manage_players_money
            )

            def on_submit(p: Player, json_str: str):
                data = json.loads(json_str)

                try:
                    change_money = int(data[0])
                except:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                if change_money == 0:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

                change_check_form = ActionForm(
                    title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                          f"{self.get_text(p, 'change_check_form.title')}",
                    on_close=self.change(player_name)
                )

                if change_money < 0:
                    change_check_form.content = (
                        f"{ColorFormat.GREEN}"
                        f"{self.get_text(p, 'chang_check_form.content.remove').format(abs(change_money), player_name)}"
                    )
                else:
                    change_check_form.content = (
                        f"{ColorFormat.GREEN}"
                        f"{self.get_text(p, 'chang_check_form.content.add').format(abs(change_money), player_name)}"
                    )

                change_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'change_check_form.confirm')}",
                    icon="textures/ui/check",
                    on_click=self.change_check(player_name, change_money)
                )

                change_check_form.add_button(
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(p, 'button.back_to_previous')}",
                    icon="textures/ui/refresh_light",
                    on_click=self.change(player_name)
                )

                p.send_form(change_check_form)

            change_form.on_submit = on_submit

            player.send_form(change_form)

        return on_click

    def change_check(self, player_name: str, change_money: int):
        def on_click(player: Player):
            self.money_data[player_name] += change_money

            self.save_money_data()

            player.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'change_check.message.success').format(player_name)}"
            )

            if self.server.get_player(player_name) is not None:
                target_player = self.server.get_player(player_name)

                message_to_send = (
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'money_changed')}: "
                )

                if change_money < 0:
                    message_to_send += (
                        f"{ColorFormat.RED}"
                        f"{change_money}\n"
                    )
                else:
                    message_to_send += (
                        f"{ColorFormat.GREEN}"
                        f"+{change_money}\n"
                    )

                message_to_send += (
                    f"{ColorFormat.YELLOW}"
                    f"{self.get_text(target_player, 'money')}: "
                    f"{ColorFormat.WHITE}"
                    f"{self.money_data[player_name]}"
                )

                target_player.send_message(message_to_send)

        return on_click

    def reload_configurations(self, player: Player):
        textinput1 = TextInput(
            label=f"{ColorFormat.GREEN}"
                  f"{self.get_text(player, 'reload_config_form.textinput1.label')}",
            placeholder=self.get_text(player, 'reload_config_form.textinput1.placeholder'),
            default_value=f"{self.config_data['default_money']}"
        )

        textinput2 = TextInput(
            label=f"{ColorFormat.GREEN}"
                  f"{self.get_text(player, 'reload_config_form.textinput2.label')}",
            placeholder=self.get_text(player, 'reload_config_form.textinput2.placeholder'),
            default_value=f"{self.config_data['rank_list_display_num']}"
        )

        reload_config_form = ModalForm(
            title=f"{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}"
                  f"{self.get_text(player, 'reload_config_form.title')}",
            controls=[
                textinput1,
                textinput2
            ],
            submit_button=f"{ColorFormat.YELLOW}"
                          f"{self.get_text(player, 'reload_config_form.submit_button')}",
            on_close=self.back_to_main_form
        )

        def on_submit(p: Player, json_str: str):
            data = json.loads(json_str)

            value_list = []

            try:
                for i in data:
                    value_list.append(int(i))
            except:
                p.send_message(
                    f"{ColorFormat.RED}"
                    f"{self.get_text(p, 'message.error')}"
                )

                return

            for i in value_list:
                if i <= 0:
                    p.send_message(
                        f"{ColorFormat.RED}"
                        f"{self.get_text(p, 'message.error')}"
                    )

                    return

            self.config_data["default_money"] = value_list[0]

            self.config_data["rank_list_display_num"] = value_list[1]

            self.save_config_data()

            p.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(p, 'reload_config.message.success')}"
            )

        reload_config_form.on_submit = on_submit

        player.send_form(reload_config_form)

    @event_handler
    def on_player_join(self, e: PlayerJoinEvent):
        if self.money_data.get(e.player.name) is None:
            self.money_data[e.player.name] = self.config_data["default_money"]

            self.save_money_data()

        e.player.send_message(
            f"{ColorFormat.YELLOW}"
            f"{self.get_text(e.player, 'money')}: "
            f"{ColorFormat.WHITE}"
            f"{self.money_data[e.player.name]}"
        )

    def save_money_data(self):
        with open(money_data_file_path, "w+") as f:
            json_str = json.dumps(self.money_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def save_config_data(self):
        with open(config_data_file_path, "w+") as f:
            json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def back_to_zx_ui(self, player: Player):
        player.perform_command("cd")

    def back_to_main_form(self, player: Player):
        player.perform_command("um")

    def get_text(self, player: Player, text_key: str) -> str:
        player_lang = player.locale

        try:
            if self.lang_data.get(player_lang) is None:
                text_value = self.lang_data["en_US"][text_key]
            else:
                if self.lang_data[player_lang].get(text_key) is None:
                    text_value = self.lang_data["en_US"][text_key]
                else:
                    text_value = self.lang_data[player_lang][text_key]

            return text_value
        except Exception as e:
            self.logger.error(
                f"{ColorFormat.RED}"
                f"{e}"
            )

            return text_key

    # API
    def api_get_money_data(self) -> dict:
        return self.money_data

    def api_get_player_money(self, player_name: str):
        if self.money_data.get(player_name) is None:
            self.logger.error(
                f"{ColorFormat.RED}"
                f"UMoney: player data not found..."
            )

            return

        return self.money_data[player_name]

    def api_get_richest_player_money_data(self) -> list:
        temple_list = list(self.money_data.items())

        temple_list.sort(key=lambda x:x[1], reverse=True)

        return [temple_list[0][0], temple_list[0][1]]

    def api_get_poorest_player_money_data(self) -> list:
        temple_list = list(self.money_data.items())

        temple_list.sort(key=lambda x:x[1], reverse=False)

        return [temple_list[0][0], temple_list[0][1]]

    def api_change_player_money(self, player_name: str, change_money: int) -> None:
        if self.money_data.get(player_name) is None:
            self.logger.error(
                f"{ColorFormat.RED}"
                f"UMoney: player data not found..."
            )

        if change_money == 0:
            self.logger.error(
                f"{ColorFormat.RED}"
                f"UMoney: Money to add or remove cannot be zero..."
            )

            return

        self.money_data[player_name] += change_money

        self.save_money_data()

        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)

            message_to_send = (
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money_changed')}: "
            )

            if change_money < 0:
                message_to_send += (
                    f"{ColorFormat.RED}"
                    f"{change_money}\n"
                )
            else:
                message_to_send += (
                    f"{ColorFormat.GREEN}"
                    f"+{change_money}\n"
                )

            message_to_send += (
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money')}: "
                f"{ColorFormat.WHITE}"
                f"{self.money_data[player_name]}"
            )

            player.send_message(message_to_send)

    def api_reset_player_money(self, player_name: str, reset_money: int) -> None:
        if self.money_data.get(player_name) is None:
            self.logger.error(
                f"{ColorFormat.RED}"
                f"UMoney: player data not found..."
            )

            return

        self.money_data[player_name] = reset_money

        self.save_money_data()

        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)

            player.send_message(
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money_reset')}\n"
                f"{ColorFormat.YELLOW}"
                f"{self.get_text(player, 'money')}: "
                f"{ColorFormat.WHITE}"
                f"{self.money_data[player_name]}"
            )
