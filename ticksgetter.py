from main import logger
from pathlib import Path
import MetaTrader5 as mt5
import pandas as pd
import pytz
from datatypes import Ticks, Formats
from accounts import LoginInfo, Accounts
from functools import singledispatchmethod
from string import Template
from datetime import datetime


class TicksGetter:
    """
    Collects ticks from a server using official MetaTrader5 package.
    """
    def __init__(self):
        """

        """
        self.company_name = None
        self.timezone = pytz.timezone("Etc/UTC")
        self.utc_from = datetime(year=2021, month=1, day=1, tzinfo=self.timezone)
        self.utc_to = datetime(year=2022, month=1, day=1, tzinfo=self.timezone)
        self.not_found_ticks: list[str] = []
        self.authorized = False
        self.symbols_from_server = set()
        self.collected_tickets: list[Ticks] = []

    def get_account_from_string(self, account_name: str) -> LoginInfo | bool:
        """

        :param account_name: name of saved account.
        :return: LoginInfo file that contains data for authorisation.
        """
        try:
            # Getting LoginInfo object by 'settings' argument
            return getattr(Accounts, account_name.lower())
        except AttributeError as attr_error:
            logger.error(attr_error)
            return False

    @singledispatchmethod
    def login(self, bug: None, account_credentials: LoginInfo) -> bool:
        """
        :param bug: https://bugs.python.org/issue41122
        :param account_credentials:
        :return: bool
        """
        if self.authorized:
            self.close_connection()
        if not account_credentials:
            logger.error('Invalid account parameters')
            return False

        logger.info('Launching MetaTrader at %s ...', account_credentials.TERMINAL_PATH)
        try:
            self.authorized = mt5.initialize(
                login=account_credentials.LOGIN,
                password=account_credentials.PASSWORD,
                server=account_credentials.SERVER,
                path=account_credentials.TERMINAL_PATH)
        except Exception as excpt:
            logger.error('Invalid login credentials, %s', excpt)
            return False
        self.set_account_info()
        logger.info('Connected to %s (login: %s)\n', self.company_name, account_credentials.LOGIN)
        return True

    @login.register
    def _(self, account_credentials: str):
        account_credentials = self.get_account_from_string(account_name=account_credentials)
        return self.login(None, account_credentials=account_credentials)

    def set_account_info(self) -> bool:
        """

        :return: True if setting account info was successful, else False
        """
        self.company_name = mt5.account_info().company
        self.symbols_from_server = {symbol.path for symbol in mt5.symbols_get()}
        if not self.symbols_from_server:
            logger.error('Did not received symbols list from the server')
            return False
        logger.info('Got symbols list from the server')
        return True

    def save_to_file(self, format_: Formats) -> bool:
        """

        :param format_:
        :return: True if file saved successfully, else False.
        """
        format_name = format_.value
        for ticks_file in self.collected_tickets:
            Path(f'ticks_{format_name}').mkdir(parents=True, exist_ok=True)
            # example - ticks_xlsx/AUDCAD_FBS_20221202_19012023.xlsx
            template = Template(
                'ticks_${format}/${filename}_${broker}_${date_from}_${date_to}.$format_extension')
            out_filename_template = template.substitute(
                format=format_name,
                filename=ticks_file.TITLE,
                broker=ticks_file.BROKER,
                date_from=f'{ticks_file.DATE_FROM.year}_'
                          f'{ticks_file.DATE_FROM.month}_'
                          f'{ticks_file.DATE_FROM.day}',
                date_to=f'{ticks_file.DATE_TO.year}_'
                        f'{ticks_file.DATE_TO.month}_'
                        f'{ticks_file.DATE_TO.day}',
                format_extension=format_name)
            path = Path(out_filename_template).resolve()

            # Call a save function corresponding to the given format
            try:
                logger.info('Saving %s to .%s...', ticks_file.TITLE, format_name)
                Formats.save_match_format(ticks_file, format_)(path)

            except Exception as excpt:
                logger.error('ERROR while saving to .%s', format_name)
                print(excpt)
                return False

            if Path.is_file(path):  # Checking file actually saved and presents in the folder
                logger.info('Successfully saved to %s.%s\n', ticks_file.TITLE, format_name)
            else:
                print(ticks_file, format_, path, format_name)
                logger.error('ERROR while saving to .%s', format_name)
                return False
        self.collected_tickets.clear()

    def close_connection(self):
        """
        Close the connection to MT account, shutdowns terminal
        """
        if self.authorized:
            self.symbols_from_server.clear()
            self.company_name = None
            logger.info('Closing connection ...')
            mt5.shutdown()
            self.authorized = False
            logger.info('Connection closed')
        else:
            logger.warning('Connection was not established')

    def is_valid_symbol(self, symbol: str) -> bool:
        """

        :param symbol:
        :return: True if the symbol is valid, else False
        """
        if not self.symbols_from_server:
            logger.error("Didn't received symbols from server")
            return False
        if {symbol} > self.symbols_from_server:
            logger.warning('%s is not in the list of symbols from %s server',
                           symbol, self.company_name)
            return False
        return True

    def validate_symbols(self, symbols_list: str) -> tuple:
        """

        :param symbols_list:
        :return:
        """
        valid_symbols = [symbol for symbol in symbols_list if self.is_valid_symbol(symbol)]
        return tuple(valid_symbols)

    def get_ticks(self, symbols: tuple | str):
        """
        Function to get ticks of symbols
        :param symbols: Tuple of symbols from gui.symbols_to_get_tree
        """
        if not self.authorized:
            logger.error('Can\' get ticks - not logged in')
            return

        if not symbols:  # Base case for recursion
            logger.info('Done parsing ticks')
            if self.not_found_ticks:
                logger.info('Ticks not found for symbols: %s', self.not_found_ticks)
            return

        logger.info('Symbols in the queue - %s', symbols)
        current_symbol = symbols[0]

        logger.info('Parsing ticks of %s from date %s to %s',
                    current_symbol, self.utc_from, self.utc_to)
        ticks = mt5.copy_ticks_range(current_symbol, self.utc_from, self.utc_to, mt5.COPY_TICKS_ALL)
        status_code = mt5.last_error()

        match status_code[0]:
            case 1:
                if len(ticks):
                    logger.info('Ticks received: %i\n', len(ticks))
                    ticks_frame = pd.DataFrame(ticks)
                    ticks = Ticks(
                        TITLE=current_symbol,
                        DATAFRAME=ticks_frame,
                        DATE_FROM=self.utc_from,
                        DATE_TO=self.utc_to,
                        BROKER=''.join(self.company_name.split())
                      )
                    self.collected_tickets.append(ticks)
                else:
                    logger.warning('Symbol found but no ticks received')
                self.get_ticks(symbols=symbols[1::])
            case -3:
                logger.warning('Ticks dataframe is too large, will divide periods and glue')
                # self.get_ticks_partly(symbol=current_symbol)
            case -10001:
                logger.warning('Terminal is not launched.')
            case _:
                logger.error('Can\'t get ticks from %s; MT Last error - %s\n',
                             current_symbol, status_code)
                self.not_found_ticks.append(current_symbol)
                self.get_ticks(symbols=symbols[1::])

    def get_ticks_partly(self, symbol: tuple | str):
        ...
