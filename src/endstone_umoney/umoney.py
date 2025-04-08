import os
import json

from endstone_umoney.lang import lang

from endstone import ColorFormat, Player
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone.event import event_handler, PlayerJoinEvent

current_dir = os.getcwd()
first_dir = os.path.join(current_dir, 'plugins', 'umoney')
if not os.path.exists(first_dir):
    os.mkdir(first_dir)

lang_dir = os.path.join(first_dir, 'lang')
if not os.path.exists(lang_dir):
    os.mkdir(lang_dir)

money_data_file_path = os.path.join(first_dir, 'money.json')
config_data_file_path = os.path.join(first_dir, 'config.json')
menu_data_file_path = os.path.join(current_dir, 'plugins', 'zx_ui')


class umoney(Plugin):
    api_version = '0.6'

    def on_enable(self):
        # Load money data
        if not os.path.exists(money_data_file_path):
            money_data = {}
            with open(money_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(money_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(money_data_file_path, 'r', encoding='utf-8') as f:
                money_data = json.loads(f.read())
        self.money_data = money_data

        # Load config data
        if not os.path.exists(config_data_file_path):
            config_data = {
                'default_money': 5000,
                'money_rank_display_num': 15
            }
            with open(config_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(config_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(config_data_file_path, 'r', encoding='utf-8') as f:
                config_data = json.loads(f.read())
        self.config_data = config_data

        # Load lang data
        self.lang_data = lang.load_lang(self, lang_dir)

        self.register_events(self)
        self.logger.info(f'{ColorFormat.YELLOW}UMoney is enabled...')

    commands = {
        'um': {
            'description': 'Call out main form of UMoney',
            'usages': ['/um'],
            'permissions': ['umoney.command.um']
        }
    }

    permissions = {
        'umoney.command.um': {
            'description': 'Call out main form of UMoney',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> None:
        if command.name == 'um':
            if not isinstance(sender, Player):
                sender.send_message(f'{ColorFormat.YELLOW}This command can only be executed by a player...')
                return
            player = sender
            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "main_form.title")}',
                content=f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                        f'{ColorFormat.WHITE}{self.money_data[player.name]}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "main_form.content")}'
            )
            main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.money_pay_online")}',
                                 icon='textures/ui/dressing_room_customization', on_click=self.send_money_to_online_player)
            main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.money_pay_offline")}',
                                 icon='textures/ui/friend_glyph_desaturated', on_click=self.send_money_to_offline_player)
            main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.money_rank")}',
                                 icon='textures/ui/icon_best3', on_click=self.money_rank)
            if player.is_op:
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.money_manage")}',
                                     icon='textures/ui/op', on_click=self.money_admin)
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.reload_config")}',
                                     icon='textures/ui/icon_setting', on_click=self.reload_config_data)
            if not os.path.exists(menu_data_file_path):
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.close")}',
                                     icon='textures/ui/cancel', on_click=None)
                main_form.on_close = None
            else:
                main_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "main_form.button.back_to_zx_ui")}',
                                     icon='textures/ui/refresh_light', on_click=self.back_to_menu)
                main_form.on_close = self.back_to_menu
            player.send_form(main_form)

    # Money pay - online
    def send_money_to_online_player(self, player: Player) -> None:
        online_player_name_list = [online_player.name for online_player in self.server.online_players if online_player.name != player.name]
        if len(online_player_name_list) == 0:
            player.send_message(f'{ColorFormat.RED}{self.get_text(player, "money_pay_online.message.fail")}: '
                                f'{ColorFormat.WHITE}{self.get_text(player, "money_pay_online.message.fail.reason_1")}')
            return
        online_player_name_list.sort(key=lambda x:x[0].lower(), reverse=False)
        player_money = self.money_data[player.name]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "money_pay_online_form.dropdown.label")}',
            options=online_player_name_list
        )
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                  f'{ColorFormat.WHITE}{self.money_data[player.name]}\n'
                  f'{ColorFormat.GREEN}{self.get_text(player, "money_pay_online_form.textinput.label")}',
            placeholder=f'{self.get_text(player, "money_pay_online_form.textinput.placeholder")}'
        )
        send_money_to_online_player_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_pay_online_form.title")}',
            controls=[dropdown, textinput],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "money_pay_online_form.submit_button")}',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            try:
                money_to_send = int(data[1])
            except ValueError:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            if money_to_send <= 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            player_money = self.money_data[player.name]
            if player_money < money_to_send:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "money_pay_online.message.fail")}: '
                                    f'{ColorFormat.WHITE}{self.get_text(player, "money_pay_online.message.fail.reason_2")}')
                return
            target_player_name = online_player_name_list[data[0]]
            self.money_data[player.name] -= money_to_send
            self.money_data[target_player_name] += money_to_send
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_pay_online.message.success")}')
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                f'{ColorFormat.RED}-{money_to_send}\n'
                                f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                f'{ColorFormat.WHITE}{self.money_data[player.name]}')
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                target_player.send_message(ColorFormat.YELLOW + self.get_text(player, "message.money_pay").format(player.name, money_to_send))
                target_player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                           f'{ColorFormat.GREEN}+{money_to_send}\n'
                                           f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                           f'{ColorFormat.WHITE}{self.money_data[target_player_name]}')
        send_money_to_online_player_form.on_submit = on_submit
        player.send_form(send_money_to_online_player_form)

    # Money pay - offline
    def send_money_to_offline_player(self, player: Player) -> None:
        online_player_name_list = [online_player.name for online_player in self.server.online_players]
        offline_player_name_list = [key for key in self.money_data.keys() if key not in online_player_name_list]
        if len(offline_player_name_list) == 0:
            player.send_message(f'{ColorFormat.RED}{self.get_text(player, "money_pay_offline.message.fail")}: '
                                f'{ColorFormat.WHITE}{self.get_text(player, "money_pay_offline.message.fail.reason_1")}')
            return
        offline_player_name_list.sort(key=lambda x:x[0].lower(), reverse=False)
        player_money = self.money_data[player.name]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "money_pay_offline_form.dropdown.label")}',
            options=offline_player_name_list
        )
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "your_money")}: '
                  f'{ColorFormat.WHITE}{self.money_data[player.name]}\n'
                  f'{ColorFormat.GREEN}{self.get_text(player, "money_pay_offline_form.textinput.label")}',
            placeholder=f'{self.get_text(player, "money_pay_offline_form.textinput.placeholder")}'
        )
        send_money_to_offline_player_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_pay_offline_form.title")}',
            controls=[dropdown, textinput],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "money_pay_offline_form.submit_button")}',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            try:
                money_to_send = int(data[1])
            except ValueError:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            if money_to_send <= 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            player_money = self.money_data[player.name]
            if player_money < money_to_send:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "money_pay_offline.message.fail")}: '
                                    f'{ColorFormat.WHITE}{self.get_text(player, "money_pay_offline.message.fail.reason_2")}')
                return
            target_player_name = offline_player_name_list[data[0]]
            self.money_data[player.name] -= money_to_send
            self.money_data[target_player_name] += money_to_send
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_pay_offline.message.success")}')
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                f'{ColorFormat.RED}-{money_to_send}\n'
                                f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                f'{ColorFormat.WHITE}{self.money_data[player.name]}')
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                target_player.send_message(ColorFormat.YELLOW + self.get_text(player, "message.money_pay").format(player.name, money_to_send))
                target_player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                           f'{ColorFormat.GREEN}+{money_to_send}\n'
                                           f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                           f'{ColorFormat.WHITE}{self.money_data[target_player_name]}')
        send_money_to_offline_player_form.on_submit = on_submit
        player.send_form(send_money_to_offline_player_form)

    # Money rank
    def money_rank(self, player: Player) -> None:
        money_rank_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_rank_form.title")}',
            content='',
            on_close=self.back_to_money_main_form
        )
        temple_list = list(self.money_data.items())
        temple_list.sort(key=lambda x:x[1], reverse=True)
        if len(temple_list) < self.config_data['money_rank_display_num']:
            index_range = len(temple_list)
        else:
            index_range = self.config_data['money_rank_display_num']
        for i in range(index_range):
            money_rank_form.content += f'{ColorFormat.YELLOW}[{temple_list[i][0]}]: {ColorFormat.GREEN}{temple_list[i][1]}'
            if i != self.config_data['money_rank_display_num']:
                money_rank_form.content += '\n'
        money_rank_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                   icon='textures/ui/refresh_light', on_click=self.back_to_money_main_form)
        money_rank_form.on_close = self.back_to_money_main_form
        player.send_form(money_rank_form)

    # Manage players' money
    def money_admin(self, player: Player) -> None:
        player_name_list = [player_name for player_name in self.money_data.keys()]
        player_name_list.sort(key=lambda x:x[0].lower(), reverse=False)
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "money_manage_form.dropdown.label")}',
            options=player_name_list
        )
        money_admin_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_manage_form.title")}',
            controls=[dropdown],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "money_manage_form.submit_button")}',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            target_player_name = player_name_list[data[0]]
            target_player_money = self.money_data[target_player_name]
            money_query_result_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{target_player_name}',
                content=ColorFormat.GREEN + self.get_text(player, "xx_money").format(target_player_name) + ': ' +
                        f'{ColorFormat.WHITE}{target_player_money}\n'
                        f'{ColorFormat.GREEN}{self.get_text(player, "money_query_form.content")}',
                on_close=self.money_admin
            )
            money_query_result_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "money_query_form.button.money_reset")}',
                                               icon='textures/ui/hammer_l', on_click=self.set_player_money(target_player_name, target_player_money))
            money_query_result_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "money_query_form.button.money_change")}',
                                               icon='textures/ui/hammer_l', on_click=self.change_player_money(target_player_name, target_player_money))
            money_query_result_form.add_button(f'{ColorFormat.YELLOW}{self.get_text(player, "button.back")}',
                                               icon='textures/ui/refresh_light', on_click=self.money_admin)
            player.send_form(money_query_result_form)
        money_admin_form.on_submit = on_submit
        player.send_form(money_admin_form)

    # Money reset
    def set_player_money(self, target_player_name: str, target_player_money: int):
        def on_click(player: Player):
            textinput = TextInput(
                label=ColorFormat.GREEN + self.get_text(player, "xx_money").format(target_player_name) + ': ' +
                      f'{ColorFormat.WHITE}{target_player_money}\n'
                      f'{ColorFormat.GREEN}{self.get_text(player, "money_reset_form.textinput.label")}',
                placeholder=f'{self.get_text(player, "money_reset_form.textinput.placeholder")}'
            )
            money_set_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_reset_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "money_reset_form.submit_button")}',
                on_close=self.money_admin
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    money_to_set = int(data[0])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                self.money_data[target_player_name] = money_to_set
                self.save_money_data()
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_reset.message.success")}')
                if self.server.get_player(target_player_name) is not None:
                    target_player = self.server.get_player(target_player_name)
                    target_player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_reset")}\n'
                                               f'{self.get_text(player, "your_money")}: '
                                               f'{ColorFormat.WHITE}{self.money_data[target_player_name]}')
            money_set_form.on_submit = on_submit
            player.send_form(money_set_form)
        return on_click

    # Money change
    def change_player_money(self, target_player_name: str, target_player_money: int):
        def on_click(player: Player):
            textinput = TextInput(
                label=ColorFormat.GREEN + self.get_text(player, "xx_money").format(target_player_name) + ': ' +
                      f'{ColorFormat.WHITE}{target_player_money}\n'
                      f'{ColorFormat.GREEN}{self.get_text(player, "money_change_form.textinput.label")}',
                placeholder=f'{self.get_text(player, "money_change_form.textinput.placeholder")}'
            )
            money_change_form = ModalForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "money_change_form.title")}',
                controls=[textinput],
                submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "money_change_form.submit_button")}',
                on_close=self.money_admin
            )
            def on_submit(player: Player, json_str: str):
                data = json.loads(json_str)
                try:
                    money_to_change = int(data[0])
                except ValueError:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                if money_to_change == 0:
                    player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                    return
                self.money_data[target_player_name] += money_to_change
                self.save_money_data()
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change.message.success")}')
                if self.server.get_player(target_player_name) is not None:
                    target_player = self.server.get_player(target_player_name)
                    if money_to_change < 0:
                        target_player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                                   f'{ColorFormat.RED}-{abs(money_to_change)}\n'
                                                   f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                                   f'{ColorFormat.WHITE}{self.money_data[target_player_name]}')
                    else:
                        target_player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                                   f'{ColorFormat.GREEN}+{money_to_change}\n'
                                                   f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                                   f'{ColorFormat.WHITE}{self.money_data[target_player_name]}')
            money_change_form.on_submit = on_submit
            player.send_form(money_change_form)
        return on_click

    # 重载配置文件
    def reload_config_data(self, player: Player) -> None:
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "reload_config_form.textinput1.label")}: '
                  f'{ColorFormat.WHITE}{self.config_data["default_money"]}',
            placeholder=f'{self.get_text(player, "reload_config_form.textinput1.placeholder")}',
            default_value=f'{self.config_data["default_money"]}'
        )
        textinput2 = TextInput(
            label=f'{ColorFormat.GREEN}{self.get_text(player, "reload_config_form.textinput2.label")}: '
                  f'{ColorFormat.WHITE}{self.config_data["money_rank_display_num"]}',
            placeholder=f'{self.get_text(player, "reload_config_form.textinput2.placeholder")}',
            default_value=f'{self.config_data["money_rank_display_num"]}'
        )
        reload_config_data_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}{self.get_text(player, "reload_config_form.title")}',
            controls=[textinput1, textinput2],
            submit_button=f'{ColorFormat.YELLOW}{self.get_text(player, "reload_config_form.submit_button")}',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str: str):
            data = json.loads(json_str)
            try:
                update_default_money = int(data[0])
                update_money_rank_display_num = int(data[1])
            except ValueError:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            if update_default_money < 0:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            if update_money_rank_display_num < 1:
                player.send_message(f'{ColorFormat.RED}{self.get_text(player, "message.type_error")}')
                return
            self.config_data['default_money'] = update_default_money
            self.config_data['money_rank_display_num'] = update_money_rank_display_num
            self.save_config_data()
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "reload_config.message.success")}')
        reload_config_data_form.on_submit = on_submit
        player.send_form(reload_config_data_form)

    def back_to_money_main_form(self, player: Player) -> None:
        player.perform_command('um')

    def back_to_menu(self, player: Player) -> None:
        player.perform_command('cd')

    # save money data
    def save_money_data(self) -> None:
        with open(money_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.money_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    # save config data
    def save_config_data(self) -> None:
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    # Get text
    def get_text(self, player: Player, text_key: str) -> str:
        try:
            lang = player.locale
            if self.lang_data.get(lang) is None:
                text_value = self.lang_data['en_US'][text_key]
            else:
                if self.lang_data[lang].get(text_key) is None:
                    text_value = self.lang_data['en_US'][text_key]
                else:
                    text_value = self.lang_data[lang][text_key]
            return text_value
        except:
            return text_key

    # Monitor players' joining game.
    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        if self.money_data.get(event.player.name) is None:
            self.money_data[event.player.name] = self.config_data['default_money']
            self.save_money_data()
        event.player.send_message(f'{ColorFormat.YELLOW}{self.get_text(event.player, "your_money")}: '
                                  f'{ColorFormat.WHITE}{self.money_data[event.player.name]}')

    # API
    # Get all player's moeny data
    def api_get_money_data(self) -> dict:
        return self.money_data

    # Get the target player's money
    def api_get_player_money(self, player_name: str) -> int:
        player_money = self.money_data[player_name]
        return player_money

    # Get the richest player's money
    def api_get_player_money_top(self) -> list:
        temple_list = list(self.money_data.items())
        temple_list.sort(key=lambda x: x[1], reverse=True)
        player_money_top = [temple_list[0][0], temple_list[0][1]]
        return player_money_top

    # Get the poorest player's money
    def api_get_player_money_bottom(self) -> list:
        temple_list = list(self.money_data.items())
        temple_list.sort(key=lambda x: x[1], reverse=True)
        player_money_bottom = [temple_list[0][-1], temple_list[0][-1]]
        return player_money_bottom

    # Reset the target player's money
    def api_set_player_money(self, player_name: str, money_to_set: int) -> None:
        self.money_data[player_name] = money_to_set
        self.save_money_data()
        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)
            player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_reset")}\n'
                                f'{self.get_text(player, "your_money")}: '
                                f'{ColorFormat.WHITE}{self.money_data[player_name]}')

    # Change the target player's money
    def api_change_player_money(self, player_name: str, money_to_change: int) -> None:
        if money_to_change == 0:
            self.logger.error(f'{ColorFormat.RED}UMoney: money change cannot be zero...')
            return
        self.money_data[player_name] += money_to_change
        self.save_money_data()
        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)
            if money_to_change < 0:
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                    f'{ColorFormat.RED}-{abs(money_to_change)}\n'
                                    f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                    f'{ColorFormat.WHITE}{self.money_data[player_name]}')
            else:
                player.send_message(f'{ColorFormat.YELLOW}{self.get_text(player, "money_change")}: '
                                    f'{ColorFormat.GREEN}+{money_to_change}\n'
                                    f'{ColorFormat.YELLOW}{self.get_text(player, "your_money")}: '
                                    f'{ColorFormat.WHITE}{self.money_data[player_name]}')