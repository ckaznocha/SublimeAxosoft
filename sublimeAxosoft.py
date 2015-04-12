"""
SublimeAxosoft.

A Sublime Text 3 plug-in for managing issues in Axosoft.
"""
# pylint: disable=F0401,E0611,R0903,W0611,R0201
import sublime
import sublime_plugin
import json
import re
import datetime
import webbrowser
from .AxosoftConfig import CONFIG
from .axosoft_api import Axosoft


def plugin_loaded():
    """ Some Setup. """
    CONFIG['settings'] = sublime.load_settings(CONFIG["file"])
    CONFIG["client"] = Axosoft(
        CONFIG["clientId"],
        CONFIG["clientSecret"],
        CONFIG["settings"].get('axosoft_domain'),
        CONFIG["settings"].get('accessToken', None)
    )


def test_auth(func):
    """ Confirm that we are authenticated. """
    def wrapper(*args, **kwargs):
        """ wrapper function. """
        if CONFIG['client'].is_authenticated():
            return func(*args, **kwargs)
        else:
            sublime.message_dialog(
                'You must authenticate with your Axosoft API first.'
            )
            return args[0].window.run_command('axosoft_auth')
    return wrapper


class AxosoftAuthCommand(sublime_plugin.WindowCommand):

    """ Authenticate with the Axosoft API."""

    def __init__(self, window):
        """ Init. """
        self.window = window

    def finish_auth(self, text):
        """ Convert the code to a token and complete authentication. """
        token = CONFIG['client'].complete_authentication_by_code(
            text,
            CONFIG['redirectUri']
        )
        if CONFIG['client'].is_authenticated():
            CONFIG['settings'].set('accessToken', token)
            sublime.save_settings(CONFIG['file'])
            sublime.message_dialog('Successfully Logged In')
            self.window.run_command('axosoft_me')
        else:
            sublime.error_message('Authentication failed')

    def run(self):
        """ Start the code based authentication process. """
        plugin_loaded()
        url = CONFIG['client'].begin_authentication_by_code(
            CONFIG['redirectUri']
        )
        webbrowser.open(url)
        self.window.show_input_panel('code', '', self.finish_auth, None, None)


class AxosoftTerminateAuthCommand(sublime_plugin.WindowCommand):

    """ Terminate the authentication token."""

    def __init__(self, window):
        """ Init. """
        self.window = window

    def run(self):
        """ Erase the token and get confirmation. """
        CONFIG['settings'].erase('accessToken')
        sublime.save_settings(CONFIG['file'])
        CONFIG['client'].log_out()
        if CONFIG['client'].is_authenticated():
            sublime.error_message('Something went wrong!')
        else:
            sublime.message_dialog('Successfully Logged Out')


class AxosoftMeCommand(sublime_plugin.WindowCommand):

    """ Get info about the current users."""

    def __init__(self, window):
        """ Init. """
        self.window = window
        self.__me = None
        self.__item_types = {
            'Custom Items': 'tasks',
            'Defects': 'defects',
            'Incidents': 'incidents',
            'User Stories': 'features'
        }

    def __on_select(self, idx):
        """ When the user is selected. """
        if idx != -1:
            sublime.set_timeout(
                lambda: self.window.show_quick_panel(
                    sorted(self.__item_types),
                    self.__on_select2
                ),
                20
            )
        else:
            pass

    def __on_select2(self, idx):
        """ When the user selects an item type. """
        if idx != -1:
            item_type = self.__item_types[
                sorted(self.__item_types)[idx]
            ]
            self.window.run_command(
                'axosoft_items',
                {'item_type': item_type, 'user': self.__me['id']}
            )
        else:
            pass

    @test_auth
    def run(self):
        """ Show the current users. """
        self.__me = CONFIG['client'].get('me')['data']
        items = [
            '{0} {1}'.format(
                self.__me['first_name'],
                self.__me['last_name']
            )
        ]
        self.window.show_quick_panel(
            items,
            self.__on_select
        )


class AxosoftItemsCommand(sublime_plugin.WindowCommand):

    """ Items Options."""

    def __init__(self, window):
        """ Init. """
        self.window = window
        self.__items = []
        self.__items_array = []
        self.__selected = int
        self.__actions = {
            'View/Edit': self.__show_item,
            'Log Time': self.__start_log_time,
            'Delete': self.__delete_item,
            'Open in Browser': self.__open_in_browser
        }
        self.__time = {}
        self.__comment = {}
        self.__item_type = None

    def __on_select_item(self, idx):
        """ What to do when a item was selected. """
        if idx != -1:
            self.__selected = idx
            sublime.set_timeout(
                lambda: self.window.show_quick_panel(
                    sorted(self.__actions),
                    self.__on_select_action
                ),
                20
            )
        else:
            pass

    def __on_select_action(self, idx):
        """ What to do when an action was selected. """
        if idx != -1:
            self.__actions[
                sorted(self.__actions)[idx]
            ](self.__selected)
        else:
            pass

    def __open_in_browser(self, selected):
        """ Open the selected item in a browser. """
        url = 'https://{0}/viewitem.aspx?id={1}&type={2}'.format(
            CONFIG["settings"].get('axosoft_domain'),
            self.__items_array[selected]['id'],
            self.__items_array[selected]['item_type']
        )
        webbrowser.open(url)

    def __delete_item(self, selected):
        """ Delete the selected item. """
        confirmation = sublime.ok_cancel_dialog(
            'You are about to delete Item #{0}\n Are you sure?'
            .format(self.__items_array[selected]['id']),
            'Yes'
        )
        if confirmation:
            CONFIG['client'].delete(
                self.__items_array[selected]['item_type'],
                self.__items_array[selected]['id']
            )
        else:
            pass

    # def __start_comment(self, selected):
    #     """ Start comment. """
    #     self.__comment['id'] = self.__items_array[selected]['id']
    #     self.window.show_input_panel(
    #         'Comment',
    #         '',
    #         self.__finish_comment,
    #         None,
    #         None
    #     )

    # def __finish_comment(self, comment):
    #     """ Finish comment. """
    #     payload = {
    #         'detail_type': 'comments',
    #         'content': comment
    #     }

    #     CONFIG['client'].create(
    #         'features',
    #         id=self.__comment['id'],
    #         element = 'comments',
    #         payload = payload
    #     )

    def __start_log_time(self, selected):
        """ Start to Log time to selected item. """
        self.__time['id'] = self.__items_array[selected]['id']
        self.__time['item_type'] = self.__items_array[selected]['item_type']

        self.window.show_input_panel(
            'Time (hours)',
            '',
            self.__setp2_log_time,
            None,
            None
        )

    def __setp2_log_time(self, text):
        """ Step 2 to Log time to selected item. """
        self.__time['duration'] = text

        self.window.show_input_panel(
            'description',
            '',
            self.__finish_log_time,
            None,
            None
        )

    def __finish_log_time(self, text):
        """ Finish Log time to selected item. """
        self.__time['description'] = text
        self.__time['date_time'] = datetime.datetime.now().isoformat()
        self.__time['user_id'] = CONFIG['client'].get('me')['data']['id']

        payload = {
            'user': {'id': self.__time['user_id']},
            'work_done': {
                'duration': self.__time['duration'],
                'time_unit': {'id': 2}
            },
            'item': {
                'id': self.__time['id'],
                'item_type': self.__time['item_type']
            },
            'description': self.__time['description'],
            'date_time': self.__time['date_time']
        }

        try:
            CONFIG['client'].create(
                'work_logs',
                payload
            )
        except ValueError:
            sublime.message_dialog(
                "Unable to log time.\nWhen entering time enter only a number."
            )

    def __show_item(self, selected):
        """ List items. """
        new_view = self.window.new_file()
        new_view.set_scratch(True)
        new_view.set_name(self.__items[selected])
        new_view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
        new_view.run_command(
            'axosoft_show_item',
            {
                'text': json.dumps(
                    self.__items_array[selected],
                    sort_keys=True,
                    indent=4,
                    separators=(',', ': ')
                )
            }
        )

    @test_auth
    def run(self, item_type, user=0, search=None):
        """ Run. """
        # Clear self.__itmes if anything was left in it
        if self.__items:
            self.__items = []

        # Create our payload
        payload = {'assigned_to_id': user}

        # Are we searching for anything in particular?
        if search is not None:
            payload['search_string'] = search

        # Get the items from the API
        items_data = CONFIG['client'].get(
            item_type,
            None,
            payload
        )['data']

        # Did we get anything back?
        if items_data:
            self.__items_array = []
            for item in items_data:
                self.__items.append(
                    'axo{0}: #{1} - {2}'.format(
                        item_type[:1],
                        item['id'],
                        item['name']
                    )
                )
                self.__items_array.append(item)

            sublime.set_timeout(
                lambda: self.window.show_quick_panel(
                    self.__items,
                    self.__on_select_item
                ),
                20
            )
        else:
            sublime.message_dialog("No Items Found")


class AxosoftSearchItemsCommand(sublime_plugin.WindowCommand):

    """ Search for a Item."""

    def __init__(self, window):
        """ Init. """
        self.__item_type = None
        self.window = window

    @test_auth
    def run(self, item_type):
        """ Run. """
        self.__item_type = item_type
        self.window.show_input_panel('Search', '', self.__search, None, None)

    def __search(self, text):
        """ Search. """
        self.window.run_command(
            'axosoft_items',
            {'item_type': self.__item_type, 'user': None, 'search': text}
        )


class AxosoftCreateItemsCommand(sublime_plugin.WindowCommand):

    """ Create a new Items."""

    def __init__(self, window):
        """ Init. """
        self.window = window
        self.payload = {}
        self.__item_type = None

    def __create(self, text):
        """ Start creating a new item. """
        # get the project from the settings
        self.payload['item']['project'] = {
            'id': CONFIG['settings'].get(
                'axosoft_project'
            )
        }
        self.payload['item']['estimated_duration'] = {
            'duration': text,
            'time_unit': {'id': 2}
        }

        try:
            data = CONFIG['client'].create(
                self.__item_type,
                payload=self.payload
            )['data']
        except ValueError as response:
            # Ugly hack because axosoft doesn't return the correct HTTP
            # response code
            data = response.args[0]['data']

        self.window.run_command(
            'axosoft_items',
            {'item_type': self.__item_type, 'user': None, 'search': data['id']}
        )

    def __description(self, text):
        """ Prompt for description. """
        self.payload['item']['name'] = text
        self.window.show_input_panel(
            'Description',
            '',
            self.__estimate,
            None,
            None
        )

    def __estimate(self, text):
        """ Prompt for an estimate. """
        self.payload['item']['Description'] = text
        self.window.show_input_panel(
            'Time Estimate(hours)',
            '',
            self.__create,
            None,
            None
        )

    @test_auth
    def run(self, item_type):
        """ Run. """
        # check if project has been set
        if CONFIG['settings'].has('axosoft_project'):
            self.__item_type = item_type
            self.payload['item'] = {}
            self.window.show_input_panel(
                'Title',
                '',
                self.__description,
                None,
                None
            )
        else:
            sublime.message_dialog(
                'You must first set the current project'
            )
            self.window.run_command('axosoft_projects')


class AxosoftProjectsCommand(sublime_plugin.WindowCommand):

    """ Project options."""

    def __init__(self, window):
        """ Init. """
        self.window = window
        self.__projects = {}

    def __on_select(self, idx):
        """ When the user is selected. """
        if idx != -1:
            # Set project in config
            CONFIG['settings'].set(
                'axosoft_project',
                self.__projects[idx]['id']
            )
            sublime.message_dialog(
                'You have set {0} as the current project'
                .format(self.__projects[idx]['name'])
            )
        else:
            pass

    @test_auth
    def run(self):
        """ Run. """
        self.__projects = CONFIG['client'].get('projects')['data']
        print(self.__projects)

        items = [x['name']for x in self.__projects]
        self.window.show_quick_panel(
            items,
            self.__on_select
        )


class AxosoftShowItemCommand(sublime_plugin.TextCommand):

    """ Open a item for editing."""

    def __init__(self, view):
        """ Init. """
        self.view = view

    @test_auth
    def run(self, edit, text):
        """ Run. """
        self.view.insert(edit, self.view.size(), text)


class EventListeners(sublime_plugin.EventListener):

    """ Event Listeners."""

    def __init__(self):
        """ Init. """
        self.modified_views = {}

    def on_modified(self, view):
        """ On Modified. """
        if view.name().startswith("axo"):
            if view.name() not in self.modified_views:
                self.modified_views[view.name()] = 1
            else:
                self.modified_views[view.name()] += 1

    def on_pre_close(self, view):
        """ Save the item on close. """
        if (re.match(r'^axo[dfit]:\s#\d+', view.name())
                and view.name() in self.modified_views
                and self.modified_views[view.name()] > 2):
            confirmation = sublime.ok_cancel_dialog(
                "Save the changes to {0}?".format(view.name()),
                "Save"
            )
            if confirmation:
                content_region = sublime.Region(0, view.size())
                content_string = view.substr(content_region)
                content_json = json.loads(content_string)
                item_id = content_json['id']
                item_type = content_json['item_type']

                CONFIG['client'].update(
                    item_type,
                    item_id,
                    payload={'item': content_json}
                )

            self.modified_views[view.name()] = 0
        else:
            pass
