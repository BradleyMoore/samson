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
    #f = open('callback.txt', 'w')
    #for line in callback:
    #    f.write(line)
    #f.close()

    group_id == callback['group_id']
    text = callback['text']

    if group_id == LEADERSHIP_GROUP_ID:
        bot_needed, command, message = parse_callback(text)

        if not bot_needed:
            return

        if command == 'post':
            post(SAMSON_BOT_ID, message)

    return callback


def parse_callback(text):
    words = text.split()
    if len(words) < 3:
        return (False, None, None)

    bots = ['#system']
    called_bot = None
    for bot in bots:
        if bot in words[0].lower():
            called_bot = bot

    commands = ['add', 'list', 'post', 'remove']
    called_command = None
    for command in commnads:
        if command in words[1]:
            called_command = command

    command_text = ' '.join(words[2:])

    return (bot_needed, command_called, command_text)
