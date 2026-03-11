#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .base_interface import IBaseInterface


class ISegmentParams(IBaseInterface):
    uid: int
    platform: str
    version: str


class ISegmentCallbackParams(IBaseInterface):
    abtest_id: int
    uid: int
