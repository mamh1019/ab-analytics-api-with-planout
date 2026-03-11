#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional, List
from .base_interface import IBaseInterface


class IExperimentConditions(IBaseInterface):
    """Experiment condition definition"""

    platform: Optional[List[str]] = None
    country: Optional[List[str]] = None
    media_source: Optional[List[str]] = None
    version: Optional[List[str]] = None
    created_after: Optional[int] = None
    created_before: Optional[int] = None
    is_payer: Optional[bool] = None
    pay_amount: Optional[float] = None
