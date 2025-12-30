<code><a href="https://github.com/umarurize/UMoney"><img height="25" src="./logo/logo.jpg" alt="UMoney" /></a>&nbsp;UMoney</code>

![Total Git clones](https://img.shields.io/badge/dynamic/json?label=Total%20Git%20clones&query=$&url=https://cdn.jsdelivr.net/gh/umarurize/UMoney@master/clone_count.txt&color=brightgreen)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/umarurize/UMoney/total)
![](https://img.shields.io/badge/language-python-blue.svg) 
[![GitHub License](https://img.shields.io/github/license/umarurize/UTP)](LICENSE)

***

### ✨ Introductions
* **Rich features:**
- [x] Money pay (online/offline)
- [x] Money rank list
- [x] Money management (operator) (change/reset)
* **Free of tedious file editing**
* **Support with full GUI forms**
* **Support with hot reloading**
* **Support with localized multi-language**

### 📦 Installation
**Tips**: *UMoney is adapted to all versions of Endstone*

<details>
<summary>Check pre-plugins</summary>

* **Optional pre-plugin**
  * [ZX_UI](https://www.minebbs.com/resources/zx-ui.9830/)

</details>

1. Ensure you have downloaded the correct version and installed all required pre-plugins
2. Place the `.whl` file into your server's `plugins` folder
3. Restart your server
4. Enter the command `/um` to call out the main form of UMoney

***

### 📄 File structure
```
plugins/
├─ umoney/
│  ├─ config.json
│  ├─ money.json
│  ├─ lang/
│  │  ├─ zh_CN.json
│  │  ├─ en_US.json
```

***

### ⚙️ Configuration
`config.json`
```json5
{
    "default_money": 5000,  // The default money for a new player
    "rank_list_display_num": 15 // The max num of players the money rank list can display
}
```

`money.json`
```json5
{
    "umaru rize": 113733,
    "minokni": 1200,
    "TheDeerInDream": 10090,
    "SoleWool4183955": 112566,
    "BarrelGold90850": 6020
}
```

***

### 🌎 Localized multi-language
* Currently supported localized languages for UMoney:
- [x] `zh_CN`
- [x] `en_US`
* How to add more languages to UMoney? Here we use Japanese for an example.
  * Create a file named `ja_JP.json` and place it into `lang` folder
  * Copy all key-value pairs from `en_US.json` and paste them into `ja_JP.json`
  * Refer to the English values and translate them all into Japanese, then save the file.
  * Restart your server, and you're all done!
* If you'd like your translated language to be included as one of the official languages of this plugin, feel free to shoot over a PR.

***

### 💪 API
```python
# Get all players' money data
self.server.plugin_manager.get_plugin('umoney').api_get_money_data() -> dict

# Get the target player's money
self.server.plugin_manager.get_plugin('umoney').api_get_player_money(player_name: str) -> int

# Get the richest player's money
# return [player_name: str, player_money: int]
self.server.plugin_manager.get_plugin('umoney').api_get_richest_player_money_data() -> list

# Get the poorest player's money
# return [player_name: str, player_money: int]
self.server.plugin_manager.get_plugin('umoney').api_get_poorest_player_money_data() -> list

# Reset the target player's money
self.server.plugin_manager.get_plugin('umoney').api_reset_player_money(player_name: str, money_to_set: int) -> None

# Change the target player's money
# money to change cannot be zero
self.server.plugin_manager.get_plugin('umoney').api_change_player_money(player_name: str, money_to_change: int) -> None
```

***

### 📷Screenshots
You can view related screenshots of UMoney from images folder of this repo.



