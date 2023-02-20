"""GUI using tkinter"""
import tkinter as tk
import calendar
from tkinter import ttk, messagebox
from datetime import datetime
from accounts import Accounts
from ticksgetter import logger, Formats, TicksGetter


class GUI(tk.Tk):
    """GUI using tkinter"""
    def __init__(self):
        super().__init__()
        self.title("Ticks Getter")
        self.labels_font = '0 10 bold'
        self.ticks_getter = TicksGetter()
        # Settings side
        self.settings_side = tk.Frame(self)
        self.settings_side.grid(row=0, column=0, padx=10, pady=10, sticky="N")
        # Settings frame
        self.settings_frame = tk.LabelFrame(self.settings_side)
        self.settings_frame.grid(row=0, column=0, padx=10, pady=10)
        # Create GUI elements
        self.logger_frame = self.create_logger_frame()
        self.login_combobox = self.create_login_combobox()
        self.format_combobox = self.create_format_combobox()
        self.btn_login = self.create_login_button()
        self.btn_get_ticks = self.create_get_ticks_button()
        self.server_symbols_tree = self.create_server_symbols_tree()
        self.connection_indicator = self.create_connection_indicator()
        # Main title
        self.main_title = tk.Label(self, text='Settings', font='0 12 italic', pady=15, padx=10)
        self.main_title.grid(row=0, column=0, sticky='nw')
        # Login label
        self.login_label = ttk.Label(self.settings_frame, text="Broker", font=self.labels_font)
        self.login_label.grid(row=0, column=0, sticky="W", padx=10)
        # Symbols Label
        self.symbols_label = ttk.Label(self.settings_frame, text="Symbols", font=self.labels_font)
        self.symbols_label.grid(row=2, column=0, sticky="W", padx=10)
        # Format Label
        self.format_label = ttk.Label(
            self.settings_frame,
            text="Export format",
            font=self.labels_font)
        self.format_label.grid(row=3, column=0, sticky="W", padx=10)
        # Dates Frame
        self.dates_frame = tk.LabelFrame(
            self.settings_side,
            text="Dates (YYYY.M.D)",
            font=self.labels_font)
        self.dates_frame.grid(row=2, sticky="W", padx=10)
        # Date from Label
        self.date_from_label = tk.Label(self.dates_frame, text="Date from", font=self.labels_font)
        self.date_from_label.grid(row=0, column=0, sticky="W", padx=10)
        # Date from Spinboxes
        self.day_from_spinbox = tk.Spinbox(
            self.dates_frame,
            from_=1,
            to=31,
            width=2,
            state='readonly')
        self.day_from_spinbox.grid(column=3, row=0)
        # Spinbox for month from
        self.month_from_spinbox = tk.Spinbox(
            self.dates_frame, values=list(range(1, 13)),
            width=2,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='from',
                month=int(self.month_from_spinbox.get()),
                year=int(self.year_from_spinbox.get())
            )
        )
        self.month_from_spinbox.grid(column=2, row=0)
        # Spinbox for year from
        self.year_from_spinbox = tk.Spinbox(
            self.dates_frame,
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
        self.year_from_spinbox.grid(column=1, row=0)
        # Date to label
        self.date_to_label = tk.Label(self.dates_frame, text="Date to", font=self.labels_font)
        self.date_to_label.grid(row=1, column=0, sticky="W", padx=10)
        # Date to spinboxes
        self.day_to_spinbox = tk.Spinbox(
            self.dates_frame,
            from_=1,
            to=31,
            width=2,
            state='readonly')
        self.day_to_spinbox.grid(column=3, row=1)
        # Spinbox for month from
        self.month_to_spinbox = tk.Spinbox(
            self.dates_frame,
            values=list(range(1, 13)), width=2,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='to',
                month=int(self.month_to_spinbox.get()),
                year=int(self.year_to_spinbox.get()))
        )
        self.month_to_spinbox.grid(column=2, row=1)
        # Spinbox for year from
        self.year_to_spinbox = tk.Spinbox(
            self.dates_frame,
            from_=2000,
            to=datetime.now().year,
            width=4,
            state='readonly',
            command=lambda: self.update_date_in_spinbox(
                source='to',
                month=int(self.month_to_spinbox.get()),
                year=int(self.year_to_spinbox.get()),
            ),
        )
        self.year_to_spinbox.grid(column=1, row=1)
        # Scrollbar layouts
        self.scrollbar_to_get_layout = tk.Canvas(self.settings_frame)
        # Symbols To Parse
        self.symbols_to_get_tree = ttk.Treeview(self.scrollbar_to_get_layout)
        self.symbols_to_get_tree.heading('#0', text='To get', anchor=tk.W)
        self.symbols_to_get_tree.grid(row=2, column=2, sticky="W")
        # To get scrollbar
        self.to_get_scrollbar = tk.Scrollbar(
            self.settings_frame,
            orient='vertical',
            command=self.symbols_to_get_tree.yview)
        self.symbols_to_get_tree.configure(yscrollcommand=self.to_get_scrollbar.set)
        self.to_get_scrollbar.grid(row=2, column=3, columnspan=3, sticky="ns")

        self.scrollbar_to_get_layout.grid(column=2, row=2)
        self.symbols_to_get_tree.bind(
            '<Double-1>', lambda _: self.move_symbols(source='on_parselist')
        )
        self.btn_info = tk.Button(self, text="?", borderwidth=1, command=self.show_info)
        self.btn_info.grid(row=0, column=1, sticky="SE", pady=15, padx=15)

    def populate_onserver_symbols_tree(self):
        """Populate treeview of symbols on server"""
        symbols_paths = self.ticks_getter.symbols_from_server
        item_list = [path.split('\\')[0] for path in symbols_paths]
        for path in set(item_list):
            self.server_symbols_tree.insert('', 'end', path, text=path)

        rest = [i.split('\\') for i in self.ticks_getter.symbols_from_server]

        # Insert children nodes into the tree
        for path in symbols_paths:
            item_list = path.split('\\')
            parent_node = item_list[0]
            path_list = [parent_node]
            for i in range(1, len(item_list)):
                path_list.append(f'{path_list[i - 1]}/{item_list[i]}')
                self.server_symbols_tree.insert(parent_node, 'end', path_list[i], text=item_list[i])
                parent_node = path_list[i]

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

    def get_all_tree_items(self) -> list:
        """Returns a list of symbols names from a list of chosen symbols."""
        return [self.symbols_to_get_tree.item(symbol)['text']
                for symbol in self.symbols_to_get_tree.get_children()]

    def move_symbols(self, source: str, event=0):
        """Moves a symbol between server symbols treeview and a list of chosen symbols."""
        if source == 'on_parselist':
            parselist_selection = self.symbols_to_get_tree.focus()
            self.symbols_to_get_tree.delete(parselist_selection)
        elif source == 'on_server':
            tree_selection = self.server_symbols_tree.focus()
            is_parent = self.server_symbols_tree.get_children(tree_selection)
            if not is_parent:
                symbol_only = tree_selection.split('/')[-1]
                if symbol_only not in self.get_all_tree_items():
                    self.symbols_to_get_tree.insert("", tk.END, text=symbol_only)
        to_get_list = self.symbols_to_get_tree.get_children()
        self.btn_get_ticks['state'] = 'normal' if to_get_list else 'disabled'
        # self.update_symbols_counters()

    def login_from_btn(self):
        """Calls 'login' function"""
        self.ticks_getter.login(self.login_combobox.get())
        if self.ticks_getter.authorized and self.ticks_getter.symbols_from_server:
            self.connection_indicator.config(fg='green')
            self.symbols_to_get_tree.delete(*self.symbols_to_get_tree.get_children())
            self.server_symbols_tree.delete(*self.server_symbols_tree.get_children())
            self.populate_onserver_symbols_tree()

            # self.update_symbols_counters()

    def set_dates_from_spinboxes(self) -> bool:
        """Parsing dates from GUI spinboxes into timestamps for the TicksGetter parameters."""
        from_date = datetime(*map(int, [self.year_from_spinbox.get(),
                                        self.month_from_spinbox.get(),
                                        self.day_from_spinbox.get()]))
        to_date = datetime(*map(int, [self.year_to_spinbox.get(),
                                      self.month_to_spinbox.get(),
                                      self.day_to_spinbox.get()]))

        if from_date >= to_date:
            logger.warning('"Date to" must be greater than "Date from"')
            return False
        self.ticks_getter.utc_from = from_date
        self.ticks_getter.utc_to = to_date
        return True

    def get_ticks_from_btn(self):
        """Calls 'get_ticks' function from button"""
        chosen_symbols = tuple(self.get_all_tree_items())
        if not chosen_symbols:
            logger.warning('No selected symbols')
            return
        format_ = Formats[self.format_combobox.get().upper()]
        if self.set_dates_from_spinboxes():
            self.ticks_getter.get_ticks(chosen_symbols)
            self.ticks_getter.save_to_file(format_=format_)

    def update_date_in_spinbox(self, source: str, month: int, year: int):
        """Updates dates in date spinboxes"""
        if source == 'from':
            self.year_to_spinbox.config(from_=year)
            self.day_from_spinbox.config(to=calendar.monthrange(year, month)[1])
        elif source == 'to':
            self.day_to_spinbox.config(to=calendar.monthrange(year, month)[1])

        # *** DoItYourself ***:
        # days_in_month = {1: 31, 3: 31, 5: 31, 7: 31, 8: 31, 10: 31, 12: 31,
        #                  4: 30, 6: 30, 9: 30, 11: 30,
        #                  2: (29 if year % 4 == 0 and year % 100 != 0 or year % 400 == 0 else 28)}
        # if source == 'from':
        #     self.year_to_spinbox.config(from_=year)
        #     self.day_from_spinbox.config(to=days_in_month[month])
        # elif source == 'to':
        #     self.day_to_spinbox.config(to=days_in_month[month])

    def create_logger_frame(self) -> tk.LabelFrame:
        """Creates frame for logger"""
        logger_side = tk.Frame(self)
        logger_side.grid(row=0, column=1, padx=10, pady=10, sticky="N")
        logger_frame = tk.LabelFrame(logger_side, text="Log", font=self.labels_font)
        logger_frame.grid(row=1, column=1, padx=10, pady=10)
        logger_field = tk.Text(logger_frame, height=20, width=52, state='disabled')
        logger_field.grid(row=1, column=0, padx=10, pady=10)
        return logger_frame

    def create_login_combobox(self) -> ttk.Combobox:
        """Creates combobox of accounts to log in"""
        values = [i.upper() for i in Accounts.__dict__ if "__" not in i]
        login_combobox = ttk.Combobox(
            self.settings_frame,
            values=values,
            state='readonly', width=15)
        login_combobox.grid(row=0, column=1, sticky="W", pady=10)
        login_combobox.current(0)
        return login_combobox

    def create_format_combobox(self) -> ttk.Combobox:
        """Creates combobox of saving formats"""
        format_combobox = ttk.Combobox(self.settings_frame, values=[i.value for i in Formats],
                                       width=7, state='readonly')
        format_combobox.grid(row=3, column=1, sticky="W", pady=10, padx=10)
        format_combobox.current(0)
        return format_combobox

    def create_login_button(self) -> ttk.Button:
        """Creates 'Login' button"""
        btn_login = ttk.Button(self.settings_frame, text="Login", command=self.login_from_btn)
        btn_login.grid(row=0, column=1, pady=10, sticky='e')
        return btn_login

    def create_server_symbols_tree(self) -> ttk.Treeview:
        """Creates treeview of symbols found on the server"""
        scrollbar_layout = tk.Canvas(self.settings_frame)
        scrollbar_layout.grid(column=1, row=2)
        on_server_scrollbar = tk.Scrollbar(
            scrollbar_layout,
            orient='vertical')
        server_symbols_tree = ttk.Treeview(
            scrollbar_layout,
            yscrollcommand=on_server_scrollbar.set)
        server_symbols_tree.heading('#0', text='On server', anchor=tk.W)
        server_symbols_tree.grid(row=2, column=1, sticky="W")
        server_symbols_tree.configure(yscrollcommand=on_server_scrollbar.set)
        on_server_scrollbar.grid(row=2, column=2, columnspan=5, sticky="ns")
        on_server_scrollbar.configure(command=server_symbols_tree.yview)
        server_symbols_tree.bind(
            '<Double-1>', lambda _: self.move_symbols(source='on_server')
        )
        return server_symbols_tree

    def create_get_ticks_button(self) -> ttk.Button:
        """Creates 'Get ticks' button"""
        btn_get_ticks = ttk.Button(
            self.settings_side,
            text="Get Ticks",
            command=self.get_ticks_from_btn,
            state='disabled')
        btn_get_ticks.grid(row=3, column=0, padx=10, pady=10)
        return btn_get_ticks

    def create_connection_indicator(self) -> tk.Label:
        """Creates connection indicator"""
        connection_indicator = tk.Label(self.settings_frame, text='\u2B24', fg='red')
        connection_indicator.grid(column=1, columnspan=4, row=0, sticky='e')
        return connection_indicator
