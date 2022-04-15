import os
from os import getenv
from dotenv import load_dotenv

admins = {}
load_dotenv()

# client vars
API_ID = int(getenv("API_ID", "6204272"))
API_HASH = getenv("API_HASH", "f935feb4ce106e741675d2e0894c6155")
BOT_TOKEN = getenv("BOT_TOKEN", "")
SESSION_NAME = getenv("SESSION_NAME", "BQBygAFtnpzGLax4XkOosc7VJ9PrUw01ztOEw_2X3diPamtrdF3luU5Ia09AWH2N08PX-pvZYTBEqFTkUyAQMfe9RCByVeYyp1iF5RvvRdcjKoxjituFkFNmoVLKE1nRJ2d8pqqVdqeMffFdDMZuC9IPClmrbYHS9p1FrLrkBeCuPdjMZg6cERuGMFRFXlOlBSfClRsuNusK13zJ7Nxg09zCk3Qjw7wsyjVy7NySth3N6rpXcATX91Llu5N63teQSkS7669n9fzWwsS2rPV08HMmWQhxKej9rDFplajw2kgun3sODr4PuMabpDKlqA-SNJZJAUL8DTlOmPQuJf5nifeWcKBElAA")

# mandatory vars
OWNER_USERNAME = getenv("OWNER_USERNAME", "ALONExBOY")
ALIVE_NAME = getenv("ALIVE_NAME", "ALONE")
ASSISTANT_NAME = getenv("ASSISTANT_NAME", "ALONEaxASSISTANT")
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1001563186923"))
BOT_USERNAME = getenv("BOT_USERNAME", "ALONEexROBOT")
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/PRONOI/ALONEexVC")
UPSTREAM_BRANCH = getenv("UPSTREM_BRANCH", "master")
DURATION_LIMIT = int(getenv("DURATION_LIMIT", "60"))
GROUP_SUPPORT = getenv("GROUP_SUPPORT", "")
UPDATES_CHANNEL = getenv("UPDATES_CHANNEL", "ALONE_SUPPORT")

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
