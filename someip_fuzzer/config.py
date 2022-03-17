import configparser
import json

config = configparser.ConfigParser()
config.read("config.ini")

def read_json(s):
    global config
    config = json.loads(s)
