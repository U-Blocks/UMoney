import os
import json


def load_lang_data(lang_dir: str) -> dict:
    zh_CN_data_file_path = os.path.join(lang_dir, "zh_CN.json")
    en_US_data_file_path = os.path.join(lang_dir, "en_US.json")

    if not os.path.exists(zh_CN_data_file_path):
        with open(zh_CN_data_file_path, "w", encoding="utf-8") as f:
            zh_CN = {
                "money": "余额",
                "money_changed": "余额变动",
                "money_reset": "余额重置",

                "message.error": "表单解析错误, 请按提示正确填写...",

                "button.back_to_zx_ui": "返回",
                "button.close": "关闭",
                "button.back_to_previous": "返回",

                "main_form.title": "UMoney - 主表单",
                "main_form.content": "请选择操作...",
                "main_form.button.pay_online": "转账 - 在线",
                "main_form.button.pay_offline": "转账 - 离线",
                "main_form.button.rank_list": "排行榜",
                "main_form.button.manage_players_money": "管理玩家余额",
                "main_form.button.reload_config": "重载配置文件",

                "pay.online.message.fail": "没有可用于转账的在线玩家...",
                "pay.offline.message.fail": "没有可用于转账的离线玩家...",
                "pay_form.dropdown.label": "选择玩家...",
                "pay_form.textinput.label": "输入转账数目...",
                "pay_form.textinput.placeholder": "输入一个不超过 {0} 的整数...",
                "pay_form.online.title": "转账 - 在线",
                "pay_form.offline.title": "转账 - 离线",
                "pay_form.submit_button": "转账",
                "pay_check_form.title": "确认表单",
                "pay_check_form.content": "你确定转账 {0} 给玩家: {1} 吗?",
                "pay_check_form.button.confirm": "确认",
                "pay.message.success1": "转账 {0} 给玩家: {1} 成功...",
                "pay.message.success2": "玩家: {0} 转账了 {1} 给你...",

                "rank_list_form.title": "排行榜",
                "rank_list_form.content": "Your current rank is {0}...",

                "manage_players_money_form.dropdown.label": "选择玩家...",
                "manage_players_money_form.title": "管理玩家余额",
                "manage_players_money_form.submit_button": "选择",
                "manage_players_money_sub_form.title": "管理玩家余额",
                "manage_players_money_sub_form.content": "你正在对玩家: {0} 进行操作...",
                "manage_players_money_sub_form.button.reset": "重置",
                "manage_players_money_sub_form.button.change": "变动",

                "reset_form.textinput.label1": "你正在对玩家: {0} 进行操作...",
                "reset_form.textinput.label2": "输入重置数目...",
                "reset_form.textinput.placeholder": "输入一个正整数或0...",
                "reset_form.title": "重置",
                "reset_form.submit_button": "重置",
                "reset_check_form.title": "确认表单",
                "reset_check_form.content": "你确定将玩家: {0} 的余额重置为 {1}...",
                "reset_check_form.button.confirm": "确认",
                "reset_check.message.success": "重置玩家: {0} 的余额成功...",

                "change_form.textinput.label1": "你正在对玩家: {0} 进行操作...",
                "change_form.textinput.label2": "输入变动数目...",
                "change_form.textinput.placeholder": "输入一个非0整数...",
                "change_form.title": "变动",
                "change_form.submit_button": "变动",
                "change_check_form.title": "确认表单",
                "chang_check_form.content.remove": "你确定从玩家: {1} 的余额中移除 {0} 吗?",
                "chang_check_form.content.add": "你确定添加 {0} 至玩家: {1} 的余额中吗?",
                "change_check_form.confirm": "确认",
                "change_check.message.success": "变动玩家: {0} 的余额成功...",

                "reload_config_form.textinput1.label": "当前分配给一个新玩家的余额",
                "reload_config_form.textinput1.placeholder": "输入一个正整数...",
                "reload_config_form.textinput2.label": "当前排行榜所展示的数目",
                "reload_config_form.textinput2.placeholder": "输入一个正整数...",
                "reload_config_form.title": "重载配置文件",
                "reload_config_form.submit_button": "重载",
                "reload_config.message.success": "重载配置文件成功..."
            }
            json_str = json.dumps(zh_CN, indent=4, ensure_ascii=False)
            f.write(json_str)

    if not os.path.exists(en_US_data_file_path):
        with open(en_US_data_file_path, "w", encoding="utf-8") as f:
            en_US = {
                "money": "Money",
                "money_changed": "Money changed",
                "money_reset": "Money reset",

                "message.error": "",

                "button.back_to_zx_ui": "Back",
                "button.close": "Close",
                "button.back_to_previous": "Back to previous",

                "main_form.title": "UMoney - main form",
                "main_form.content": "Please select a function...",
                "main_form.button.pay_online": "Pay - online",
                "main_form.button.pay_offline": "Pay - offline",
                "main_form.button.rank_list": "Rank list",
                "main_form.button.manage_players_money": "Manage players' money",
                "main_form.button.reload_config": "Reload configurations",

                "pay.online.message.fail": "There are no online players available to pay...",
                "pay.offline.message.fail": "There are no offline players available to pay...",
                "pay_form.dropdown.label": "Select a player...",
                "pay_form.textinput.label": "Input payment amount...",
                "pay_form.textinput.placeholder": "Input a positive integer not more than {0}...",
                "pay_form.online.title": "Pay - online",
                "pay_form.offline.title": "Pay - offline",
                "pay_form.submit_button": "Pay",
                "pay_check_form.title": "Check form",
                "pay_check_form.content": "Are you sure to pay {0} to player: {1}?",
                "pay_check_form.button.confirm": "Confirm",
                "pay.message.success1": "Successfully paid {0} to player: {1}...",
                "pay.message.success2": "Player: {0} has paid {1} to you...",

                "rank_list_form.title": "Rank list",
                "rank_list_form.content": "Your current rank is {0}...",

                "manage_players_money_form.dropdown.label": "Select a player...",
                "manage_players_money_form.title": "Manage players' money",
                "manage_players_money_form.submit_button": "Select",
                "manage_players_money_sub_form.title": "Manage players money",
                "manage_players_money_sub_form.content": "You are operating on player: {0}...",
                "manage_players_money_sub_form.button.reset": "Reset",
                "manage_players_money_sub_form.button.change": "Change",

                "reset_form.textinput.label1": "You are operating on player: {0}...",
                "reset_form.textinput.label2": "Input reset amount...",
                "reset_form.textinput.placeholder": "Input a positive integer or zero...",
                "reset_form.title": "Reset",
                "reset_form.submit_button": "Reset",
                "reset_check_form.title": "Check form",
                "reset_check_form.content": "Are you sure to reset player: {0}'s money to {1}...",
                "reset_check_form.button.confirm": "Confirm",
                "reset_check.message.success": "Successfully reset player: {0}'s money...",

                "change_form.textinput.label1": "You are operating on player: {0}...",
                "change_form.textinput.label2": "Input change amount...",
                "change_form.textinput.placeholder": "Input a non-zero integer...",
                "change_form.title": "Change",
                "change_form.submit_button": "Change",
                "change_check_form.title": "Check form",
                "chang_check_form.content.remove": "Are you sure to remove {0} from player: {1}'s money?",
                "chang_check_form.content.add": "Are you sure to add {0} to player: {1}'s money?",
                "change_check_form.confirm": "Confirm",
                "change_check.message.success": "Successfully change player: {0}'s money...",

                "reload_config_form.textinput1.label": "The current default money for a new player",
                "reload_config_form.textinput1.placeholder": "Input a positive integer...",
                "reload_config_form.textinput2.label": "The current display num for rank list",
                "reload_config_form.textinput2.placeholder": "Input a positive integer...",
                "reload_config_form.title": "Reload configurations",
                "reload_config_form.submit_button": "Reload",
                "reload_config.message.success": "Successfully reloaded configurations..."
            }
            json_str = json.dumps(en_US, indent=4, ensure_ascii=False)
            f.write(json_str)

    lang_data = {}

    for lang in os.listdir(lang_dir):
        lang_name = lang.strip(".json")

        lang_file_path = os.path.join(lang_dir, lang)

        with open(lang_file_path, "r", encoding="utf-8") as f:
            lang_data[lang_name] = json.loads(f.read())

    return lang_data
