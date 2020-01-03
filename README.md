<a href="https://discordapp.com/">
  <img align="right" width="200" src="https://discordapp.com/assets/2c21aeda16de354ba5334551a883b481.png" alt="Discord">
<a/>

## Description
This is just a simple music bot.

## Installation
1. Clone this repository: `git clone https://github.com/jakobgrine/musicbot.git`
2. Change into the directory: `cd musicbot`
3. Install the requirements: `pip install -r requirements.txt`
4. Start the discord bot to generate the configuration file: `python main.py`
5. Configure the discord bot as described [below](#configuration)
6. Restart the discord bot: `python main.py`

## Configuration
Edit the configuration file `config.json` to configure the discord bot.

Name | Meaning
--- | ---
`active_extensions` | Which extensions are loaded by default (you usually do not have to edit this)
`command_prefix` | No special meaning for now
`delete_messages` | Whether the bot deletes its messages after a certain amount of time
`discord_token` | Discord token
