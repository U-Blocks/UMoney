![header](https://capsule-render.vercel.app/api?type=venom&height=150&color=gradient&text=UMoney&fontColor=0:8871e5,100:b678c4&fontSize=50&desc=A%20simple%20economy%20plug-in%20with%20%rich%20features.&descAlignY=80&descSize=20&animation=fadeIn)

****

<code><a href="https://github.com/umarurize/UMoney"><img height="25" src="https://github.com/umarurize/UMoney/blob/master/logo/logo.jpg" alt="UMoney" /></a>&nbsp;UMoney</code>

[![Minecraft - Version](https://img.shields.io/badge/minecraft-v1.21.60_(Bedrock)-black)](https://feedback.minecraft.net/hc/en-us/sections/360001186971-Release-Changelogs)
[![PyPI - Version](https://img.shields.io/pypi/v/endstone)](https://pypi.org/project/endstone)
![Total Git clones](https://img.shields.io/badge/dynamic/json?label=Total%20Git%20clones&query=$&url=https://cdn.jsdelivr.net/gh/umarurize/UMoney@master/clone_count.txt&color=brightgreen)

### Introductions
* **Rich features:** `money pay`, `money rank`, `money query (operator)`, `money change (operator)`, `money reset (operator)`
* **Full GUI:** Beautiful GUI forms for easy operation rather than commands.
* **Hot reload support:** Operators can edit/update `config.json` in game directly.
* **Localized languages support**

### Installation
[Optional pre-plugin] ZX_UI

Put `.whl` file into the endstone plugins folder, and then start the server. Enter the command `/um` to call out the main form.

### Download
Now, you can get the release version form this repo or <code><a href="https://www.minebbs.com/resources/umoney-jian-dan-shi-yong-qu-zhi-ling-hua-de-jing-ji-xi-tong.10622/"><img height="20" src="https://github.com/umarurize/umaru-cdn/blob/main/images/minebbs.png" alt="Minebbs" /></a>&nbsp;Minebbs</code>.

### File structure
```
Plugins/
├─ umoney/
│  ├─ config.json
│  ├─ money.json
```

### Configuration
UMoney allows operators to edit/update `config.json` through GUI forms with ease, here are just simple explanations for relevant configurations.

`money.json` just stores simple key-value pairs (key stands for player's name, value stands for player's money)

`config.json`
```json
{
    "default_money": 5000,  // initial money for a new player
    "money_rank_display_num": 15 // the player amount that the money rank can display
}
```

`money.json`
```json
{
    "umaru rize": 113733,
    "minokni": 1200,
    "TheDeerInDream": 10090,
    "SoleWool4183955": 112566,
    "BarrelGold90850": 6020
}
```

### Languages
- [x] `zh_CN`
- [x] `en_US`

Off course you can add your mother language to UMoney, just creat `XX_XX.json` (such as `ja_JP.json`) and translate value with reference to `en_US.json`.

You can also creat a PR to this repo to make your mother language one of the official languages of UMoney.

### API
```python
# get all players' money data
self.server.plugin_manager.get_plugin('umoney').api_get_money_data() -> dict

# get the target player's money
self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player_name: str) -> int

# get the richest player's money
# return [player_name: str, player_money: int]
self.server.plugin_manager.get_plugin('umoney').api_get_player_money_top() -> list

# get the poorest player's money
# return [player_name: str, player_money: int]
self.server.plugin_manager.get_plugin('umoney').api_get_player_money_bottom() -> list

# reset the target player's money
self.server.plugin_manager.get_plugin('umoney').api_set_player_money(player_name: str, money_to_set: int) -> None

# change the target player's money
# money_to change cannot be zero
self.server.plugin_manager.get_plugin('umoney').api_change_player_money(player_name: str, money_to_change: int) -> None
```

### Screenshots
You can view related screenshots of UMoney from images folder of this repo.


![](https://img.shields.io/badge/language-python-blue.svg) [![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)
