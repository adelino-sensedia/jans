from typing import OrderedDict
from asyncio import ensure_future

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
)
from prompt_toolkit.application.current import get_app
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    VerticalLine,
    HorizontalLine
)
from cli import config_cli
from static import DialogResult
from wui_components.jans_dialog_with_nav import JansDialogWithNav
from wui_components.jans_side_nav_bar import JansSideNavBar
from wui_components.jans_cli_dialog import JansGDialog
from wui_components.jans_drop_down import DropDownWidget
from wui_components.jans_data_picker import DateSelectWidget
from utils import DialogUtils
from wui_components.jans_vetrical_nav import JansVerticalNav
from view_uma_dialog import ViewUMADialog
import threading

from multi_lang import _
import re

class EditScopeDialog(JansGDialog, DialogUtils):
    """The Main Scope Dialog that contain every thing related to The Scope
    """
    def __init__(self, parent, title, data, buttons=[], save_handler=None):
        """init for `EditScopeDialog`, inherits from two diffrent classes `JansGDialog` and `DialogUtils`
            
        DialogUtils (methods): Responsable for all `make data from dialog` and `check required fields` in the form for any Edit or Add New
        
        Args:
            parent (widget): This is the parent widget for the dialog, to access `Pageup` and `Pagedown`
            title (str): The Main dialog title
            data (list): selected line data 
            button_functions (list, optional): Dialog main buttons with their handlers. Defaults to [].
            save_handler (method, optional): handler invoked when closing the dialog. Defaults to None.
        """
        super().__init__(parent, title, buttons)
        self.save_handler = save_handler
        self.data = data
        self.title=title
        self.showInConfigurationEndpoint = self.data.get('attributes',{}).get('showInConfigurationEndpoint','')
        self.defaultScope = self.data.get('defaultScope','')
        self.tbuffer = None
        self.prepare_tabs()
        self.create_window()
        self.sope_type = self.data.get('scopeType') or 'oauth'
        


    def save(self):
        self.myparent.logger.debug('SAVE SCOPE')

        data = {}

        for item in self.dialog.content.children + self.alt_tabs[self.sope_type].children:
            item_data = self.get_item_data(item)
            if item_data:
                data[item_data['key']] = item_data['value']

        self.myparent.logger.debug('DATA: ' + str(data))
        self.data = data    
        if 'attributes' in self.data.keys():    
            self.data['attributes'] = {'showInConfigurationEndpoint':self.data['attributes']}


        self.myparent.logger.debug('handler: '+str(self.save_handler))
        close_me = True
        if self.save_handler:
            close_me = self.save_handler(self)
        if close_me:
            self.future.set_result(DialogResult.ACCEPT)
    
    def cancel(self):
        self.future.set_result(DialogResult.CANCEL)


    def create_window(self):

        scope_types = [('oauth', 'OAuth'), ('openid', 'OpenID'), ('dynamic', 'Dynamic'), ('uma', 'UMA')]
        buttons = [(self.save, _("Save")), (self.cancel, _("Cancel"))]
        if self.data:
            if self.data.get('scopeType') == 'spontaneous':
                scope_types.insert(3, ('spontaneous', 'Spontaneous'))
                buttons.pop(0)

            if self.data.get('scopeType') == 'uma':
                buttons.pop(0)
            else:
                for stype in scope_types[:]:
                    if stype[0] == 'uma':
                        scope_types.remove(stype)

        self.dialog = JansDialogWithNav(
            title=self.title,
            content= HSplit([
                self.myparent.getTitledRadioButton(
                                _("Scope Type"),
                                name='scopeType',
                                current_value=self.data.get('scopeType'),
                                values=scope_types,
                                on_selection_changed=self.scope_selection_changed,
                                style='class:outh-scope-radiobutton'),

                self.myparent.getTitledText(_("id"), name='id', value=self.data.get('id',''), style='class:outh-scope-text'),
                self.myparent.getTitledText(_("inum"), name='inum', value=self.data.get('inum',''), style='class:outh-scope-text',read_only=True,),
                self.myparent.getTitledText(_("Display Name"), name='displayName', value=self.data.get('displayName',''), style='class:outh-scope-text'),
                self.myparent.getTitledText(_("Description"), name='description', value=self.data.get('description',''), style='class:outh-scope-text'),
                DynamicContainer(lambda: self.alt_tabs[self.sope_type]),
            ], style='class:outh-scope-tabs'), 
             button_functions=buttons,
            height=self.myparent.dialog_height,
            width=self.myparent.dialog_width,
                   )

    def scope_selection_changed(self, cb):
        self.sope_type = cb.current_value

    def set_scope_type(self, scope_type):
        self.sope_type = scope_type

    def nothing(self):
        pass

    def get_scopes(self):

        data = [[claim] for claim in self.data.get('claims', [])]
        self.myparent.logger.debug('datadata: ' + str(data))
        
        self.claims_container = JansVerticalNav(
                myparent=self.myparent,
                headers=['claims'],
                preferred_size= [0],
                data=data,
                on_display=self.myparent.data_display_dialog,
                on_delete=self.delete_claim,
                selectes=0,
                headerColor='class:outh-client-navbar-headcolor',
                entriesColor='class:outh-client-navbar-entriescolor',
                all_data=data
                )
                
        return self.claims_container

    def delete_claim(self, selected, event):
        """This method for the deletion of claim

        Args:
            selected (_type_): The selected claim
            event (_type_): _description_

        """

        dialog = self.myparent.get_confirm_dialog(_("Are you sure want to delete claim dn:")+"\n {} ?".format(selected[0]))
        async def coroutine():
            focused_before = self.myparent.layout.current_window
            result = await self.myparent.show_dialog_as_float(dialog)
            try:
                self.myparent.layout.focus(focused_before)
            except:
                self.myparent.layout.focus(self.app.center_frame)

            if result.lower() == 'yes':
                self.data['claims'].remove(selected[0])
                self.claims_container.data.remove(selected)


        ensure_future(coroutine())


    def prepare_tabs(self):
        """Prepare the tabs for Edil Scope Dialogs
        """
        schema = self.myparent.cli_object.get_schema_from_reference('#/components/schemas/Scope')

        self.alt_tabs = {}


        self.alt_tabs['oauth'] = HSplit([
                            self.myparent.getTitledCheckBox(
                                    _("Default Scope"),
                                    name='defaultScope',
                                    checked=self.data.get('defaultScope'),
                                    style='class:outh-scope-checkbox',
                            ),

                            self.myparent.getTitledCheckBox(
                                    _("Show in configuration endpoint"),
                                    name='showInConfigurationEndpoint',
                                    checked=self.data.get('attributes',{}).get('showInConfigurationEndpoint','') ,
                                    style='class:outh-scope-checkbox',
                            ),

                        ],width=D(),)

        self.alt_tabs['openid'] = HSplit([

                            self.myparent.getTitledCheckBox(
                                    _("Default Scope"),
                                    name='defaultScope',
                                    checked=self.data.get('defaultScope'),
                                    style='class:outh-scope-checkbox',
                            ),

                            self.myparent.getTitledCheckBox(
                                    _("Show in configuration endpoint"),
                                    name='showInConfigurationEndpoint',
                                    checked=self.data.get('attributes',{}).get('showInConfigurationEndpoint','') ,
                                    style='class:outh-scope-checkbox',
                            ),

                            # Window(char='-', height=1),

                            # HorizontalLine(),
                            self.myparent.getTitledText(
                                    _("Search"), 
                                    name='oauth:scopes:openID:claims:search',
                                    style='class:outh-scope-textsearch',width=10,
                                    jans_help=_("Press enter to perform search"),
                                    #accept_handler=self.search_openID_claims
                                    ),


                            ####################################################
                            self.get_scopes(),
                            ###################################################

                            ],width=D(),)

        self.alt_tabs['dynamic'] = HSplit([
                        
                        self.myparent.getTitledText(_("Dynamic Scope Script"),
                            name='dynamicScopeScripts',
                            value='\n'.join(self.data.get('dynamicScopeScripts', [])),
                            height=3, 
                            style='class:outh-scope-text'),
                        
                        # Window(char='-', height=1),
                        self.myparent.getTitledText(
                                _("Search"), 
                                name='oauth:scopes:openID:claims:search',
                                style='class:outh-scope-textsearch',width=10,
                                jans_help=_("Press enter to perform search"), ),#accept_handler=self.search_scopes

                        self.myparent.getTitledText(
                                _("Claims"),
                                name='claims',
                                value='\n'.join(self.data.get('claims', [])),
                                height=3, 
                                style='class:outh-scope-text'),

                        # Label(text=_("Claims"),style='red'),  ## name = claims TODO 

                        ],width=D(),
                    )

        self.alt_tabs['spontaneous'] = HSplit([
                    self.myparent.getTitledText(_("Associated Client"), name='none', value=self.data.get('none',''), style='class:outh-scope-text',read_only=True,height=3,),## Not fount
                    self.myparent.getTitledText(_("Creationg time"), name='creationDate', value=self.data.get('creationDate',''), style='class:outh-scope-text',read_only=True,),

                                                ],width=D(),
                    )

        uma_creator = self.data.get('creatorId','') or self.myparent.cli_object.get_user_info().get('inum','')


        self.alt_tabs['uma'] = HSplit([
                    self.myparent.getTitledText(_("IconURL"), name='iconUrl', value=self.data.get('iconUrl',''), style='class:outh-scope-text'),
                    

                    self.myparent.getTitledText(_("Authorization Policies"),
                            name='umaAuthorizationPolicies',
                            value='\n'.join(self.data.get('umaAuthorizationPolicies', [])),
                            height=3, 
                            style='class:outh-scope-text'),

                    self.myparent.getTitledText(_("Associated Client"), name='none', value=self.data.get('none',''), style='class:outh-scope-text',read_only=True,height=3,), ## Not fount
                    self.myparent.getTitledText(_("Creationg time"), name='description', value=self.data.get('description',''), style='class:outh-scope-text',read_only=True,),
                    self.myparent.getTitledText(
                                    _("Creator"), 
                                    name='Creator',
                                    style='class:outh-scope-text',
                                    read_only=True,
                                    value=uma_creator
                                    ),
                    ],
                    width=D(),
                    )
 

    def __pt_container__(self):
        return self.dialog

