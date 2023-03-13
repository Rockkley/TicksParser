"""GUI using tkinter"""
import tkinter as tk
import calendar
from tkinter import ttk, messagebox
from datetime import datetime
from accounts import Accounts
from ticksgetter import logger, Formats, TicksGetter

LABELS_FONT = '0 10 bold'
TITLE_FONT = '0 12 italic'
WIDGET_ARGS = {'padx': 10, 'pady': 10, 'sticky': 'w'}
WIDGET_BACKGROUND_COLOR = 'white smoke'


class ExportFrame(tk.Frame):
    """Frame containing export combobox and label"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg=parent['bg'])
        self.format_label = ttk.Label(
            self,
            text="Export format",
            font=LABELS_FONT,
            background=self['bg'])
        self.format_combobox = self.create_format_combobox()
        self.format_label.grid(row=3, column=0, **WIDGET_ARGS)
        self.format_combobox.grid(row=3, column=1, **WIDGET_ARGS)

    def create_format_combobox(self) -> ttk.Combobox:
        """Creates combobox of saving formats.

        :rtype: ttk.Combobox
        """
        format_combobox = ttk.Combobox(self, values=[i.value for i in Formats],
                                       width=13, state='readonly')
        format_combobox.set('Select format...')
        return format_combobox

    def get_chosen_format(self) -> Formats:
        try:
            selection = self.format_combobox.get()
            return Formats[selection.upper()]
        except KeyError:
            logger.warning('Select saving format')


class LoginFrame(tk.Frame):
    """Frame containing login form (spinbox, label and connection indicator)"""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.config(bg=parent['bg'])
        self.login_label = ttk.Label(self, text="Broker", font=LABELS_FONT)
        self.login_btn_var = tk.StringVar()
        self.parent = parent
        # Creating widgets
        self.btn_login = self.create_login_button()
        self.login_combobox = self.create_login_combobox()
        self.connection_indicator = self.create_connection_indicator()
        self.login_btn_var.trace_add('write', self.trace_login_combobox)
        self.login_btn_var.trace_add('write', self.trace_connection)
        # Grid
        self.login_label.grid(row=0, column=0, **WIDGET_ARGS)
        self.login_combobox.grid(row=0, column=1, **WIDGET_ARGS)
        self.btn_login.grid(row=0, column=2, **WIDGET_ARGS)
        self.connection_indicator.grid(row=0, column=3, **WIDGET_ARGS)

    def create_login_button(self) -> ttk.Button:
        """Creates 'Login' button"""
        return ttk.Button(
            self,
            text="Login",
            command=self.login_from_btn,
            state=tk.DISABLED,
        )

    def create_login_combobox(self) -> ttk.Combobox:
        """Creates combobox of accounts to log in"""
        values = [i.upper() for i in Accounts.__dict__ if "__" not in i]
        login_combobox = ttk.Combobox(
            self,
            values=values,
            state='readonly', width=15, textvariable=self.login_btn_var)
        login_combobox.set('Select account...')
        # login_combobox.current(0)
        return login_combobox

    def create_connection_indicator(self) -> tk.Label:
        """Creates connection indicator"""
        return tk.Label(self, text='\u2B24')

    def login_from_btn(self):
        """Calls 'login' function"""
        self.parent.ticks_getter.login(self.login_combobox.get())
        self.parent.symbols_treeviews.clear_trees()

    def trace_login_combobox(self, var=None, index=None, mode=None):
        """Function to enable/disable login button
        if login combobox changed."""
        values = self.login_combobox['values']
        if self.login_combobox.get() in values:
            self.btn_login.config(state=tk.NORMAL)
        else:
            self.btn_login.config(state=tk.DISABLED)

    def trace_connection(self, var, index, mode):
        """Function to colorize connection indicator"""
        self.connection_indicator.config(
            fg='green' if self.parent.ticks_getter.authorized else 'red')


class DatesFrame(tk.LabelFrame):
    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(text="Dates (YYYY.M.D)", bg=parent['bg'], font=LABELS_FONT)
        self.date_from_label = tk.Label(self, text="Date from", font=LABELS_FONT)
        self.date_from_label.grid(row=0, column=0, sticky="W", padx=10)
        # Date to label
        self.date_to_label = tk.Label(self, text="Date to", font=LABELS_FONT)
        self.date_to_label.grid(row=1, column=0, sticky="W", padx=10)

        # Date from Spinboxes
        self.day_from_spinbox = tk.Spinbox(
            self,
            from_=1,
            to=31,
            width=2,
            state='readonly')

        self.month_from_spinbox = tk.Spinbox(
            self, values=list(range(1, 13)),
            width=2,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='from',
                month=int(self.month_from_spinbox.get()),
                year=int(self.year_from_spinbox.get())
            )
        )

        self.year_from_spinbox = tk.Spinbox(
            self,
            from_=2000,
            to=datetime.now().year,
            width=4,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='from',
                month=int(self.month_from_spinbox.get()),
                year=int(self.year_from_spinbox.get()),
            ),
        )

        # Date to Spinboxes
        self.day_to_spinbox = tk.Spinbox(
            self,
            from_=1,
            to=31,
            width=2,
            state='readonly')

        self.month_to_spinbox = tk.Spinbox(
            self,
            values=list(range(1, 13)), width=2,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='to',
                month=int(self.month_to_spinbox.get()),
                year=int(self.spinbox_year_last.get()))
        )

        self.spinbox_year_last = tk.Spinbox(
            self,
            from_=2000,
            to=datetime.now().year,
            width=4,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='to',
                month=int(self.month_to_spinbox.get()),
                year=int(self.spinbox_year_last.get()),
            ),
        )

        self.day_from_spinbox.grid(column=3, row=0)
        self.month_from_spinbox.grid(column=2, row=0)
        self.year_from_spinbox.grid(column=1, row=0)
        self.day_to_spinbox.grid(column=3, row=1)
        self.month_to_spinbox.grid(column=2, row=1)
        self.spinbox_year_last.grid(column=1, row=1)

    def get_dates_from_spinboxes(self) -> dict[str, datetime]:
        """Parsing dates from GUI spinboxes into timestamps for the TicksGetter parameters.
        :return: Dictionary with keys 'from_date' and 'to_date'.
        """
        from_date = datetime(
            *map(
                int,
                [
                    self.year_from_spinbox.get(),
                    self.month_from_spinbox.get(),
                    self.day_from_spinbox.get(),
                ],
            )
        )
        to_date = datetime(
            *map(
                int,
                [
                    self.spinbox_year_last.get(),
                    self.month_to_spinbox.get(),
                    self.day_to_spinbox.get(),
                ],
            )
        )

        if from_date < to_date:
            return {'from_date': from_date, 'to_date': to_date}
        logger.warning('"Date to" must be greater than "Date from"')
        return {}

    def update_date_in_spinbox(self, source: str, month: int, year: int):
        """Updates dates in date spinboxes"""
        if source == 'from':
            self.spinbox_year_last.config(from_=year)
            self.day_from_spinbox.config(to=calendar.monthrange(year, month)[1])
        elif source == 'to':
            self.day_to_spinbox.config(to=calendar.monthrange(year, month)[1])

        # *** DoItYourself ***:
        # days_in_month = {1: 31, 3: 31, 5: 31, 7: 31, 8: 31, 10: 31, 12: 31,
        #                  4: 30, 6: 30, 9: 30, 11: 30,
        #                  2: (29 if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else 28)}
        # if source == 'from':
        #     self.spinbox_year_last.config(from_=year)
        #     self.day_from_spinbox.config(to=days_in_month[month])
        # elif source == 'to':
        #     self.day_to_spinbox.config(to=days_in_month[month])

    def set_dates_to_tickparser(self, dates: dict[str, datetime]):

        self.parent.ticks_getter.utc_from = dates['from_date']
        self.parent.ticks_getter.utc_to = dates['to_date']


class SymbolsTreeviewsFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(bg=parent['bg'])
        self.label = ttk.Label(self, text="Symbols", font=LABELS_FONT)
        self.chosen_symbols_tree = self.create_chosen_symbols_tree()
        self.server_symbols_tree = self.create_server_symbols_tree()
        self.label.grid(row=2, column=0, **WIDGET_ARGS)
        self.chosen_symbols_tree.grid(row=2, column=1)
        self.server_symbols_tree.grid(row=2, column=0)

    def create_server_symbols_tree(self) -> ttk.Treeview:
        """Creates treeview of symbols found on the server"""
        scrollbar_layout = tk.Canvas(self)
        scrollbar_layout.grid(column=1, row=2, sticky='W')
        scrollbar = tk.Scrollbar(
            scrollbar_layout,
            orient='vertical')
        server_symbols_tree = ttk.Treeview(
            scrollbar_layout,
            yscrollcommand=scrollbar.set)
        server_symbols_tree.heading('#0', text='On server', anchor=tk.W)
        scrollbar.configure(command=server_symbols_tree.yview)
        server_symbols_tree.bind(
            '<Double-1>', lambda _: self.move_symbols(source='on_server')
        )
        scrollbar.grid(row=2, column=2, columnspan=5, sticky="ns")
        return server_symbols_tree

    def create_chosen_symbols_tree(self) -> ttk.Treeview:
        """Creates treeview of chosen symbols"""
        scrollbar_to_get_layout = tk.Canvas(self)
        scrollbar_to_get_layout.grid(column=2, row=2)
        chosen_symbols_tree = ttk.Treeview(scrollbar_to_get_layout)
        chosen_symbols_tree.heading('#0', text='To get', anchor=tk.W)
        chosen_symbols_tree.grid(row=2, column=2, sticky="W")
        # To get scrollbar
        to_get_scrollbar = tk.Scrollbar(
            self,
            orient='vertical',
            command=chosen_symbols_tree.yview)
        chosen_symbols_tree.configure(yscrollcommand=to_get_scrollbar.set)
        to_get_scrollbar.grid(row=2, column=3, columnspan=3, sticky="ns")
        chosen_symbols_tree.bind(
            '<Double-1>', lambda _: self.move_symbols(source='on_parselist')
        )
        return chosen_symbols_tree

    def move_symbols(self, source: str, event=None):
        """Moves a symbol between server symbols treeview and a list of chosen symbols."""
        if source == 'on_parselist':
            parselist_selection = self.chosen_symbols_tree.focus()
            self.chosen_symbols_tree.delete(parselist_selection)
        elif source == 'on_server':
            tree_selection = self.server_symbols_tree.focus()
            is_parent = self.server_symbols_tree.get_children(tree_selection)
            if not is_parent:
                symbol_only = tree_selection.split('/')[-1]
                if symbol_only not in self.get_all_chosen_symbols():
                    self.chosen_symbols_tree.insert("", tk.END, text=symbol_only)
        to_get_list = self.chosen_symbols_tree.get_children()
        self.parent.parent.btn_get_ticks['state'] = 'normal' if to_get_list else 'disabled'

    def populate_onserver_symbols_tree(self):
        """Populate treeview of symbols on server"""
        symbols_paths = self.parent.ticks_getter.symbols_from_server
        item_list = [path.split('\\')[0] for path in symbols_paths]
        for path in set(item_list):
            self.server_symbols_tree.insert('', 'end', path, text=path)

        rest = [i.split('\\') for i in self.parent.ticks_getter.symbols_from_server]

        # Insert children nodes into the tree
        for path in symbols_paths:
            item_list = path.split('\\')
            parent_node = item_list[0]
            path_list = [parent_node]
            for i in range(1, len(item_list)):
                path_list.append(f'{path_list[i - 1]}/{item_list[i]}')
                self.server_symbols_tree.insert(parent_node, 'end', path_list[i], text=item_list[i])
                parent_node = path_list[i]

    def get_all_chosen_symbols(self) -> tuple:
        """Returns a list of symbols names from a list of chosen symbols."""
        if symbols_in_tree := tuple(
                self.chosen_symbols_tree.item(symbol)['text']
                for symbol in self.chosen_symbols_tree.get_children()
        ):
            return symbols_in_tree
        logger.warning('No selected symbols')
        return tuple()

    def clear_trees(self):
        print(self.parent)

        self.chosen_symbols_tree.delete(*self.chosen_symbols_tree.get_children())
        self.server_symbols_tree.delete(*self.server_symbols_tree.get_children())
        self.populate_onserver_symbols_tree()


class SettingsFrame(tk.LabelFrame):
    """Settings frame containing login widgets, treeviews and export widgets."""

    def __init__(self, parent, *args, **kwargs):
        tk.LabelFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.config(bg=WIDGET_BACKGROUND_COLOR)
        self.ticks_getter = self.parent.ticks_getter
        self.config(text='Settings', font=LABELS_FONT)

        self.dates_frame = DatesFrame(self)
        self.symbols_treeviews = SymbolsTreeviewsFrame(self)
        self.export_frame = ExportFrame(self)

        self.symbols_treeviews.grid(row=2, column=0, columnspan=5)
        self.export_frame.grid(row=3, column=1, columnspan=5, sticky='w')
        self.dates_frame.grid(row=3, column=0, padx=10, pady=10, sticky='w')

    def get_ticks_from_btn(self):
        """Calls 'get_ticks' function from button"""
        chosen_symbols = self.symbols_treeviews.get_all_chosen_symbols()
        format_ = self.export_frame.get_chosen_format()
        if chosen_symbols and format_:
            if dates := self.dates_frame.get_dates_from_spinboxes():
                self.dates_frame.set_dates_to_tickparser(dates)
                self.ticks_getter.get_ticks(chosen_symbols)
                self.ticks_getter.save_ticks_to_file(format_=format_)


class LoggerFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        logger_label_frame = tk.LabelFrame(self, text="Log", font=LABELS_FONT)
        logger_label_frame.grid(row=0, column=0)
        logger_field = tk.Text(logger_label_frame, height=20, width=52, state='disabled')
        logger_field.grid(row=0, column=0, padx=10, pady=10)


class MainApplication(tk.Tk):
    """Main container of GUI frames with widgets."""

    def __init__(self, parent, *args, **kwargs):
        tk.Tk.__init__(self, parent, *args, **kwargs)
        self.title("Ticks Getter")
        self.ticks_getter = TicksGetter()
        self.config(bg='snow2')
        # Frames

        self.settings_frame = SettingsFrame(self)
        self.login_frame = LoginFrame(parent=self.settings_frame)
        self.logger_frame = LoggerFrame(self)
        self.get_ticks_btn_var = tk.StringVar()
        self.get_ticks_btn_var.trace_add('write', self.trace_get_ticks_btn)
        self.btn_get_ticks = self.create_get_ticks_button()
        # Main title
        # self.main_title = tk.Label(self, text='Settings', font=TITLE_FONT, pady=15, padx=10)
        # self.main_title.grid(row=0, column=0, sticky='nw')
        self.btn_info = tk.Button(self, text="?", borderwidth=1, command=self.show_info)

        self.login_frame.grid(row=0, column=0, sticky='nw')
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nw')
        self.logger_frame.grid(row=0, column=1, padx=10, pady=10)
        self.btn_info.grid(row=3, column=1, pady=10, padx=10, sticky='e')

    def trace_get_ticks_btn(self, var=None, index=None, mode=None):
        to_get_list = self.settings_frame.symbols_treeviews.chosen_symbols_tree.get_children()
        print(to_get_list)
        self.btn_get_ticks['state'] = 'normal' if to_get_list else 'disabled'

    def create_get_ticks_button(self) -> ttk.Button:
        """Creates 'Get ticks' button"""
        btn_get_ticks = ttk.Button(
            self,
            text="Get Ticks",
            command=self.settings_frame.get_ticks_from_btn,
            state='disabled',
        )
        btn_get_ticks.grid(row=3, column=0, padx=10, pady=10)
        return btn_get_ticks

        # symbols_paths = self.ticks_getter.symbols_from_server
        # for path in symbols_paths:
        #     split_path = path.split('\\')
        #     subnodes = split_path[:-1]
        #     symbol = split_path[-1]
        #     for subnode in subnodes:
        #         if self.server_symbols_tree.exists(subnode):
        #             self.server_symbols_tree.insert(parent, 'end', parent, text=parents)
        #         else:
        #             self.server_symbols_tree.insert('', 'end', parent, text= parents)

    def show_info(self):
        """Shows info about the program"""
        messagebox.showinfo('About',
                            '''
        Created by Evgeniy Samarin aka Rockkley
        
        https://github.com/Rockkley/
        2023
        ''')


def run():
    """Runs tkinter GUI"""
    app = MainApplication(parent=None)
    app.mainloop()
