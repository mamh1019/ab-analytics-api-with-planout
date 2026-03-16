# -*- coding: utf-8 -*-

from fastapi import Request


def is_empty(obj: any) -> any:
    import numpy as np

    if obj == "" or obj is None:
        return True
    if type(obj) == float and np.isnan(obj):
        return True
    if type(obj) in [list, tuple] and len(obj) <= 0:
        return True
    if type(obj) == dict and len(obj.keys()) <= 0:
        return True
    return False


def get_ip(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0]
    else:
        client_ip = request.client.host

    return client_ip
