from curses import window
import threading

from collections import OrderedDict
import json
from asyncio import Future, ensure_future

from prompt_toolkit.application.current import get_app
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    HSplit,
    VSplit,
    VerticalAlign,
    DynamicContainer,
    FloatContainer,
    Window
)
from prompt_toolkit.layout.containers import VerticalAlign
from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.lexers import PygmentsLexer ,DynamicLexer
from prompt_toolkit.widgets import (
    Box,
    Button,
    Frame,
    Label,
    RadioList,
    TextArea,
    CheckboxList,
    Shadow,
)
from prompt_toolkit.filters import Condition

from cli import config_cli
from wui_components.jans_nav_bar import JansNavBar
from wui_components.jans_side_nav_bar import JansSideNavBar
from wui_components.jans_vetrical_nav import JansVerticalNav
from wui_components.jans_dialog import JansDialog
from wui_components.jans_dialog_with_nav import JansDialogWithNav


class JansAuthServer:


    def initialize(self):
        self.oauth_containers = {}
        self.oauth_prepare_navbar()
        self.oauth_prepare_containers()
        self.oauth_nav_selection_changed(self.oauth_navbar.navbar_entries[0][0])


    def oauth_prepare_containers(self):

        self.oauth_data_container = {
            'clients' :HSplit([],width=D()),
            'scopes' :HSplit([],width=D()),

        } 
        self.oauth_main_area = HSplit([],width=D())

        self.oauth_containers['scopes'] = HSplit([
                    VSplit([
                        self.getButton(text="Get Scopes", name='oauth:scopes:get', jans_help="Retreive first 10 Scopes", handler=self.oauth_get_scopes),
                        self.getTitledText('Search: ', name='oauth:scopes:search', jans_help='Press enter to perform search'),
                        self.getButton(text="Add Scope", name='oauth:scopes:add', jans_help="To add a new scope press this button")
                        ],
                        padding=3,
                        width=D(),
                    ),
                    DynamicContainer(lambda: self.oauth_data_container['scopes'])
                    ])

        self.oauth_containers['clients'] = HSplit([
                    VSplit([
                        self.getButton(text="Get Clients", name='oauth:clients:get', jans_help="Retreive first 10 OpenID Connect clients", handler=self.oauth_get_clients),
                        self.getTitledText('Search: ', name='oauth:clients:search', jans_help='Press enter to perform search'),
                        self.getButton(text="Add Client", name='oauth:clients:add', jans_help="To add a new client press this button")
                        ],
                        padding=3,
                        width=D(),
                        ),
                        DynamicContainer(lambda: self.oauth_data_container['clients'])
                    ]
                    )

        self.oauth_main_container = HSplit([
                                        Box(self.oauth_navbar.nav_window, style='fg:#f92672 bg:#4D4D4D', height=1),
                                        DynamicContainer(lambda: self.oauth_main_area),
                                        ],
                                    height=D(),
                                    )


    def oauth_prepare_navbar(self):
         self.oauth_navbar = JansNavBar(
                    self,
                    entries=[('clients', 'Clients'), ('scopes', 'Scopes'), ('keys', 'Keys'), ('defaults', 'Defaults'), ('properties', 'Properties'), ('logging', 'Logging')],
                    selection_changed=self.oauth_nav_selection_changed,
                    select=0,
                    bgcolor='#66d9ef'
                    )

    def oauth_nav_selection_changed(self, selection):
        if selection in self.oauth_containers:
            self.oauth_main_area = self.oauth_containers[selection]
        else:
            self.oauth_main_area = self.not_implemented

    def oauth_set_center_frame(self):
        self.center_container = self.oauth_main_container

    def oauth_update_clients(self):
        try :
            result = self.cli_object.process_command_by_id('get-oauth-openid-clients', '', 'limit:10', {})


            data =[]

            for d in result: 
                data.append(
                    [
                    d['inum'],
                    d['clientName']['values'][''],
                    ','.join(d['grantTypes']),
                    d['subjectType'] 
                    ]
                )

            clients = JansVerticalNav(
                myparent=self,
                headers=['Client ID', 'Client Name', 'Grant Types', 'Subject Type'],
                preferred_size= [0,0,30,0],
                data=data,
                on_enter=self.edit_client_dialog,
                on_display=self.data_display_dialog,
                # selection_changed=self.data_selection_changed,
                selectes=0,
                headerColor='green',
                entriesColor='white',
                all_data=result
            )

            self.layout.focus(clients)   # clients.focuse..!? TODO >> DONE
            self.oauth_data_container['clients'] = HSplit([
                clients
            ])

            get_app().invalidate()

        except Exception as e:
            self.oauth_data_container['clients'] = HSplit([Label("Faild to Fitch client Data.. Reason: " + str(e))], width=D())
            get_app().invalidate()

    def oauth_get_clients(self):
        self.oauth_data_container['clients'] = HSplit([Label("Please wait while getting clients")], width=D())
        t = threading.Thread(target=self.oauth_update_clients, daemon=True)
        t.start()

    def update_oauth_scopes(self):
        try :
            result = self.cli_object.process_command_by_id('get-oauth-scopes', '', 'limit:10', {})

            data =[]
            
            for d in result: 
                data.append(
                    [
                    d['id'],
                    d['description'],
                    d['scopeType']
                    ]
                )

            clients = JansVerticalNav(
                myparent=self,
                headers=['id', 'Description', 'Type'],
                preferred_size= [0,0,30,0],
                data=data,
                on_enter=self.edit_scope_dialog,
                on_display=self.data_display_dialog,
                # selection_changed=self.data_selection_changed,
                selectes=0,
                headerColor='green',
                entriesColor='white',
                all_data=result
            )

            self.layout.focus(clients)   # clients.focuse..!? TODO >> DONE
            self.oauth_data_container['scopes'] = HSplit([
                clients
            ])

            get_app().invalidate()

        except Exception as e:
            self.oauth_data_container['scopes'] = HSplit([Label("Faild to Fitch client Data.. Reason: " + str(e))], width=D())
            get_app().invalidate()

    def oauth_get_scopes(self):
        self.oauth_data_container['scopes'] = HSplit([Label("Please wait while getting Scopes")], width=D())
        t = threading.Thread(target=self.update_oauth_scopes, daemon=True)
        t.start()

    def display_scope(self):
        pass
