import json, requests

from config import EJECTOMATIC_ACCESS_TOKEN, MOORE_ACCESS_TOKEN, BASE_URL
from config import LEADERSHIP_BOT_ID, LEADERSHIP_GROUP_ID
from config import SAMSON_BOT_ID, SAMSON_GROUP_ID
from config import TEST_BOT_ID, TEST_GROUP_ID


class Callback(object):
    def __init__(self, callback):
        self.callback = callback

    def parse_callback(self, groups):
        text = self.callback['text']
        words = text.split()
        if len(words) < 2:
            return

        parsed_callback = {}

        potential_bot = words[0].lower()
        parsed_callback['group'] = self.determine_called_group(groups, potential_bot)

        if parsed_callback['group']:
            potential_command = words[1].lower()
            parsed_callback['command'] = self.determine_called_command(potential_command)
        else:
            return

        if parsed_callback['command'] and len(words) >= 3:
            potential_text = words[2:]
            parsed_callback['message'] = self.dertermine_command_text(potential_text)
        else:
            parsed_callback['message'] = None

        return parsed_callback

    def determine_called_group(self, groups, potential_bot):
        for group in groups:
            if potential_bot == group.bot.name:
                return group

    def determine_called_command(self, potential_command):
        commands = ['add', 'list', 'post', 'remove']
        for command in commands:
            if command == potential_command:
                return command

    def dertermine_command_text(self, potential_text):
        command_text = ' '.join(potential_text)
        return command_text

    def write_callback_to_file(self):
        f = open('callback.txt', 'w')
        callback_json = json.dumps(self.callback)
        for line in callback_json:
            f.write(line)
        f.close()


class Group(object):
    def __init__(self, group_id, name):
        self.id = group_id
        self.url = BASE_URL + '/groups/' + self.id

        if self.id == SAMSON_GROUP_ID:
            self.bot = self.Bot(SAMSON_BOT_ID, name)
            self.allowed_access = False
        elif self.id == LEADERSHIP_GROUP_ID:
            self.bot = self.Bot(LEADERSHIP_BOT_ID, name)
            self.allowed_access = True
        elif self.id == TEST_GROUP_ID:
            self.bot = self.Bot(TEST_BOT_ID, name)
            self.allowed_access = True

    def add_member(self, name, phone_number=None, email=None):
        if phone_number:
            phone_number = '+1' + phone_number

        url = self.url + '/members/add'
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

    def list_members(self):
        payload = {"token": ACCESS_TOKEN}

        r = requests.get(self.url, params = payload)

        data = json.loads(r.content)
        node = data['response']['members']

        members = {}
        for member in node:
            members[member['id']] = member['nickname']

        members_string = ''
        for key, value in members.iteritems():
            members_string += '(%s, %s) :: ' %(value, key)
        members_string = members_string[:-4]

        return members_string

    def remove_member(self, member_id):
        url = self.url + '/members/' + member_id + '/remove'
        payload = {"token": ACCESS_TOKEN}

        r = requests.post(url, params = payload)


    class Bot(object):
        def __init__(self, bot_id, name):
            self.id = bot_id
            self.name = name
            self.url = BASE_URL + '/bots'

        def obey(self, requesting_group, parsed_callback):
            group = parsed_callback['group']
            command = parsed_callback['command']
            message = parsed_callback['message']

            if command == 'post':
                group.bot.post(message)
            elif command == 'list':
                members = group.list_members()
                requesting_group.bot.post(members)
            else:
                requesting_group.bot.post('Que?')

        def post(self, message=None, attachment=None):
            url = self.url + '/post'
            payload = {
                    'bot_id': self.id,
                    'text': message,
                    'attachments': attachment
            }

            r = requests.post(url, params = payload)


def create_groups():
    leaderGroup = Group(LEADERSHIP_GROUP_ID, '#helper')
    samsonGroup = Group(SAMSON_GROUP_ID, '#system')
    testGroup = Group(TEST_GROUP_ID, '#test')

    groups = [leaderGroup, samsonGroup, testGroup]
    return groups


def get_requesting_group(callback, groups):
    for group in groups:
        if callback['group_id'] == group.id:
            return group


def activate(callback): # rename get_callback in views.py to this
    groupme = Callback(callback)
    groups = create_groups()

    group = get_requesting_group(groupme.callback, groups)
    if group.allowed_access:
        parsed_callback = groupme.parse_callback(groups)
        if parsed_callback:
            parsed_callback['group'].bot.obey(group, parsed_callback)
