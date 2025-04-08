import os
import json

class lang():
    def load_lang(self, lang_dir: str) -> dict:
        zh_CN_data_file_path = os.path.join(lang_dir, 'zh_CN.json')
        en_US_data_file_path = os.path.join(lang_dir, 'en_US.json')

        if not os.path.exists(zh_CN_data_file_path):
            with open(zh_CN_data_file_path, 'w', encoding='utf-8') as f:
                zh_CN = {
                    'your_money': '你的余额',
                    'xx_money': "{0} 的余额",
                    'money_change': '经济变动',
                    'money_reset': '经济重置',
                    'message.type_error': '表单解析错误, 请按提示正确填写...',
                    'message.money_pay': '玩家 {0} 向你支付了 {1}...',
                    'button.back': '返回',

                    'main_form.title': 'UMoney - 主表单',
                    'main_form.content': '请选择操作...',
                    'main_form.button.money_pay_online': '经济转账 - 在线玩家',
                    'main_form.button.money_pay_offline': '经济转账 - 离线玩家',
                    'main_form.button.money_rank': '财富榜',
                    'main_form.button.money_manage': '管理玩家经济',
                    'main_form.button.reload_config': '重载配置文件',
                    'main_form.button.close': '关闭',
                    'main_form.button.back_to_zx_ui': '返回',

                    'money_pay_online_form.title': '经济转账 - 在线玩家',
                    'money_pay_online_form.dropdown.label': '选择玩家',
                    'money_pay_online_form.textinput.label': '输入转账金额',
                    'money_pay_online_form.textinput.placeholder': '请输入一个正整数...',
                    'money_pay_online_form.submit_button': '转账',
                    'money_pay_online.message.fail': '转账失败',
                    'money_pay_online.message.fail.reason_1': '没有可用于转账的在线玩家...',
                    'money_pay_online.message.fail.reason_2': '你的余额不足...',
                    'money_pay_online.message.success': '转账成功...',

                    'money_pay_offline_form.title': '经济转账 - 离线玩家',
                    'money_pay_offline_form.dropdown.label': '选择玩家',
                    'money_pay_offline_form.textinput.label': '输入转账金额',
                    'money_pay_offline_form.textinput.placeholder': '请输入一个正整数...',
                    'money_pay_offline_form.submit_button': '转账',
                    'money_pay_offline.message.fail': '转账失败',
                    'money_pay_offline.message.fail.reason_1': '没有可用于转账的离线玩家...',
                    'money_pay_offline.message.fail.reason_2': '你的余额不足...',
                    'money_pay_offline.message.success': '转账成功...',

                    'money_rank_form.title': '财富榜',

                    'money_manage_form.title': "管理玩家经济",
                    'money_manage_form.dropdown.label': '选择玩家',
                    'money_manage_form.submit_button': '查询',

                    'money_query_form.content': '请选择操作...',
                    'money_query_form.button.money_reset': '经济重置',
                    'money_query_form.button.money_change': '经济变动',

                    'money_reset_form.title': '经济重置',
                    'money_reset_form.textinput.label': '输入重置金额',
                    'money_reset_form.textinput.placeholder': '请输入一个整数...',
                    'money_reset_form.submit_button': '重置',
                    'money_reset.message.success': '重置成功...',

                    'money_change_form.title': '经济变动',
                    'money_change_form.textinput.label': '输入变动金额',
                    'money_change_form.textinput.placeholder': '请输入一个非0整数...',
                    'money_change_form.submit_button': '变动',
                    'money_change.message.success': '变动成功...',

                    'reload_config_form.title': '重载配置文件',
                    'reload_config_form.textinput1.label': '当前新玩家的默认经济',
                    'reload_config_form.textinput1.placeholder': '请输入一个正整数或0...',
                    'reload_config_form.textinput2.label': '当前财富榜展示玩家数量',
                    'reload_config_form.textinput2.placeholder': '请输入一个不小于1的正整数...',
                    'reload_config_form.submit_button': '重载',
                    'reload_config.message.success': '重载配置文件成功...',

                }
                json_str = json.dumps(zh_CN, indent=4, ensure_ascii=False)
                f.write(json_str)

        if not os.path.exists(en_US_data_file_path):
            with open(en_US_data_file_path, 'w', encoding='utf-8') as f:
                en_US = {
                    'your_money': 'Your money',
                    'xx_money': "{0}'s money",
                    'money_change': 'Money change',
                    'money_reset': 'Money reset',
                    'message.type_error': 'The form is parsed incorrectly, please follow the prompts to fill in correctly...',
                    'message.money_pay': 'Player {0} has paied {1} to you...',
                    'button.back': 'Back to previous',


                    'main_form.title': 'UMoney - main form',
                    'main_form.content': 'Please select a function...',
                    'main_form.button.money_pay_online': 'Money pay - online',
                    'main_form.button.money_pay_offline': 'Money pay - offline',
                    'main_form.button.money_rank': 'Money rank',
                    'main_form.button.money_manage': "Manage players' money",
                    'main_form.button.reload_config': 'Reload configurations',
                    'main_form.button.close': 'Close',
                    'main_form.button.back_to_zx_ui': 'Back to menu',

                    'money_pay_online_form.title': 'Money pay - online',
                    'money_pay_online_form.dropdown.label': 'Select a player',
                    'money_pay_online_form.textinput.label': 'Input the amount of money to pay',
                    'money_pay_online_form.textinput.placeholder': 'Input a positive integer...',
                    'money_pay_online_form.submit_button': 'Pay',
                    'money_pay_online.message.fail': 'Failed to pay',
                    'money_pay_online.message.fail.reason_1': 'there are no players online available for money pay...',
                    'money_pay_online.message.fail.reason_2': 'your money is not sufficient...',
                    'money_pay_online.message.success': 'Successfully pay...',

                    'money_pay_offline_form.title': 'Money pay - offline',
                    'money_pay_offline_form.dropdown.label': 'Select a player',
                    'money_pay_offline_form.textinput.label': 'Input the amount of money to pay',
                    'money_pay_offline_form.textinput.placeholder': 'Input a positive integer...',
                    'money_pay_offline_form.submit_button': 'Pay',
                    'money_pay_offline.message.fail': 'Failed to pay',
                    'money_pay_offline.message.fail.reason_1': 'there are no players offline available for money pay...',
                    'money_pay_offline.message.fail.reason_2': 'your money is not sufficient...',
                    'money_pay_offline.message.success': 'Successfully pay...',

                    'money_rank_form.title': 'Money rank',

                    'money_manage_form.title': "Manage players' money",
                    'money_manage_form.dropdown.label': 'Select a player',
                    'money_manage_form.submit_button': 'Query',

                    'money_query_form.content': 'Please select a function...',
                    'money_query_form.button.money_reset': 'Money reset',
                    'money_query_form.button.money_change': 'Money change',

                    'money_reset_form.title': 'Money reset',
                    'money_reset_form.textinput.label': 'Input the amount of money to reset',
                    'money_reset_form.textinput.placeholder': 'Input a integer...',
                    'money_reset_form.submit_button': 'Reset',
                    'money_reset.message.success': 'Successfully reset...',

                    'money_change_form.title': 'Money change',
                    'money_change_form.textinput.label': 'Input the amount of money to change',
                    'money_change_form.textinput.placeholder': 'Input a positive or negative integer...',
                    'money_change_form.submit_button': 'Change',
                    'money_change.message.success': 'Successfully change...',

                    'reload_config_form.title': 'Reload configurations',
                    'reload_config_form.textinput1.label': 'The current default money for a new player',
                    'reload_config_form.textinput1.placeholder': 'Input a positive integer or zero...',
                    'reload_config_form.textinput2.label': 'The current number of players shown on money rank',
                    'reload_config_form.textinput2.placeholder': 'Input a positive integer not less than 1...',
                    'reload_config_form.submit_button': 'Reload',
                    'reload_config.message.success': 'Successfully reload configurations...',
                }
                json_str = json.dumps(en_US, indent=4, ensure_ascii=False)
                f.write(json_str)

        lang_data = {}
        lang_list = os.listdir(lang_dir)
        for lang in lang_list:
            lang_name = lang.strip('.json')
            lang_data_file_path = os.path.join(lang_dir, lang)
            with open(lang_data_file_path, 'r', encoding='utf-8') as f:
                lang_data[lang_name] = json.loads(f.read())

        return lang_data