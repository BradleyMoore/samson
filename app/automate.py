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
        callback (json): Json object that contains at a minimum
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
        """Parse callback for bot, command, and message.

        Takes the instance callback and breaks it apart to find
        information on the called bot, the command, and the message
        sent, if included.

        Args:
            groups (list): Contains each available group object.

        Returns:
            A dict containing the bot, command, message, attachments,
            or False for each absent value.
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
        # Determine which group is being called by comparing bot names.
        for group in groups:
            if potential_bot == group.bot.name:
                return group

    def determine_called_command(self, potential_command):
        # Determines which command is called, if any.
        commands = ['add', 'list', 'post', 'remove']
        for command in commands:
            if command == potential_command:
                return command

    def dertermine_command_text(self, potential_text):
        # Determines the message sent, if any.
        command_text = ' '.join(potential_text)
        return command_text

    def write_callback_to_file(self):
        # For debugging only; writes the callback to callback.txt.
        f = open('callback.txt', 'w')
        callback_json = json.dumps(self.callback)
        for line in callback_json:
            f.write(line)
        f.close()


class Group(object):
    """A groupme group used to manage user requests.

    This class is used to manage the various groupme groups so the app
    knows which group to communicate with. The bot is nested because it
    is directily associated with this group in groupmes listings.

    Attributes:
        id (str): A string of numbers id-ing this group to groupme.
        url (str): The url used for calls to this groupme group.
        bot (Bot): The class of the associated groupme bot.
        allowed_access (boolean): Whether or not the group is allowed
                                  to make calls to this API.
    """

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
        """Add a new member to the groupme group.

        Args:
            name (str): The name to be used in the groupme group.
            phone_number (str): The new member's phone number.
            email (str): The new member's email address.

        Returns:
            Nothing is returned.
        """

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
        """List all members from the called group in calling group.

        Gets all members from the called group, parses them into a
        string ready to post back in the calling group's chat thread.

        Args:
            No arguments are used.

        Returns:
            A string formatted to post in the groupme chat thread.
        """

        payload = {"token": MOORE_ACCESS_TOKEN}

        r = requests.get(self.url, params = payload)

        data = r.json()
        node = data['response']['members']

        members = {}
        for member in node:
            members[member['id']] = member['nickname']

        members_string = ''
        for key, value in members.items():
            members_string += '(%s, %s)\n' %(value, key)
        members_string = members_string

        return members_string

    def remove_member(self, member_id):
        """Remove a member from the groupme group.

        Args:
            member_id (str): A string of numbers representing the
                             member to the group.

        Returns:
            Nothing is returned.
        """

        url = self.url + '/members/' + member_id + '/remove'
        payload = {"token": EJECTOMATIC_ACCESS_TOKEN}

        r = requests.post(url, params = payload)

    class Bot(object):
        """A bot associated with a specific groupme group.

        This class is directly related to the Group it is nested in.
        It is associated on groupme's servers. The bot's main purpost
        is to post on a user's behalf so the rest of the users don't
        know exactly who is sending the message. It's main usage is for
        system messages relating to the entire group.

        Attributes:
            id (str): A string of numbers id-ing this bot to groupme.
            name (str): The bot's name used to check if it is called.
            url (str): The url used for calls to this groupme bot.
        """

        def __init__(self, bot_id, name):
            self.id = bot_id
            self.name = name
            self.url = BASE_URL + '/bots'

        def obey(self, requesting_group, parsed_callback):
            """Calls correct action based on the user's directive.

            Acts upon the command called by calling the appropriate
            method.

            Args:
                requesting_group (str): Calling group used to send
                                        messages back to the user if
                                        necessary.
                parsed_callback (dict): The important parts of the
                                        callback ready for use.

            Returns:
                Nothing is returned.
            """

            attachments = parsed_callback['attachments']
            command = parsed_callback['command']
            group = parsed_callback['group']
            message = parsed_callback['message']

            if command == 'post':
                group.bot.post(message, attachments)
            elif command == 'list':
                members = group.list_members()
                requesting_group.bot.post(members)
            elif command == 'remove':
                members = group.list_members()
                if message:
                    if message in members:
                        group.remove_member(message)
                    else:
                        requesting_group.bot.post(members + '"' + message +
                            '" is not a valid member ID.\n\n')
                else:
                    requesting_group.bot.post(members +
                        '\n\nYou must include the member ID.')
            else:
                requesting_group.bot.post('Que?')

        def post(self, message, attachments=None):
            """Post a message to the appropriate groupme group.

            Takes a message and any attachments and posts them to the
            correct group based on the bot called in the callback.

            Args:
                message (str): The command modifies. Usually the
                               message to be posted to the groupme
                               group.
                attachments (list of dicts): Attachments to be posted
                                             to the correct groupme
                                             group.

            Returns:
                Nothing is returned.
            """

            url = self.url + '/post'
            payload = {
                    'bot_id': self.id,
                    'text': message,
                    'attachments': attachments
            }

            r = requests.post(url, params = payload)


def create_groups():
    """Creates all of my groupme groups as Groups() in a list.

    Args:
        No arguments are used.

    Returns:
        A list of all created groups.
    """

    groups = [Group(LEADERSHIP_GROUP_ID, '#helper'),
              Group(SAMSON_GROUP_ID, '#system'),
              Group(TEST_GROUP_ID, '#test')]

    return groups


def get_requesting_group(callback_group, groups):
    """Determine which group the callback came from.

    Compares the callback group_id to the different groups ids to
    determine which group called the script.

    Args:
        callback_group (str): String of numbers representing the
                              group to groupme.
        groups (list): All of my groupme groups.

    Returns:
        The calling group or False if it doesn't exist.
    """

    for group in groups:
        if callback_group == group.id:
            return group


def activate(callback):
    """Activates everything needed for the bot callback system to work.

    Args:
        callback (json): The groupme callback sent everytime a message
                         is posted in one of my groups.

    Returns:
        Nothing is returned.
    """

    groupme = Callback(callback)
    groups = create_groups()

    group = get_requesting_group(groupme.callback_group, groups)
    if group.allowed_access:
        parsed_callback = groupme.parse_callback(groups)
        if parsed_callback:
            parsed_callback['group'].bot.obey(group, parsed_callback)
