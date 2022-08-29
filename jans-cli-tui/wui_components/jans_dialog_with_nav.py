from shutil import get_terminal_size


from prompt_toolkit.layout.containers import (
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.widgets import (
    Button,
    Dialog,
    VerticalLine,
)
from prompt_toolkit.key_binding import KeyBindings


from prompt_toolkit.layout import ScrollablePane
from prompt_toolkit.application.current import get_app


class JansDialogWithNav():
    def __init__(self,content, height=None, width=None, title=None, button_functions=[], navbar=None):
        self.navbar = navbar
        self.button_functions = button_functions
        self.title = title
        self.height = height
        self.width =width
        self.content = content
        self.create_window()

    def create_window(self):

        max_data_str = 30 ## TODO TO BE Dynamic
        wwidth, wheight = get_terminal_size()

        height = 19 if wheight <= 30 else wheight - 11

        self.dialog = Dialog(
            title=self.title,
            body=VSplit([
                    HSplit([
                        self.navbar
                        ], width= (max_data_str )),
                    VerticalLine(),
                    ScrollablePane(content=self.content, height=height),
                ], width=120, padding=1,key_bindings=self.get_nav_bar_key_bindings()),

            buttons=[
                Button(
                    text=str(self.button_functions[k][1]),
                    handler=self.button_functions[k][0],
                ) for k in range(len(self.button_functions))
            ],
            with_background=False,

        )
#--------------------------------------------------------------------------------------#

    def get_nav_bar_key_bindings(self):
        kb = KeyBindings()

        @kb.add("pageup")
        def _go_up(event) -> None:
            app = get_app()
            self.navbar.go_up()
            app.layout.focus(self.navbar)

        @kb.add("pagedown")
        def _go_up(event) -> None:
            app = get_app()
            self.navbar.go_down()
            app.layout.focus(self.navbar)
    



        @kb.add("enter")
        def _(event):
            pass

        return kb

    def __pt_container__(self):
        return self.dialog

