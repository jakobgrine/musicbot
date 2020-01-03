import commands
import config

cfg = config.load_config()

bot = commands.Bot(command_prefix=cfg.get('command_prefix'),
                   help_command=commands.CustomHelpCommand())
bot.config = cfg

for ext in cfg.get('active_extensions', []):
    bot.load_extension(ext)

bot.run(cfg.get('discord_token'))
