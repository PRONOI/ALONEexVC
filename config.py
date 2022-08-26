import os
from os import getenv
from dotenv import load_dotenv

admins = {}
load_dotenv()

# client vars
API_ID = int(getenv("API_ID", ""))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")
SESSION_NAME = getenv("SESSION_NAME", "")

# mandatory vars
OWNER_USERNAME = getenv("OWNER_USERNAME", "Xd_LyF")
ALIVE_NAME = getenv("ALIVE_NAME", "⏤͟͟͞Ftw")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "ALONEaxASSISTANT")
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", ""))
BOT_USERNAME = getenv("BOT_USERNAME", "ALONEexROBOT")
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/PRONOI/ALONEexVC")
UPSTREAM_BRANCH = getenv("UPSTREM_BRANCH", "master")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60"))
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "Xd_About")

# database, decorators, handlers mandatory vars
MONGODB_URL = getenv(" ")
COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ ! . ^ • * # ? ~ $").split())
OWNER_ID = list(map(int, getenv("OWNER_ID", "1063334882").split()))
SUDO_USERS = list(map(int, getenv("SUDO_USERS", "1063334882").split()))

# image resources vars
IMG_1 = getenv("IMG_1", "https://telegra.ph/file/22f95cbff261624946770.jpg")
IMG_2 = getenv("IMG_2", "https://telegra.ph/file/c1ba55b4d8c5f607a04b3.jpg")
IMG_3 = getenv("IMG_3", "https://telegra.ph/file/22f95cbff261624946770.jpg")
IMG_4 = getenv("IMG_4", "https://telegra.ph/file/c1ba55b4d8c5f607a04b3.jpg")
IMG_5 = getenv("IMG_5", "https://telegra.ph/file/54afe09fb4f94bc3a564b.jpg")
ALIVE_IMG = getenv("ALIVE_IMG", "https://telegra.ph/file/305106fb7bf6ad740c830.jpg")

if str(getenv("LOG_SESSION")).strip() == "":
    LOG_SESSION = str(None)
else:
    LOG_SESSION = str(getenv("LOG_SESSION"))
