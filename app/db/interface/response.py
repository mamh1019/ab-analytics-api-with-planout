#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional
from .base_interface import IBaseInterface


class ISegmentResponse(IBaseInterface):
    """Response format definition for segment call"""

    status: str

    # Whether callback needs to be sent
    callback_done: Optional[int] = None

    # Actual group assignment information
    abtest_id: Optional[int] = None
    abtest_group: Optional[str] = None
    abtest_parameters: Optional[dict] = None


class ISegmentCallbackResponse(IBaseInterface):
    """Response format definition for segment callback"""

    message: str
