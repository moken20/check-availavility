import logging
import urllib
from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Dict, List

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)


class Scraper(metaclass=ABCMeta):
    def __init__(
        self,
        base_url: str,
        start_date: None | date = None,
        end_date: None | date = None,
    ) -> None:
        self.base_url = base_url

        if not start_date:
            start_date = date.today() + relativedelta(days=2)
        if not end_date:
            end_date = start_date + relativedelta(months=2)
        self.start_date = start_date
        self.end_date = end_date

    def get_page(self, **url_param) -> BeautifulSoup:
        """Request and prase reservation page"""
        query = urllib.parse.urlencode(url_param)
        url = self.base_url + "?" + query
        res = requests.get(url)

        return BeautifulSoup(res.text, "html.parser")

    def search_avail_rooms(self, vacant_table: BeautifulSoup) -> Dict[str, List[str]]:
        """extract vacant room name and dates from page"""
        pass

    @abstractmethod
    def get_availability(self, **filtering_cond):
        """get all vacant room name and dats in given period"""
        pass
