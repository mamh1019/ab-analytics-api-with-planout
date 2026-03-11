#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import wraps
from fastapi.responses import JSONResponse


def wrap_api(func):
    """Convert API response to common format."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        return JSONResponse(content={"code": 200, "data": response})

    return wrapper
