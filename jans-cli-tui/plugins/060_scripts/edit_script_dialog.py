from typing import OrderedDict
from asyncio import ensure_future
from functools import partial

from prompt_toolkit.layout.dimension import D
from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    DynamicContainer,
    Window
)
from prompt_toolkit.widgets import (
    Box,
    Button,
    Label,
    TextArea,
)
from prompt_toolkit.application.current import get_app
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    VerticalLine,
    HorizontalLine,
    CheckboxList,
)

from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.jvm import JavaLexer

from cli import config_cli
from static import DialogResult
from wui_components.jans_dialog_with_nav import JansDialogWithNav
from wui_components.jans_side_nav_bar import JansSideNavBar
from wui_components.jans_cli_dialog import JansGDialog
from wui_components.jans_drop_down import DropDownWidget
from wui_components.jans_data_picker import DateSelectWidget
from utils import DialogUtils
from wui_components.jans_vetrical_nav import JansVerticalNav
from wui_components.jans_spinner import Spinner
from prompt_toolkit.layout.containers import (
    AnyContainer,
)
from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout.dimension import AnyDimension
from typing import Optional, Sequence, Union
from typing import TypeVar, Callable

from view_uma_dialog import ViewUMADialog
import threading

from multi_lang import _
import re

class EditScriptDialog(JansGDialog, DialogUtils):
    """This Script editing dialog
    """
    def __init__(
        self,
        parent,
        data:list,
        title: AnyFormattedText= "",
        buttons: Optional[Sequence[Button]]= [],
        save_handler: Callable= None,
        )-> Dialog:
        """init for `EditScriptDialog`, inherits from two diffrent classes `JansGDialog` and `DialogUtils`
            
        DialogUtils (methods): Responsable for all `make data from dialog` and `check required fields` in the form for any Edit or Add New
        
        Args:
            parent (widget): This is the parent widget for the dialog, to access `Pageup` and `Pagedown`
            title (str): The Main dialog title
            data (list): selected line data 
            button_functions (list, optional): Dialog main buttons with their handlers. Defaults to [].
            save_handler (method, optional): handler invoked when closing the dialog. Defaults to None.
        """
        super().__init__(parent, title, buttons)
        self.myparent = parent
        self.save_handler = save_handler
        self.data = data
        self.title=title
        self.cur_lang = self.data.get('programmingLanguage', 'PYTHON')
        self.create_window()
        self.script = self.data.get('script','')

    def save(self):

        data = {}

        for item in self.edit_dialog_content:
            item_data = self.get_item_data(item)
            if item_data:
                data[item_data['key']] = item_data['value']

        for prop_container in (self.config_properties_container, self.module_properties_container):

            if prop_container.data:
                data[prop_container.jans_name] = []
                for prop_ in prop_container.data:
                    key_ = prop_[0]
                    val_ = prop_[1]

                    if key_:
                        prop = {'value1': key_}
                        if val_:
                            prop['value2'] = val_
                        if len(prop_) > 2:
                            prop['hide'] = prop_[2]
                        data[prop_container.jans_name].append(prop)

        
        data['locationType'] = 'LDAP' if data['location'] == 'db' else 'FILE'
        data['internal'] = self.data.get('internal', False)
        data['modified'] = self.data.get('modified', False)
        data['revision'] = self.data.get('revision', 0) + 1
        data['script'] = self.script

        del data['location']

        if not data['inum']:
            del data['inum']

        if self.data.get('baseDn'):
            data['baseDn'] = self.data['baseDn']

        self.new_data = data

        close_me = True
        if self.save_handler:
            close_me = self.save_handler(self)
        if close_me:
            self.future.set_result(DialogResult.ACCEPT)

    def cancel(self):
        self.future.set_result(DialogResult.CANCEL)

    def create_window(self):

        schema = self.myparent.cli_object.get_schema_from_reference('#/components/schemas/CustomScript')

        script_types = [
                        ['PERSON_AUTHENTICATION', 'Person Authentication'],
                        ['CONSENT_GATHERING', 'Consent Gathering'],
                        ['POST_AUTHN', 'Post Authentication'],
                        ['ID_TOKEN', 'id_token'],
                        ['PASSWORD_GRANT', 'Password Grant'],
                        ['CIBA_END_USER_NOTIFICATION', 'CIBA End User Notification'],
                        ['OpenID Configuration', 'OpenID Configuration'],
                        ['DYNAMIC_SCOPE', 'Dynamic Scope', ],
                        ['SPONTANEOUS_SCOPE', 'Spontaneous Scope',],
                        ['APPLICATION_SESSION', 'Application Session'],
                        ['END_SESSION', 'End Session'],
                        ['CLIENT_REGISTRATION', 'Client Registration'],
                        ['INTROSPECTION', 'Introspection'],
                        ['UPDATE_TOKEN', 'Update Token'],
                        ['CONFIG_API', 'Config API'],
                        ['IDP', 'IDP'],
                        ['RESOURCE_OWNER_PASSWORD_CREDENTIALS', 'Resource Owner Password Credentials'],
                        ['CACHE_REFRESH', 'Cache Refresh'],
                        ['ID_GENERATOR', 'Id Generator'],
                        ['UMA_RPT_POLICY', 'Uma Rpt Policy'],
                        ['UMA_RPT_CLAIMS', 'Uma Rpt Claims'],
                        ['UMA_CLAIMS_GATHERING', 'Uma Claims Gathering'],
                        ['SCIM', 'SCIM'],
                        ['REVOKE_TOKEN', 'Revoke Token'],
                        ['PERSISTENCE_EXTENSION', 'Persistence Extension'],
                        ['DISCOVERY', 'Discovery'],
                        ]

        self.location_widget = self.myparent.getTitledText(_("          Path"), name='locationPath', value=self.data.get('locationPath',''), style='class:script-titledtext', jans_help=self.myparent.get_help_from_schema(schema, 'locationPath'))
        self.set_location_widget_state(self.data.get('locationPath') == 'file')

        config_properties_title = _("Conf. Properties: ")
        add_property_title = _("Add Property")
        module_properties_title = _("Module Properties: ")

        config_properties_data = []
        for prop in self.data.get('configurationProperties', []):
            config_properties_data.append([prop['value1'], prop.get('value2', ''), prop.get('hide', False)])

        self.config_properties_container = JansVerticalNav(
                myparent=self.myparent,
                headers=['Key', 'Value', 'Hide'],
                preferred_size=[15, 15, 5],
                data=config_properties_data,
                on_enter=self.edit_property,
                on_delete=self.delete_config_property,
                on_display=self.myparent.data_display_dialog,
                selectes=0,
                headerColor='class:outh-client-navbar-headcolor',
                entriesColor='class:outh-client-navbar-entriescolor',
                all_data=config_properties_data,
                underline_headings=False,
                max_width=52,
                jans_name='configurationProperties',
                max_height=False
                )

        module_properties_data = []
        for prop in self.data.get('moduleProperties', []):
            module_properties_data.append([prop['value1'], prop.get('value2', '')])

        self.module_properties_container = JansVerticalNav(
                myparent=self.myparent,
                headers=['Key', 'Value'],
                preferred_size=[20, 20],
                data=module_properties_data,
                on_enter=self.edit_property,
                on_delete=self.delete_config_property,
                on_display=self.myparent.data_display_dialog,
                selectes=0,
                headerColor='class:outh-client-navbar-headcolor',
                entriesColor='class:outh-client-navbar-entriescolor',
                all_data=module_properties_data,
                underline_headings=False,
                max_width=44,
                jans_name='moduleProperties',
                max_height=3
                )

        open_editor_button_title = _("Edit Script")
        open_editor_button = Button(text=open_editor_button_title, width=len(open_editor_button_title)+2, handler=self.edit_script_dialog)
        open_editor_button.window.jans_help="Enter to open editing window"

        self.edit_dialog_content = [
                    self.myparent.getTitledText(_("Inum"), name='inum', value=self.data.get('inum',''), style='class:script-titledtext', jans_help=self.myparent.get_help_from_schema(schema, 'inum'), read_only=True),
                    self.myparent.getTitledWidget(
                                _("Script Type"),
                                name='scriptType',
                                widget=DropDownWidget(
                                    values=script_types,
                                    value=self.data.get('scriptType', '')
                                    ),
                                jans_help=self.myparent.get_help_from_schema(schema, 'scriptType'),
                                style='class:outh-client-dropdown'),

                    self.myparent.getTitledCheckBox(_("Enabled"), name='enabled', checked= not self.data.get('enabled'), style='class:script-checkbox', jans_help=self.myparent.get_help_from_schema(schema, 'enabled')),
                    self.myparent.getTitledText(_("Name"), name='name', value=self.data.get('name',''), style='class:script-titledtext', jans_help=self.myparent.get_help_from_schema(schema, 'name')),
                    self.myparent.getTitledText(_("Description"), name='description', value=self.data.get('description',''), style='class:script-titledtext', jans_help=self.myparent.get_help_from_schema(schema, 'description')),

                    self.myparent.getTitledRadioButton(
                            _("Location"),
                            name='location',
                            values=[('db', _("Database")), ('file', _("File System"))],
                            current_value= 'file' if self.data.get('locationPath') else 'db',
                            jans_help=_("Where to save script"),
                            style='class:outh-client-radiobutton',
                            on_selection_changed=self.script_location_changed,
                            ),

                     self.location_widget,

                    self.myparent.getTitledWidget(
                                _("Programming Language"),
                                name='programmingLanguage',
                                widget=DropDownWidget(
                                    values=[['PYTHON', 'Python'], ['JAVA', 'Java']],
                                    value=self.cur_lang,
                                    on_value_changed=self.script_lang_changed,
                                    ),
                                jans_help=self.myparent.get_help_from_schema(schema, 'programmingLanguage'),
                                style='class:outh-client-dropdown'),

                    self.myparent.getTitledWidget(
                                _("Level"),
                                name='level',
                                widget=Spinner(
                                    value=self.data.get('level', 0)
                                    ),
                                jans_help=self.myparent.get_help_from_schema(schema, 'level'),
                                style='class:outh-client-dropdown'),

                    VSplit([
                            Label(text=config_properties_title, style='class:script-label', width=len(config_properties_title)+1), 
                            self.config_properties_container,
                            Window(width=2),
                            HSplit([
                                Window(height=1),
                                Button(text=add_property_title, width=len(add_property_title)+4, handler=partial(self.edit_property, jans_name='configurationProperties')),
                                ]),
                            ],
                            height=5, width=D(),
                            ),

                    VSplit([
                            Label(text=module_properties_title, style='class:script-label', width=len(module_properties_title)+1), 
                            self.module_properties_container,
                            Window(width=2),
                            HSplit([
                                Window(height=1),
                                Button(text=add_property_title, width=len(add_property_title)+4, handler=partial(self.edit_property, jans_name='moduleProperties')),
                                ]),
                            ],
                             height=5
                            ),
                    VSplit([open_editor_button, Window(width=D())]),
                    ]


        self.dialog = JansDialogWithNav(
            title=self.title,
            content= HSplit(
                self.edit_dialog_content,
                width=D(),
                height=D()
                ),
            button_functions=[(self.cancel, _("Cancel")), (self.save, _("Save"))],
            height=self.myparent.dialog_height,
            width=self.myparent.dialog_width,
            )

    def script_lang_changed(self, value):
        self.cur_lang = value

    def set_location_widget_state(self, state):
        self.location_widget.me.read_only = not state
        self.location_widget.me.focusable = state
        if not state:
            self.location_widget.me.text = ''

    def script_location_changed(self, redio_button):
        state = redio_button.current_value == 'file'
        self.set_location_widget_state(state)

    def edit_property(self, **kwargs):

        if kwargs['jans_name'] == 'moduleProperties':
            key, val = kwargs.get('data', ('',''))
            title = _("Enter Module Properties")
        else:
            key, val, hide = kwargs.get('data', ('','', False))
            hide_widget = self.myparent.getTitledCheckBox(_("Hide"), name='property_hide', checked=hide, style='class:script-titledtext', jans_help=_("Hide script property?"))
            title = _("Enter Configuration Properties")

        key_widget = self.myparent.getTitledText(_("Key"), name='property_key', value=key, style='class:script-titledtext', jans_help=_("Script propery Key"))
        val_widget = self.myparent.getTitledText(_("Value"), name='property_val', value=val, style='class:script-titledtext', jans_help=_("Script property Value"))


        def add_property(dialog):
            key_ = key_widget.me.text
            val_ = val_widget.me.text
            cur_data = [key_, val_]

            if kwargs['jans_name'] == 'configurationProperties':
                hide_ = hide_widget.me.checked
                cur_data.append(hide_)
                container = self.config_properties_container
            else:
                container = self.module_properties_container
            if not kwargs.get('data'):
                container.add_item(cur_data)
            else:
                container.replace_item(kwargs['selected'], cur_data)

        body_widgets = [key_widget, val_widget]
        if kwargs['jans_name'] == 'configurationProperties':
            body_widgets.append(hide_widget)

        body = HSplit(body_widgets)
        buttons = [Button(_("Cancel")), Button(_("OK"), handler=add_property)]
        dialog = JansGDialog(self.myparent, title=title, body=body, buttons=buttons, width=self.myparent.dialog_width-20)
        self.myparent.show_jans_dialog(dialog)

    def delete_config_property(self, **kwargs):
        if kwargs['jans_name'] == 'configurationProperties':
            self.config_properties_container.remove_item(kwargs['selected'])
        else:
            self.module_properties_container.remove_item(kwargs['selected'])

    def edit_script_dialog(self):

        text_editor = TextArea(
                text=self.script,
                multiline=True,
                height=self.myparent.dialog_height-10,
                width=D(),
                focusable=True,
                scrollbar=True,
                line_numbers=True,
                lexer=PygmentsLexer(PythonLexer if self.cur_lang == 'PYTHON' else JavaLexer),
            )

        def modify_script(arg):
            self.script = text_editor.text

        buttons = [Button(_("Cancel")), Button(_("OK"), handler=modify_script)]
        dialog = JansGDialog(self.myparent, title=_("Edit Script"), body=HSplit([text_editor]), buttons=buttons, width=self.myparent.dialog_width-10)
        self.myparent.show_jans_dialog(dialog)

    def __pt_container__(self):
        return self.dialog

