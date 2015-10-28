import json, requests

from config import EJECTOMATIC_ACCESS_TOKEN, MOORE_ACCESS_TOKEN, BASE_URL
from config import LEADERSHIP_BOT_ID, LEADERSHIP_GROUP_ID
from config import SAMSON_BOT_ID, SAMSON_GROUP_ID
from config import TEST_BOT_ID, TEST_GROUP_ID


class Callback(object):
    """The response object from each post to any of my groupme groups.

    The callback should be a json object that includes at a minumum a
    group ID #, and a message's text.

    Attributes:
        callback (object): Json object that contains at a minimum
                                a group id and a message's text.
        callback_group (str): A string of numbers gathered from the callback.
        callback_text (str): A message to be parsed.

    """

    def __init__(self, callback):
        self.callback = callback
        self.callback_attachments = self.callback['attachments']
        self.callback_group = self.callback['group_id']
        self.callback_text = self.callback['text']

    def parse_callback(self, groups):
        """Parse callback for bot, command, and message

        Takes the instance callback and breaks it apart to find
        information on the called bot, the command, and the message
        sent, if included.

        Args:
            groups (list): Contains each available group object.

        Returns:
            A dict containing the bot, command, and message, False for
            each absent value.
        """

        words = self.callback_text.split()
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

        parsed_callback['attachments'] = self.callback_attachments

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
        payload = {"token": MOORE_ACCESS_TOKEN}

        r = requests.get(self.url, params = payload)

        data = json.loads(r.content)
        node = data['response']['members']

        members = {}
        for member in node:
            members[member['id']] = member['nickname']

        members_string = ''
        for key, value in members.iteritems():
            members_string += '(%s, %s\n)' %(value, key)
        members_string = members_string

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
            attachments = parsed_callback['attachments']
            command = parsed_callback['command']
            group = parsed_callback['group']
            message = parsed_callback['message']

            if command == 'post':
                group.bot.post(message, attachments)
            elif command == 'list':
                members = group.list_members()
                requesting_group.bot.post(members)
            else:
                requesting_group.bot.post('Que?')

        def post(self, message, attachments=None):
            url = self.url + '/post'
            payload = {
                    'bot_id': self.id,
                    'text': message,
                    'attachments': attachments
            }

            r = requests.post(url, params = payload)


def create_groups():
    groups = [Group(LEADERSHIP_GROUP_ID, '#helper'),
              Group(SAMSON_GROUP_ID, '#system'),
              Group(TEST_GROUP_ID, '#test')]

    return groups


def get_requesting_group(callback_group, groups):
    for group in groups:
        if callback_group == group.id:
            return group


def activate(callback): # rename get_callback in views.py to this
    groupme = Callback(callback)
    groups = create_groups()

    group = get_requesting_group(groupme.callback_group, groups)
    if group.allowed_access:
        parsed_callback = groupme.parse_callback(groups)
        if parsed_callback:
            parsed_callback['group'].bot.obey(group, parsed_callback)
