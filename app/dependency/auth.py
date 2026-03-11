#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi import Request, HTTPException, status


async def parse_api_key(request: Request):
    api_key = request.headers.get("api-key")

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    return api_key
