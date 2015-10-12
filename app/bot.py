import json, requests

from config import ACCESS_TOKEN, BASE_URL
from config import LEADERSHIP_BOT_ID, LEADERSHIP_GROUP_ID
from config import SAMSON_BOT_ID, SAMSON_GROUP_ID


def get_bot_id(group_id):
    if group_id == LEADERSHIP_GROUP_ID:
        bot_id = LEADERSHIP_BOT_ID
    else: bot_id = SAMSON_BOT_ID

    return bot_id


def list_members(group_id):
    url = BASE_URL + 'groups/' + group_id
    payload = {"token": ACCESS_TOKEN}

    r = requests.get(url, params = payload)

    data = json.loads(r.content)
    node = data['response']['members']

    members = {}
    for member in node:
        members[member['id']: member['nickname']]

    bot_id = get_bot_id(group_id)
    post(bot_id, members)


def remove_member(group_id, member_id):
    url = BASE_URL + '/groups/' + group_id + '/members/' + member_id + '/remove'
    payload = {"token": ACCESS_TOKEN}

    r = requests.post(url, params = payload)


def add_member(group_id, name, phone_number=None, email=None):
    if phone_number:
        phone_number = '+1' + phone_number

    url = BASE_URL + '/' + group_id + '/members/add'
    payload = {
    "token": ACCESS_TOKEN,
    "members":
        [
            {
                "nickname": name,
                "phone_number": phone_number,
                "email": email
            }
        ]
    }

    r = requests.post(url, params = payload)


def post(bot_id, message):
    url = BASE_URL + '/bots/post'
    payload = {
            'bot_id': bot_id,
            'text': message
    }

    r = requests.post(url, params = payload)


def get_callback(callback):
    f = open('callback.txt', 'w')
    for line in callback:
        f.write(line)
    f.close()

    data = json.loads(callback)
    node = data['response']
    group_id = node['group_id']
    text = node['text']

    if group_id == LEADERSHIP_GROUP_ID:
        bot_needed, command, message = parse_callback(text)

        if not bot_needed:
            return

        if command == 'post':
            post(SAMSON_BOT_ID, message)

    return callback


def parse_callback(text):
    if '#system' not in text.lower():
        return (False, None, None)

    bot_needed = True
    command_called = None
    command_text = None

    commands = ['add', 'list', 'post', 'remove']
    for command in commands:
        if command in text:
            command_called = command
            continue

    command_text = text.split(command_called,1)[1]

    return (bot_needed, command_called, command_text)
