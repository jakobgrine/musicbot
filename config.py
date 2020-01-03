import json
import sys
import os

config_file = os.path.join(os.path.dirname(__file__), 'config.json')
default_config = {
    'active_extensions': [],
    'command_prefix': '',
    'delete_messages': True,
    'discord_token': ''
}


def load_config():
    try:
        with open(config_file, 'r') as f:
            config = default_config
            config.update(json.load(f))
            return config
    except IOError:
        with open(config_file, 'w+') as f:
            json.dump(default_config, f, indent=4)
        sys.exit()
