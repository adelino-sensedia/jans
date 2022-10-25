import json
from asyncio import Future
from typing import OrderedDict

from prompt_toolkit.widgets import Button, TextArea
from prompt_toolkit.application.current import get_app
from prompt_toolkit.layout.dimension import D
from static import DialogResult
from wui_components.jans_dialog import JansDialog
from prompt_toolkit.layout.containers import (
    VSplit,
    DynamicContainer,
)
from prompt_toolkit.key_binding import KeyBindings

from prompt_toolkit.widgets import (
    Button,
    Label,
    TextArea,

)
from asyncio import ensure_future

from prompt_toolkit.widgets import (
    Button,
    Dialog,
    VerticalLine,
)
from cli import config_cli
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
from prompt_toolkit.widgets import (
    Box,
    Button,
    Frame,
    Label,
    RadioList,
    TextArea,
 )
from wui_components.jans_dialog_with_nav import JansDialogWithNav
from wui_components.jans_nav_bar import JansNavBar
from wui_components.jans_side_nav_bar import JansSideNavBar
from utils import DialogUtils

from wui_components.jans_cli_dialog import JansGDialog

from wui_components.jans_drop_down import DropDownWidget
from prompt_toolkit.layout.containers import (
    AnyContainer,
)
from prompt_toolkit.buffer import Buffer

from prompt_toolkit.formatted_text import AnyFormattedText
from prompt_toolkit.layout.dimension import AnyDimension
from typing import Optional, Sequence, Union
from typing import TypeVar, Callable
from multi_lang import _
import cli_style

class ViewProperty(JansGDialog, DialogUtils):
    """The Main UMA-resources Dialog to view UMA Resource Details
    """
    def __init__(
        self,
        parent,
        data:tuple,
        title: AnyFormattedText= "",
        search_text: AnyFormattedText= "",
        buttons: Optional[Sequence[Button]]= [],
        get_properties: Callable= None,
        search_properties: Callable= None,
        )-> Dialog:

        super().__init__(parent, title, buttons)
        self.property, self.value = data[0],data[1]
        self.myparent= parent
        self.get_properties = get_properties
        self.search_properties= search_properties
        self.search_text=search_text
        self.value_content = HSplit([],width=D())
        self.tabs = {}
        self.selected_tab = 'tab0'
        self.schema = self.myparent.cli_object.get_schema_from_reference('#/components/schemas/AppConfiguration')

        self.prepare_properties()
        self.create_window()
        
    def cancel(self) -> None:
        self.future.set_result(DialogResult.CANCEL)

    def save(self) -> None:
        
        for wid in self.dialog.body.children:
            for item in wid.children:
                if type(self.value) == str or type(self.value) == int :
                    item_data = self.get_item_data(item)
                    if item_data:
                        data = item_data['value']

                elif type(self.value) == bool:
                    item_data = self.get_item_data(item)
                    if item_data:
                        data = item_data['value']

                elif type(self.value) == list:
                    self.myparent.logger.debug("self.value: "+str(self.value))
                    if type(self.value[0]) in [str,int,bool] :
                        
                        item_data = self.get_item_data(item)
                        self.myparent.logger.debug("item_data: "+str(item_data))
                        if item_data:
                            data = item_data['value'].split('\n')
                            self.myparent.logger.debug("data[item_data['key']]: "+str(data))

                    else:
                        ## TODO dict in list
                        # pass
                        tab_num = len(self.value)
                        tabs = []
                        for i in range(tab_num) :
                            tabs.append(('tab{}'.format(i),'tab{}'.format(i)))
                        self.myparent.logger.debug("*******************************************")
                        data = []
                        self.myparent.logger.debug("itemitem: "+str(item))
                        self.myparent.logger.debug("wid: "+str(wid))
                        item_data = self.get_item_data(item)
                        self.myparent.logger.debug("item_data: "+str(item_data))
                        for tab in self.value:  
                            data_tab={}
                            for i,field in enumerate(item.children) :
                                item_data = self.get_item_data(item)
                                self.myparent.logger.debug("item_data: "+str(item_data))
                                
                                if item_data:
                                    data_tab['tab{}'.format(self.value.index(tab))] = item_data['value']
                                    self.myparent.logger.debug("data_tab: "+str(data_tab))
                                    data.append(data_tab)
                        self.myparent.logger.debug("datadata: "+str(data))
                        self.myparent.logger.debug("*******************************************")


                elif type(self.value) == dict:
                    data = {}
                    for i,field in enumerate(item.children) :
                        if type(self.value[list(self.value)[i]])  in [str,int,bool]:
                            item_data = self.get_item_data(field)
                            if item_data:
                                data[item_data['key']] = item_data['value']

                else:
                    item_data = self.get_item_data(item)
                    self.myparent.logger.debug("item_data,Else: "+str(item_data))
        if data :
            response = self.myparent.cli_object.process_command_by_id(
                    operation_id='patch-properties' ,
                    url_suffix='',
                    endpoint_args='',
                    data_fn='',
                    data=[ {'op':'replace', 'path': self.property, 'value': data } ]
                    )
        else:
            return

        if response:

            if self.search_text:
                tbuff = Buffer(name='', )
                tbuff.text=self.search_text
                self.search_properties(tbuff)
            else:
                self.get_properties()
            self.future.set_result(DialogResult.ACCEPT)
            return True

        self.myparent.show_message(_("Error!"), _("An error ocurred while saving property:\n") + str(response.text))

    def get_type(self,prop):
        try :
            if self.schema.get('properties', {})[prop]['type'] in ['string', 'integer']:
                prop_type= 'TitledText'

            elif self.schema.get('properties', {})[prop]['type'] == 'boolean':
                prop_type= 'TitledCheckBox'

            elif self.schema.get('properties', {})[prop]['type'] == 'object':
                prop_type= 'dict'

            elif self.schema.get('properties', {})[prop]['type'] == 'array':
                if 'enum' in self.schema.get('properties', {})[prop]:
                   prop_type= 'checkboxlist' 
                else:
                    if type(self.value[0]) == dict:
                        prop_type= 'list-dict'
                    else:
                        prop_type= 'long-TitledText'
        except:
            prop_type = None

        self.myparent.logger.debug("get_type:" +str(prop_type))
        self.myparent.logger.debug("type:" +str(self.schema.get('properties', {})[prop]['type']))
        return prop_type

    def get_listValues(self,prop):
        try :
            list_values= self.schema.get('properties', {})[prop]['enum']
        except:
            list_values = []

        return list_values

    def prepare_properties(self):

        prop_type = self.get_type(self.property)

        if prop_type == 'TitledText':
                self.value_content= HSplit([self.myparent.getTitledText(
                self.property, 
                name=self.property, 
                value=self.value, 
                style='class:outh-scope-text'
                ),
                ],width=D())

        elif prop_type == 'long-TitledText':
            self.value_content= HSplit([self.myparent.getTitledText(
                                self.property+'\n'*(len(self.value)-1), 
                                name=self.property, 
                                height=3,
                                value='\n'.join(self.value), 
                                style='class:outh-scope-text'
                                ),
                                ],width=D())    

        elif prop_type == 'checkboxlist':
            self.value_content= HSplit([
                        self.myparent.getTitledCheckBoxList(
                                self.property+'\n'*(len(self.get_listValues(self.property))-1), 
                                name=self.property, 
                                values=self.get_listValues(self.property), 
                                style='class:outh-client-checkboxlist'),
                                ],width=D())    


        # elif type(self.value) == list:
        #     if type(self.value[0]) in [str,bool,int]: 
        #         self.value_content= HSplit([self.myparent.getTitledText(
        #             self.property+'\n'*(len(self.value)-1), 
        #             name=self.property, 
        #             height=3,
        #             value='\n'.join(self.value), 
        #             style='class:outh-scope-text'
        #             ),
        #             ],width=D())
        #     elif type(self.value[0]) == dict:
        #         tab_num = len(self.value)
        #         tabs = []
        #         for i in range(tab_num) :
        #             tabs.append(('tab{}'.format(i),'tab{}'.format(i)))
        #         self.myparent.logger.debug("tabs: "+str(tabs))

        #         self.myparent.logger.debug("self.value: "+str(self.value))
        #         for tab in self.value:  
        #             tab_list=[]
        #             self.myparent.logger.debug("tab: "+str(tab))
        #             for item in tab:
        #                 self.myparent.logger.debug("item: "+str(item))
        #                 if type(tab[item]) == str or type(tab[item]) == int :
        #                     tab_list.append(HSplit([self.myparent.getTitledText(
        #                         item ,
        #                         name=item, 
        #                         value=tab[item], 
        #                         style='class:outh-scope-text'
        #                         ),
        #                         ],width=D()))

        #                 elif type(tab[item]) == list:
        #                     tab_list.append(HSplit([self.myparent.getTitledText(
        #                         item, 
        #                         name=item, 
        #                         height=3,
        #                         value='\n'.join(tab[item]), 
        #                         style='class:outh-scope-text'
        #                         ),
        #                         ],width=D()))

        #                 elif type(tab[item]) == bool:
        #                     tab_list.append(HSplit([
        #                         self.myparent.getTitledCheckBox(
        #                             item, 
        #                             name=item, 
        #                             checked= tab[item], 
        #                             style='class:outh-client-checkbox'),
        #                     ],width=D()))

        #                 self.tabs['tab{}'.format(self.value.index(tab))] = HSplit(tab_list,width=D())

        #         self.myparent.logger.debug("self.tabs: "+str(self.tabs))
        #         self.value_content=HSplit([
        #                         self.myparent.getTitledRadioButton(
        #                             _("Tab Num")+'\n'*(len(tabs)-1),
        #                             name='tabNum',
        #                             current_value=self.selected_tab,
        #                             values=tabs,
        #                             on_selection_changed=self.tab_selection_changed,
        #                             style='class:outh-scope-radiobutton'),

        #                         DynamicContainer(lambda: self.tabs[self.selected_tab]),     

        #             ],width=D())
                    
        #     elif type(self.value[0]) == list:
        #         for k in range(len(self.value)):
        #             self.value[k] = (','.join(self.value[k]),','.join(self.value[k]))

        #         self.value_content= HSplit([
        #             self.myparent.getTitledCheckBoxList(
        #                 self.property+'\n'*(len(self.value)-1), 
        #                 name=self.property, 
        #                 values=self.value,
        #                 # current_values=self.data.get('grantTypes', []), 
        #                 style='class:outh-client-checkboxlist'), 
        #             ],width=D())

        elif prop_type == 'list-dict':  
            tab_num = len(self.value)
            tabs = []
            for i in range(tab_num) :
                tabs.append(('tab{}'.format(i),'tab{}'.format(i)))
            self.myparent.logger.debug("tabs: "+str(tabs))

            self.myparent.logger.debug("self.value: "+str(self.value))
            for tab in self.value:  
                tab_list=[]
                self.myparent.logger.debug("tab: "+str(tab))
                for item in tab:
                    self.myparent.logger.debug("item: "+str(item))
                    if type(tab[item]) == str or type(tab[item]) == int :
                        tab_list.append(HSplit([self.myparent.getTitledText(
                            item ,
                            name=item, 
                            value=tab[item], 
                            style='class:outh-scope-text'
                            ),
                            ],width=D()))

                    elif type(tab[item]) == list:
                        tab_list.append(HSplit([self.myparent.getTitledText(
                            item, 
                            name=item, 
                            height=3,
                            value='\n'.join(tab[item]), 
                            style='class:outh-scope-text'
                            ),
                            ],width=D()))

                    elif type(tab[item]) == bool:
                        tab_list.append(HSplit([
                            self.myparent.getTitledCheckBox(
                                item, 
                                name=item, 
                                checked= tab[item], 
                                style='class:outh-client-checkbox'),
                        ],width=D()))  
                                    
                    self.tabs['tab{}'.format(self.value.index(tab))] = HSplit(tab_list,width=D())

            self.myparent.logger.debug("self.tabs: "+str(self.tabs))
            self.value_content=HSplit([
                            self.myparent.getTitledRadioButton(
                                _("Tab Num")+'\n'*(len(tabs)-1),
                                name='tabNum',
                                current_value=self.selected_tab,
                                values=tabs,
                                on_selection_changed=self.tab_selection_changed,
                                style='class:outh-scope-radiobutton'),

                            DynamicContainer(lambda: self.tabs[self.selected_tab]),     

                ],width=D())
                
        elif prop_type == 'TitledCheckBox':
            self.value_content= HSplit([
                self.myparent.getTitledCheckBox(
                    self.property, 
                    name=self.property, 
                    checked= self.value, 
                    style='class:outh-client-checkbox'),
            ],width=D())

        elif prop_type == 'dict':
            dict_list=[]
            for item in self.value:
                if type(self.value[item]) == str or type(self.value[item]) == int :
                        dict_list.append(HSplit([self.myparent.getTitledText(
                        item ,
                        name=item, 
                        value=self.value[item], 
                        style='class:outh-scope-text'
                        ),
                        ],width=D()))

                elif type(self.value[item]) == list:
                    dict_list.append(HSplit([self.myparent.getTitledText(
                        item, 
                        name=item, 
                        height=3,
                        value='\n'.join(self.value[item]), 
                        style='class:outh-scope-text'
                        ),
                        ],width=D()))

                elif type(self.value[item]) == bool:
                    dict_list.append(HSplit([
                        self.myparent.getTitledCheckBox(
                            item, 
                            name=item, 
                            checked= self.value[item], 
                            style='class:outh-client-checkbox'),
                    ],width=D()))

                else :
                    dict_list.append(HSplit([self.myparent.getTitledText(
                                            item, 
                                            name=item, 
                                            value="No Items Here", 
                                            style='class:outh-scope-text',
                                            read_only=True,
                                            ),
                                            ],width=D()))  
            self.value_content= HSplit(dict_list,width=D())

    def create_window(self):

        self.dialog = Dialog(title=self.property,
            body=     
            HSplit([
            self.value_content,
        ], padding=1,width=100,style='class:outh-uma-tabs'
        ),
        buttons=[
                Button(
                    text=_("Cancel"),
                    handler=self.cancel,
                ) ,
                Button(
                    text=_("Save"),
                    handler=self.save,
                ) ,            ],
            with_background=False,
        )

    def tab_selection_changed(
        self, 
        cb: RadioList,
        ) -> None:
        self.selected_tab = cb.current_value

    def __pt_container__(self)-> Dialog:
        return self.dialog

