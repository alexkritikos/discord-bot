import os

from dotenv import load_dotenv

load_dotenv()

def to_multi_line_text(filename):
    with open(filename) as file:
        multi_line_text = "\n".join(line.strip() for line in file)
    return multi_line_text

def filter_bots(member):
    return member.bot

def set_activity_env_vars(activity_type, activity_name):
    os.environ['ACTIVITY_TYPE'] = activity_type
    os.environ['ACTIVITY_NAME'] = activity_name