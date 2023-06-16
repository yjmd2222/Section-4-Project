'''
access info for many
'''
from os import getenv
from dotenv import load_dotenv

load_dotenv()

DB_HOST_NAME = getenv('DB_HOST_NAME', '')
DB_USER_NAME = getenv('DB_USER_NAME', '')
DB_PASSWORD = getenv('DB_PASSWORD', '')
DB_NAME = getenv('DB_NAME', '')
DB_PORT = str(getenv('DB_PORT', ''))
