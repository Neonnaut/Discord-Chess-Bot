import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_CLIENT = os.getenv("DISCORD_CLIENT")
PREFIX = '!!'
TESTING = True if os.getenv("TESTING") == 'True' else False

# Emojis
CHECK = ':white_check_mark:'
ERR = ':x:'
WARN = ':warning:'
INFO = ':information_source:'