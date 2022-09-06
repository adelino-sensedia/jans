from prompt_toolkit.layout.containers import (
    HSplit,
    Window,
    FloatContainer,
    Dimension
)
from prompt_toolkit.formatted_text import merge_formatted_text
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.key_binding import KeyBindings


class JansSideNavBar():
    """This is a Vertical Navigation bar Widget with one value used in clients/scopes dialogs
    """
    def __init__(self, myparent, entries, selection_changed, select=0, entries_color='#00ff44'):
        """init for JansSideNavBar

        Args:
            parent (widget): This is the parent widget for the dialog, to caluclate the size
            entries (list): List of all navigation headers names
            selection_changed (method): Method to be invoked when selection is changed
            select (int, optional): The first value to be selected. Defaults to 0.
            entries_color (str, optional): Color for entries. Defaults to '#00ff44'.

        Examples:
            self.side_nav_bar = JansSideNavBar(myparent=self.myparent,
                        entries=list(self.tabs.keys()),
                        selection_changed=(self.client_dialog_nav_selection_changed) ,
                        select=0,
                        entries_color='#2600ff')
        """
        self.myparent = myparent  # ListBox parent class
        self.navbar_entries = entries  # ListBox entries
        self.cur_navbar_selection = select  # ListBox initial selection
        self.entries_color = entries_color
        self.cur_tab = entries[self.cur_navbar_selection][0]
        self.selection_changed = selection_changed
        self.create_window()

    def create_window(self):
        """This method creat the dialog it self
        Todo:
            * Change `width` to be dynamic      
        """
        self.side_nav = FloatContainer(
            content=HSplit([
                Window(
                    content=FormattedTextControl(
                        text=self.get_navbar_entries,
                        focusable=True,
                        key_bindings=self.get_nav_bar_key_bindings(),
                        style=self.entries_color,

                    ),
                    style='class:select-box',
                    height=Dimension(preferred=len(
                        self.navbar_entries)*2, max=len(self.navbar_entries)*2+1),
                    cursorline=True,
                    width= 10 #self.get_data_width()
                ),
            ]
            ), floats=[]
        )

    def get_data_width(self):
        """get the largest title lenght

        Returns:
            int: the max title lenght
        """
        return len(max(self.navbar_entries, key=len))

    def get_navbar_entries(self):
        """Get all selective entries

        Returns:
            merge_formatted_text: Merge (Concatenate) several pieces of formatted text together. 
        """

        result = []
        for i, entry in enumerate(self.navbar_entries):
            if i == self.cur_navbar_selection:
                result.append([('[SetCursorPosition]', '')])
            result.append(entry)
            result.append('\n')
            result.append('\n')
        return merge_formatted_text(result)

    def update_selection(self):
        """Update the selected tab and pass the current tab name to the selection_changed handler
        """
        self.cur_tab = self.navbar_entries[self.cur_navbar_selection]
        self.selection_changed(self.cur_tab)

    def go_up(self):
        self.cur_navbar_selection = (
            self.cur_navbar_selection - 1) % len(self.navbar_entries)
        self.update_selection()

    def go_down(self):
        self.cur_navbar_selection = (
            self.cur_navbar_selection + 1) % len(self.navbar_entries)
        self.update_selection()

    def get_nav_bar_key_bindings(self):
        """All key binding for the Dialog with Navigation bar

        Returns:
            KeyBindings: The method according to the binding key
        """
        kb = KeyBindings()

        @kb.add('up')
        def _go_up(event) -> None:
            self.cur_navbar_selection = (
                self.cur_navbar_selection - 1) % len(self.navbar_entries)
            self.update_selection()

        @kb.add('down')
        def _go_down(event) -> None:
            self.cur_navbar_selection = (
                self.cur_navbar_selection + 1) % len(self.navbar_entries)
            self.update_selection()

        # @kb.add("enter")
        # def _(event):
        #     pass

        return kb

    def __pt_container__(self):
        return self.side_nav
