import json, requests

from config import ACCESS_TOKEN, BASE_URL
from config import LEADERSHIP_BOT_ID, LEADERSHIP_GROUP_ID
from config import SAMSON_BOT_ID, SAMSON_GROUP_ID
from config import TEST_BOT_ID, TEST_GROUP_ID


class Callback(object):
    def __init__(self, callback):
        self.callback = callback


    def parse_callback(self):
        text = self.callback['text']
        words = text.split()
        if len(words) < 2:
            return

        parsed_callback = {}

        potential_bot = words[0].lower()
        parsed_callback['group'] = determine_called_group(potential_bot)

        if called_group:
            potential_command = words[1].lower()
            parsed_callback['command'] = determine_called_command(potential_command)
        else:
            return

        if called_command and len(words) >= 3:
            potential_text = words[2:]
            parsed_callback['message'] = dertermine_command_text(potential_text)
        else:
            parsed_callback['message'] = None

        return parsed_callback


    def determine_called_group(self, potential_bot):
        bots = ['#helper', '#system', '#test']
        called_group = None
        for bot in bots:
            if bot == potential_bot:
                if bot == '#helper':
                    called_group = leaderGroup
                elif bot == '#system':
                    called_group = samsonGroup
                elif bot == '#test':
                    called_group = testGroup
                break

        return called_group


    def determine_called_command(self, potential_command):
        commands = ['add', 'list', 'post', 'remove']
        called_command = None
        for command in commands:
            if command == potential_command:
                called_command = command
                break

        return called_command


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
    def __init__(self, group_id):
        self.id = group_id
        self.url = BASE_URL + '/groups/' + self.id

        if self.id == SAMSON_GROUP_ID:
            self.bot = self.Bot(SAMSON_BOT_ID)
            self.allowed_access = False
        elif self.id == LEADERSHIP_GROUP_ID:
            self.bot = self.Bot(LEADERSHIP_BOT_ID)
            self.allowed_access = True
        elif self.id == TEST_GROUP_ID:
            self.bot = self.Bot(TEST_BOT_ID)
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
        def __init__(self, bot_id):
            self.id = bot_id
            self.url = BASE_URL + '/bots'


        def obey(self, parsed_callback):
            group = parsed_callback['group']
            command = parsed_callback['command']
            message = parsed_callback['message']

            if command == 'post':
                group.bot.post(message)
            elif command == 'list':
                members = group.list_members()
                testGroup.bot.post(members)
                #leaderGroup.bot.post(members)
            else:
                testGroup.bot.post('Que?')
                #leaderGroup.bot.post('Que?')


        def post(self, message=None, attachment=None):
            url = self.url + '/post'
            payload = {
                    'bot_id': self.id,
                    'text': message,
                    'attachments': attachment
            }

            r = requests.post(url, params = payload)


def check_for_allowed_group(group):
    if group.allowed_access:
        return True


def create_groups():
    leaderGroup = Group(LEADERSHIP_GROUP_ID)
    samsonGroup = Group(SAMSON_GROUP_ID)
    testGroup = Group(TEST_GROUP_ID)

    groups = [leaderGroup, samsonGroup, testGroup]
    return groups


def get_requesting_group(groups):
    for group in groups:
        if groupme.callback['group_id'] == group.id:
            return group


def activate(callback): # rename get_callback in views.py to this
    groupme = Callback(callback)
    groups = create_groups()

    group = get_requesting_group(groups)
    allowed = check_for_allowed_group(group)
    if not allowed:
        return

    parsed_callback = groupme.parsed_callback()
    if parsed_callback:
        parsed_callback['group'].bot.obey(parsed_callback)
