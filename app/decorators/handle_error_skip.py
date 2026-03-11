#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps


def handle_error_skip(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except Exception:
            # Return None to keep server running even if exception occurs
            return None

    return wrapper
