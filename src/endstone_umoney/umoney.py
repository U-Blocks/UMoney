import os
import json
from endstone import ColorFormat, Player
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone.form import ActionForm, ModalForm, Dropdown, TextInput
from endstone.event import event_handler, PlayerJoinEvent

current_dir = os.getcwd()
first_dir = os.path.join(current_dir, 'plugins', 'umoney')
if not os.path.exists(first_dir):
    os.mkdir(first_dir)
money_data_file_path = os.path.join(first_dir, 'money.json')
config_data_file_path = os.path.join(first_dir, 'config.json')
menu_data_file_path = os.path.join(current_dir, 'plugins', 'zx_ui')

class umoney(Plugin):
    api_version = '0.6'

    def on_enable(self):
        # 加载 money.json
        if not os.path.exists(money_data_file_path):
            money_data = {}
            with open(money_data_file_path, 'w', encoding='utf-8') as f:
                json_str = json.dumps(money_data, indent=4, ensure_ascii=False)
                f.write(json_str)
        else:
            with open(money_data_file_path, 'r', encoding='utf-8') as f:
                money_data = json.loads(f.read())
        self.money_data = money_data
        # 加载 config.json
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
        self.register_events(self)
        self.logger.info(f'{ColorFormat.YELLOW}UMoney 已启用...')

    commands = {
        'um': {
            'description': '打开计分板经济菜单',
            'usages': ['/um'],
            'permissions': ['umoney.command.um']
        }
    }

    permissions = {
        'umoney.command.um': {
            'description': '打开计分板经济菜单',
            'default': True
        }
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]):
        if command.name == 'um':
            if not isinstance(sender, Player):
                sender.send_message(f'{ColorFormat.YELLOW}该命令只能由玩家执行...')
                return
            player = sender
            main_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}经济主表单',
                content=f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[player.name]}'
            )
            main_form.add_button(f'{ColorFormat.YELLOW}转账-在线玩家', icon='textures/ui/dressing_room_customization', on_click=self.send_money_to_online_player)
            main_form.add_button(f'{ColorFormat.YELLOW}转账-离线玩家', icon='textures/ui/friend_glyph_desaturated', on_click=self.send_money_to_offline_player)
            main_form.add_button(f'{ColorFormat.YELLOW}财富榜', icon='textures/ui/icon_best3', on_click=self.money_rank)
            if player.is_op:
                main_form.add_button(f'{ColorFormat.YELLOW}玩家经济管理', icon='textures/ui/op', on_click=self.money_admin)
                main_form.add_button(f'{ColorFormat.YELLOW}重载配置文件', icon='textures/ui/icon_setting', on_click=self.reload_config_data)
            if not os.path.exists(menu_data_file_path):
                main_form.add_button(f'{ColorFormat.YELLOW}关闭', icon='textures/ui/cancel', on_click=None)
                main_form.on_close = None
            else:
                main_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_menu)
                main_form.on_close = self.back_to_menu
            player.send_form(main_form)

    # 转账-在线玩家
    def send_money_to_online_player(self, player: Player):
        online_player_name_list = [online_player.name for online_player in self.server.online_players if online_player.name != player.name]
        if len(online_player_name_list) == 0:
            player.send_message(f'{ColorFormat.RED}转账失败： {ColorFormat.WHITE}当前没有可转账的玩家在线...')
            return
        player_money = self.money_data[player.name]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}选择玩家...',
            options=online_player_name_list
        )
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{self.money_data[player.name]}\n'
                  f'{ColorFormat.GREEN}输入转账金额...',
            placeholder='请输入一个正整数, 例如： 20'
        )
        send_money_to_online_player_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}转账-在线玩家',
            controls=[dropdown, textinput],
            submit_button=f'{ColorFormat.YELLOW}转账',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            try:
                money_to_send = int(data[1])
            except:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            if money_to_send <= 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            player_money = self.money_data[player.name]
            if player_money < money_to_send:
                player.send_message(f'{ColorFormat.RED}转账失败： {ColorFormat.WHITE}余额不足...')
                return
            target_player_name = online_player_name_list[data[0]]
            self.money_data[player.name] -= money_to_send
            self.money_data[target_player_name] += money_to_send
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}转账成功...')
            player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.RED}-{money_to_send}, '
                                f'{ColorFormat.YELLOW}余额： {self.money_data[player.name]}')
            # 防止目标转账玩家掉线
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                target_player.send_message(f'{ColorFormat.YELLOW}玩家 {ColorFormat.WHITE}{player.name} '
                                           f'{ColorFormat.YELLOW}向你转账...')
                target_player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.GREEN}+{money_to_send}, '
                                           f'{ColorFormat.YELLOW}余额： {self.money_data[target_player_name]}')
        send_money_to_online_player_form.on_submit = on_submit
        player.send_form(send_money_to_online_player_form)

    # 转账-离线玩家
    def send_money_to_offline_player(self, player: Player):
        online_player_name_list = [online_player.name for online_player in self.server.online_players]
        offline_player_name_list = [key for key in self.money_data.keys() if key not in online_player_name_list]
        if len(offline_player_name_list) == 0:
            player.send_message(f'{ColorFormat.RED}转账失败： {ColorFormat.WHITE}当前所有玩家都在线...')
            return
        player_money = self.money_data[player.name]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}选择玩家...',
            options=offline_player_name_list
        )
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{self.money_data[player.name]}\n'
                  f'{ColorFormat.GREEN}输入转账金额...',
            placeholder='请输入一个正整数, 例如： 20'
        )
        send_money_to_offline_player_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}转账-离线玩家',
            controls=[dropdown, textinput],
            submit_button=f'{ColorFormat.YELLOW}转账',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            try:
                money_to_send = int(data[1])
            except:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            if money_to_send <= 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            player_money = self.money_data[player.name]
            if player_money < money_to_send:
                player.send_message(f'{ColorFormat.RED}转账失败： {ColorFormat.WHITE}余额不足...')
                return
            target_player_name = offline_player_name_list[data[0]]
            self.money_data[player.name] -= money_to_send
            self.money_data[target_player_name] += money_to_send
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}转账成功...')
            player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.RED}-{money_to_send}, '
                                f'{ColorFormat.YELLOW}余额： {self.money_data[player.name]}')
            # 防止目标转账玩家上线
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                target_player.send_message(f'{ColorFormat.YELLOW}玩家 {ColorFormat.WHITE}{player.name} '
                                           f'{ColorFormat.YELLOW}向你转账...')
                target_player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.GREEN}+{money_to_send}, '
                                           f'{ColorFormat.YELLOW}余额： {self.money_data[target_player_name]}')
        send_money_to_offline_player_form.on_submit = on_submit
        player.send_form(send_money_to_offline_player_form)

    # 财富榜
    def money_rank(self, player: Player):
        money_rank_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}财富榜',
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
            money_rank_form.content += f'{ColorFormat.YELLOW}[{temple_list[i][0]}]： {ColorFormat.GREEN}{temple_list[i][1]}'
            if i != self.config_data['money_rank_display_num']:
                money_rank_form.content += '\n'
        money_rank_form.add_button('返回', icon='textures/ui/refresh_light', on_click=self.back_to_money_main_form)
        money_rank_form.on_close = self.back_to_money_main_form
        player.send_form(money_rank_form)

    # 管理玩家经济
    def money_admin(self, player: Player):
        money_admin_form = ActionForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}经济管理',
            content=f'{ColorFormat.GREEN}请选择操作...',
            on_close=self.back_to_money_main_form
        )
        money_admin_form.add_button(f'{ColorFormat.YELLOW}查询玩家经济', icon='textures/ui/magnifyingGlass', on_click=self.search_player_money)
        money_admin_form.add_button(f'{ColorFormat.YELLOW}重置玩家经济', icon='textures/ui/hammer_l', on_click=self.set_player_money)
        money_admin_form.add_button(f'{ColorFormat.YELLOW}变动玩家经济', icon='textures/ui/hammer_l', on_click=self.change_player_money)
        money_admin_form.add_button(f'{ColorFormat.YELLOW}重载玩家经济', icon='textures/ui/icon_setting', on_click=self.reload_money_data)
        money_admin_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_money_main_form)
        player.send_form(money_admin_form)

    # 查询玩家经济
    def search_player_money(self, player: Player):
        textinput = TextInput(
            label=f'{ColorFormat.GREEN}输入玩家名...',
            placeholder='请输入服务器中存在过的玩家名'
        )
        search_player_money_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}查询玩家经济',
            controls=[textinput],
            submit_button=f'{ColorFormat.YELLOW}查询',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            if len(data[0]) == 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            target_player_name = data[0]
            player_name_list = [key for key in self.money_data.keys()]
            if target_player_name not in player_name_list:
                player.send_message(f'{ColorFormat.RED}查询失败： {ColorFormat.WHITE}查无此人...')
                return
            target_player_money = self.money_data[target_player_name]
            search_player_money_result_form = ActionForm(
                title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}查询结果： {target_player_name}',
                content=f'{ColorFormat.GREEN}余额： {ColorFormat.WHITE}{target_player_money}',
                on_close=self.back_to_money_main_form
            )
            search_player_money_result_form.add_button(f'{ColorFormat.YELLOW}重置玩家经济', icon='textures/ui/hammer_l', on_click=self.set_player_money)
            search_player_money_result_form.add_button(f'{ColorFormat.YELLOW}变动玩家经济', icon='textures/ui/hammer_l', on_click=self.set_player_money)
            search_player_money_result_form.add_button(f'{ColorFormat.YELLOW}返回', icon='textures/ui/refresh_light', on_click=self.back_to_money_main_form)
            player.send_form(search_player_money_result_form)
        search_player_money_form.on_submit = on_submit
        player.send_form(search_player_money_form)

    # 重置玩家经济
    def set_player_money(self, player: Player):
        player_name_list = [key for key in self.money_data.keys()]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}选择玩家...',
            options=player_name_list
        )
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}输入重置金额...',
            placeholder='请输入任意整数，例如：20或0或-20'
        )
        money_set_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}经济重置',
            controls=[dropdown, textinput1],
            submit_button=f'{ColorFormat.YELLOW}重置',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            # 获取目标设置的玩家名
            target_player_name = player_name_list[data[0]]
            # 判断目标设置的金额是否为正确的数字类型
            try:
                money_to_set = int(data[1])
            except:
                player.send_message(f'{ColorFormat.RED}重置失败： {ColorFormat.WHITE}表单数据解析错误，请按提示正确填写...')
                return
            self.money_data[target_player_name] = money_to_set
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}重置成功...')
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                target_player.send_message(f'{ColorFormat.YELLOW}经济重置： '
                                           f'余额： {ColorFormat.WHITE}{self.money_data[target_player_name]}')
        money_set_form.on_submit = on_submit
        player.send_form(money_set_form)

    # 更改玩家经济
    def change_player_money(self, player: Player):
        player_name_list = [key for key in self.money_data.keys()]
        dropdown = Dropdown(
            label=f'{ColorFormat.GREEN}选择玩家...',
            options=player_name_list
        )
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}输入变动金额...',
            placeholder='请输入任意正整数或负整数，但不能为0， 例如：20或-20'
        )
        money_change_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}经济变动',
            controls=[dropdown, textinput1],
            submit_button=f'{ColorFormat.YELLOW}变动',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            # 获取目标设置的玩家名
            target_player_name = player_name_list[data[0]]
            try:
                money_to_change = int(data[1])
            except:
                player.send_message(f'{ColorFormat.RED}变动失败： {ColorFormat.WHITE}表单数据解析错误，请按提示正确填写...')
                return
            if money_to_change == 0:
                player.send_message(f'{ColorFormat.RED}变动失败： {ColorFormat.WHITE}表单数据解析错误，请按提示正确填写...')
                return
            self.money_data[target_player_name] += money_to_change
            self.save_money_data()
            player.send_message(f'{ColorFormat.YELLOW}变动成功...')
            if self.server.get_player(target_player_name) is not None:
                target_player = self.server.get_player(target_player_name)
                if money_to_change < 0:
                    target_player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.RED}-{abs(money_to_change)}, '
                                               f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[target_player_name]}')
                else:
                    target_player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.GREEN}+{money_to_change}, '
                                               f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[target_player_name]}')
        money_change_form.on_submit = on_submit
        player.send_form(money_change_form)

    # 重载玩家经济
    def reload_money_data(self, player: Player):
        with open(money_data_file_path, 'r', encoding='utf-8') as f:
            self.money_data = json.loads(f.read())
        player.send_message(f'{ColorFormat.YELLOW}重载玩家经济成功...')

    # 重载配置文件
    def reload_config_data(self, player: Player):
        textinput1 = TextInput(
            label=f'{ColorFormat.GREEN}当前玩家默认经济为： {ColorFormat.WHITE}{self.config_data["default_money"]}\n'
                  f'{ColorFormat.GREEN}（请输入一个正整数或 0, 例如： 1000 或 0...）',
            placeholder='请输入一个正整数, 例如： 1000 或 0...',
            default_value=f'{self.config_data["default_money"]}'
        )
        textinput2 =  TextInput(
            label=f'{ColorFormat.GREEN}当前财富榜显示数目为： {ColorFormat.WHITE}{self.config_data["money_rank_display_num"]}\n'
                  f'{ColorFormat.GREEN}（请输入一个 >=1 的正整数, 例如：15...）',
            placeholder='请输入一个 >=1 的正整数, 例如：15...',
            default_value=f'{self.config_data["money_rank_display_num"]}'
        )
        reload_config_data_form = ModalForm(
            title=f'{ColorFormat.BOLD}{ColorFormat.LIGHT_PURPLE}重载配置文件',
            controls=[textinput1, textinput2],
            submit_button=f'{ColorFormat.YELLOW}重载',
            on_close=self.back_to_money_main_form
        )
        def on_submit(player: Player, json_str):
            data = json.loads(json_str)
            # 判断所填写的是否为正确的数字类型
            try:
                update_default_money = int(data[0])
                update_money_rank_display_num = int(data[1])
            except:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            if update_default_money < 0:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            if update_money_rank_display_num < 1:
                player.send_message(f'{ColorFormat.RED}表单解析错误, 请按提示正确填写...')
                return
            self.config_data['default_money'] = update_default_money
            self.config_data['money_rank_display_num'] = update_money_rank_display_num
            self.save_config_data()
            player.send_message(f'{ColorFormat.YELLOW}重载配置文件成功...')
        reload_config_data_form.on_submit = on_submit
        player.send_form(reload_config_data_form)

    def back_to_money_main_form(self, player: Player):
        player.perform_command('um')

    # 返回 zx_ui
    def back_to_menu(self, player: Player):
        player.perform_command('cd')

    def save_money_data(self):
        with open(money_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.money_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    def save_config_data(self):
        with open(config_data_file_path, 'w+', encoding='utf-8') as f:
            json_str = json.dumps(self.config_data, indent=4, ensure_ascii=False)
            f.write(json_str)

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent):
        if self.money_data.get(event.player.name) is None:
            self.money_data[event.player.name] = self.config_data['default_money']
            self.save_money_data()
        event.player.send_message(f'{ColorFormat.YELLOW}余额： '
                                  f'{ColorFormat.WHITE}{self.money_data[event.player.name]}')

    # API
    # 获取所有玩家经济
    def api_get_money_data(self):
        return self.money_data
    # 获取指定玩家经济
    def api_get_player_money(self, player_name: str):
        player_money = self.money_data[player_name]
        return player_money

    # 获取最富有的玩家经济
    def api_get_player_money_top(self):
        temple_list = list(self.money_data.items())
        temple_list.sort(key=lambda x: x[1], reverse=True)
        player_money_top = [temple_list[0][0], temple_list[0][1]]
        return player_money_top

    # 获取最贫穷的玩家经济
    def api_get_player_money_bottom(self):
        temple_list = list(self.money_data.items())
        temple_list.sort(key=lambda x: x[1], reverse=True)
        player_money_bottom = [temple_list[0][-1], temple_list[0][-1]]
        return player_money_bottom

    # 重置玩家经济
    def api_set_player_money(self, player_name: str, money_to_set: int):
        self.money_data[player_name] = money_to_set
        self.save_money_data()
        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)
            player.send_message(f'{ColorFormat.YELLOW}经济重置： '
                                f'余额： {ColorFormat.WHITE}{self.money_data[player_name]}')

    # 变动玩家经济
    def api_change_player_money(self, player_name: str, money_to_change: int):
        if money_to_change == 0:
            self.logger.error(f'{ColorFormat.RED}UMoney： 经济变动不能为0...')
            return
        self.money_data[player_name] += money_to_change
        self.save_money_data()
        if self.server.get_player(player_name) is not None:
            player = self.server.get_player(player_name)
            if money_to_change < 0:
                player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.RED}-{abs(money_to_change)}, '
                                    f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[player_name]}')
            else:
                player.send_message(f'{ColorFormat.YELLOW}经济变动： {ColorFormat.GREEN}+{money_to_change}, '
                                    f'{ColorFormat.YELLOW}余额： {ColorFormat.WHITE}{self.money_data[player_name]}')