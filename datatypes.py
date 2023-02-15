"""
Ticks and Formats data structures
"""
from datetime import datetime
from typing import NamedTuple, Callable
from enum import Enum

import pandas as pd


class Ticks(NamedTuple):
    """
    A NamedTuple representing the data of parsed ticks.
     Attributes:
         TITLE (str):
            Title of the symbol.
         DATAFRAME (pd.DataFrame):
            Dataframe containing ticks.
         DATE_FROM (datetime):
            Starting date of ticks.
         DATE_TO (datetime):
            Ending date of ticks.
         BROKER (str):
            Name of broker from which the ticks parsed.
    """
    TITLE: str
    DATAFRAME: pd.DataFrame
    DATE_FROM: datetime
    DATE_TO: datetime
    BROKER: str


class Formats(Enum):
    """
    Enumeration of possible file formats.
        Attributes:
        PKL (str): The pickle format.
        CSV (str): The CSV format.
        HTML (str): The HTML format.
        JSON (str): The JSON format.
        XML (str): The XML format.
        XLSX (str): The XLSX format.
    """
    PKL = 'pkl'
    CSV = 'csv'
    HTML = 'html'
    JSON = 'json'
    XML = 'xml'
    XLSX = 'xlsx'

    @classmethod
    def save_match_format(cls, ticks_file: Ticks, format_) -> Callable:
        """
        Returns the appropriate file format save method.
        :param ticks_file:
        :param format_: ticks_file (Ticks): Dataframe to save.
        :return: A callable function, which saves the dataframe to the specified format.

        """
        return {
            Formats.PKL:  ticks_file.DATAFRAME.to_pickle,
            Formats.CSV:  ticks_file.DATAFRAME.to_csv,
            Formats.HTML: ticks_file.DATAFRAME.to_html,
            Formats.JSON: ticks_file.DATAFRAME.to_json,
            Formats.XML:  ticks_file.DATAFRAME.to_xml,
            Formats.XLSX: ticks_file.DATAFRAME.to_excel,
        }.get(format_)

    #
    # def __getitem__(self, item):
    #     print(f'returning {item.name} source {item}')
    #     return item.name
