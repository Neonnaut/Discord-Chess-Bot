import os
from dotenv import load_dotenv

load_dotenv()

CHECK = '<:check:1001706162665832448>'
ERR = '<:err:1001706158786101269>'
WARN = '<:warn:1001706160438657109>'
INFO = '<:info:1003510951515005008>'

TOKEN = os.getenv("TOKEN")

GOOGLE_CLIENT = {
    "private_key": os.getenv("PRIVATE_KEY"),
    "client_email": os.getenv("CLIENT_EMAIL"),
    "token_uri": os.getenv("TOKEN_URI"),
}