# -*- coding: utf-8 -*-

import pandas as pd
from datetime import datetime, timedelta


class Date:
    @staticmethod
    def now(date_format="%Y%m%d"):
        return pd.to_datetime(datetime.now()).strftime(date_format)

    @staticmethod
    def yesterday(date_format="%Y%m%d"):
        return Date.sub_days(Date.str_to_datetime(Date.now()), 1, date_format)

    @staticmethod
    def add_days(origin_date, add_days=0, date_format="%Y%m%d"):
        return pd.to_datetime((origin_date + timedelta(days=int(add_days)))).strftime(date_format)

    @staticmethod
    def sub_days(origin_date, sub_days=0, date_format="%Y%m%d"):
        return pd.to_datetime((origin_date - timedelta(days=sub_days))).strftime(date_format)

    @staticmethod
    def date_interval(start: int, end: int):
        start_date = datetime.strptime(str(start), "%Y%m%d")
        end_date = datetime.strptime(str(end), "%Y%m%d")
        return abs((end_date - start_date).days)

    @staticmethod
    def str_to_datetime(date_str, date_format="%Y%m%d"):
        return datetime.strptime(date_str, date_format)

    @staticmethod
    def datetime_to_str(date_datetime, date_format="%Y%m%d"):
        return date_datetime.strftime(date_format)

    @staticmethod
    def str_to_month(date_str: str):
        date_str = str(date_str)
        if len(date_str) == 6:
            return date_str
        return pd.to_datetime(date_str).strftime("%Y%m")

    @staticmethod
    def real_end_func():
        real_end_date = pd.to_datetime("today") - pd.DateOffset(days=1)
        return real_end_date.strftime("%Y%m%d")

    @staticmethod
    def date_range(min_date, max_date):
        s_date = datetime.strptime(str(min_date), "%Y%m%d").date()
        e_date = datetime.strptime(str(max_date), "%Y%m%d").date()
        e_date = e_date + timedelta(days=1)

        for n in range(int((e_date - s_date).days)):
            yield s_date + timedelta(n)
