import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")

KFACTOR = 24

CHECK = ':white_check_mark:'
ERR = ':x:'
WARN = ':warning:'
INFO = ':information_source:'

# KFACTOR = 24