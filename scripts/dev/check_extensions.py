import importlib, sys, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
	sys.path.insert(0, ROOT)

m = importlib.import_module('src.infrastructure.external.discord_bot')
print('module imported')
bot_cls = m.RPGDiscordBot('!', __import__('discord').Intents.default())
print(bot_cls.initial_extensions)
