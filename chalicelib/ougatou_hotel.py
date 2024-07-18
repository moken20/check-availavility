import re
from datetime import date
from typing import Dict, List, Union

from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from chalicelib.base_scraper import Scraper
from chalicelib.util.dict_util import merge_lists_in_dict
from aws_lambda_powertools import Logger

logger = Logger(child=True) 

BASE_URL = "https://www.ougatou.jp/booking/"


class ScrapeOugatou(Scraper):
    def __init__(
        self,
        start_date: None | date = None,
        end_date: None | date = None,
    ) -> None:
        super().__init__(base_url=BASE_URL, start_date=start_date, end_date=end_date)

    def _get_vacant_table(self, page: BeautifulSoup) -> BeautifulSoup:
        return page.find("table", {"class": "table table-bordered vacant-list"})

    def _separate_dates_from_table(
        self, vacant_table: BeautifulSoup
    ) -> Union[List[str], BeautifulSoup]:
        column_line = vacant_table.findNext()
        date_classes = column_line.find_all("th", class_=re.compile("day-cell wk"))
        date_list = [
            date_class.text.strip().replace("\n", " ") for date_class in date_classes
        ]
        vacant_table = column_line.find_next_siblings()
        return date_list, vacant_table

    def _search_avail_rooms(
        self, date_list, vacant_table: BeautifulSoup, filtering=True
    ) -> Dict[str, List[str]]:
        available_rooms = {}

        for room_status in vacant_table:
            status_list = room_status.find_all(string=re.compile("満室|残室"))
            avail_date_list = [
                date_list[i] for i, elem in enumerate(status_list) if "残室" in elem
            ]

            if avail_date_list:
                room_name = (
                    room_status.find("td", {"class", "room-name"})
                    .text.strip()
                    .replace("\u3000", " ")
                )
                if "3名以上" in room_name:
                    continue
                available_rooms[room_name] = avail_date_list
        return available_rooms

    def get_availability(self, filtering=True) -> Dict[str, List[str]]:
        current_date = self.start_date
        available_rooms = {}

        while current_date < self.end_date:
            page = self.get_page(
                year=current_date.year, month=current_date.month, day=current_date.day
            )
            vacant_table = self._get_vacant_table(page)
            date_list, vacant_table = self._separate_dates_from_table(vacant_table)
            available_rooms = merge_lists_in_dict(
                old=available_rooms,
                new=self._search_avail_rooms(date_list, vacant_table, filtering),
            )

            current_date += relativedelta(weeks=1)
        logger.info(f'Outagou hotel current availability: {available_rooms}')
        return available_rooms
