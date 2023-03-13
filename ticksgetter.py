from pathlib import Path
from functools import singledispatchmethod
from string import Template
from datetime import datetime
import MetaTrader5 as mt5
import pandas as pd
import pytz
from main import logger
from datatypes import Ticks, Formats
from accounts import LoginInfo, Accounts


class TicksGetter:
    """
    Collects ticks from a server using official MetaTrader5 package.
    """
    def __init__(self):
        """

        """
        self.company_name = None
        self.authorized = False
        self.timezone = pytz.timezone("Etc/UTC")
        self.utc_from = datetime(year=2021, month=1, day=1, tzinfo=self.timezone)
        self.utc_to = datetime(year=2022, month=1, day=1, tzinfo=self.timezone)
        self.not_found_ticks: list[str] = []
        self.symbols_from_server = set()
        self.collected_tickets: list[Ticks] = []
        self.template = Template(
                'ticks_${format}/${filename}_${broker}_${date_from}_${date_to}.$format_extension'
        )

    def get_account_from_string(self, account_name: str) -> LoginInfo | bool:
        """
        Gets LoginInfo corresponding to name from account_name argument.

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
            logger.error('Invalid account credentials')
            return False

        try:
            self.authorized = mt5.initialize(
                login=account_credentials.LOGIN,
                password=account_credentials.PASSWORD,
                server=account_credentials.SERVER,
                path=account_credentials.TERMINAL_PATH)
        except Exception as excpt:
            logger.error('Invalid login credentials, %s', excpt)
            return False
        logger.info('Launching MetaTrader at %s ...', account_credentials.TERMINAL_PATH)
        if not self.set_account_info():
            logger.error('Failed on setting account information')
            return False
        logger.info('Connected to %s (login: %s)\n', self.company_name, account_credentials.LOGIN)
        return True

    @login.register
    def _(self, account_credentials: str):
        account_credentials = self.get_account_from_string(account_name=account_credentials)
        return self.login(None, account_credentials=account_credentials)

    def set_account_info(self) -> bool:
        """
        Gets information of account and sets it to classes attributes.

        :return: True if account info set successfully, else False.
        """
        self.company_name = mt5.account_info().company
        self.symbols_from_server = {symbol.path for symbol in mt5.symbols_get()}
        if not self.symbols_from_server:
            logger.error('Did not receive symbols list from the server')
            return False
        logger.info('Got account information the server')
        return True

    def save_ticks_to_file(self, format_: Formats) -> bool:
        """
        Saves ticks to a file in one of the format from Formats class.

        :param format_: format to save to
        :return: False if saved file not found in the directory of corresponding format.
        """
        format_name = format_.value
        Path(f'ticks_{format_name}').mkdir(parents=True, exist_ok=True)
        for ticks_file in self.collected_tickets:
            out_filename_template = self.template.substitute(
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

            # Call a saving function corresponding to the given format
            logger.info('Saving %s to .%s...', ticks_file.TITLE, format_name)
            Formats.save_match_format(ticks_file, format_)(path)
            try:
                if Path.is_file(path):  # Checking file actually saved and presents in the folder
                    logger.info('Successfully saved to %s\n', path.name)
            except FileNotFoundError:
                logger.error('ERROR while saving to .%s', format_name)
                return False
        self.collected_tickets.clear()
        return True

    def close_connection(self):
        """
        Closes the connection to MT account, shutdowns terminal.
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

    def get_ticks(self, symbols: tuple | str) -> bool:
        """
        Function to get ticks of symbols.

        :param symbols: Tuple of symbols
        """
        if not self.authorized:
            logger.error('Can\' get ticks - not logged in')
            return False

        if not symbols:  # Base case for recursion
            logger.info('Done parsing ticks')
            if self.not_found_ticks:
                logger.info('Ticks not found for symbols: %s', self.not_found_ticks)
            return True

        logger.info('Symbols in the queue - %s', symbols)
        current_symbol = symbols[0]

        logger.info('Parsing ticks of %s from date %s to %s',
                    current_symbol, self.utc_from, self.utc_to)
        ticks = mt5.copy_ticks_range(current_symbol, self.utc_from, self.utc_to, mt5.COPY_TICKS_ALL)
        if self.match_status_code() == 1:
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
                self.not_found_ticks.append(current_symbol)
        else:
            logger.error('Can\'t get ticks from %s;\n', current_symbol)

        self.get_ticks(symbols=symbols[1::])

    def get_ticks_partly(self, symbol: tuple | str):
        ...

    def match_status_code(self) -> int:
        status_code = mt5.last_error()[0]
        match status_code:
            case -3:
                logger.warning('Out of memory')
            # self.get_ticks_partly(symbol=current_symbol)

            case -10001:
                logger.warning('Terminal is not launched.')

            case 1:
                logger.info('Status code OK')

            case _:
                logger.error('MT Last error - %s\n', status_code)
        return status_code



