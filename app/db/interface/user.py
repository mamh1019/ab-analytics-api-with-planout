#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from .base_interface import IBaseInterface


class IUser(IBaseInterface):
    app_id: int = 0
    uid: int = 0
    platform: str = "unknown"
    country: str = "ZZ"
    media_source: str = "Organic"
    pay_count: int = 0
    pay_amount: float = 0.0
    join_date: int = 0
    version: str = "0.0.0"

    @property
    def is_nru(self) -> bool:
        today = datetime.today().strftime("%Y%m%d")
        return str(self.join_date) == today
