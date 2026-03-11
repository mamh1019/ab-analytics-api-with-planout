# -*- coding: utf-8 -*-

import re
import time


def apply_dict_tree(origin_dict: dict, tree_nodes: list, node_value: any) -> None:
    """set dict key by list order
    dict = {}
    list = ['A', 'B', 'C']
    apply_dict_tree(dict, list, 1000)
    print(dict)
    {'A': {'B': {'C': 1000}}}
    """
    tmp = None
    max_index = len(tree_nodes) - 1
    for index, node in enumerate(tree_nodes):
        if tmp is None:
            next_val = {}
            if index == max_index:
                next_val = node_value
            tmp = origin_dict.setdefault(node, next_val)
        else:
            val = node_value if index == max_index else {}
            tmp = tmp.setdefault(node, val)


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


def list_intersect(a: list, b: list) -> list:
    return list(set(a).intersection(b))


def my_ip() -> str:
    import socket

    return socket.gethostbyname(socket.gethostname())


def get_campaign_id(campaign_name):
    r = re.findall(r"\((.*)\)", campaign_name)
    if r is None:
        return campaign_name
    if len(r) <= 0:
        return campaign_name
    return r[len(r) - 1]


def text_compress(text):
    import zlib
    import base64

    return base64.b64encode(zlib.compress(bytes(text, "utf-8"))).decode("ascii")


def text_decompress(encoded_data):
    import zlib
    import base64

    compressed_data = base64.b64decode(encoded_data.encode("ascii"))
    return zlib.decompress(compressed_data).decode("utf-8")


def array_split(arr: list, split_num: int):
    import numpy as np

    return np.array_split(arr, np.ceil(len(arr) / split_num))


def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_float(value):
    try:
        float(value)
        return "." in value
    except ValueError:
        return False


def is_number(value):
    return is_integer(value) or is_float(value)


def pp(obj: any):
    from datetime import datetime

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
    print(f"[{current_time}] {obj}")


class Timer:
    """For performance measurement"""

    @classmethod
    def start(cls):
        cls.start_time = time.time()

    @classmethod
    def end(cls):
        elapsed_time = time.time() - cls.start_time
        print("---%s seconds---" % elapsed_time)
        return elapsed_time


from fastapi import Request


def get_ip(request: Request):
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0]
    else:
        client_ip = request.client.host

    return client_ip
