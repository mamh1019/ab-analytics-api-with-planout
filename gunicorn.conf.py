#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import signal
import multiprocessing

# core options
env = os.environ.get("env")

host = "0.0.0.0"
port = 8001
use_loglevel = "info"
limit_request_line = 0
limit_request_field_size = 0
limit_request_body = 30 * 1024 * 1024  # 30MB
web_concurrency = max(2, multiprocessing.cpu_count())
worker_class = "uvicorn.workers.UvicornWorker"

# define
bind = f"{host}:{port}"
workers = web_concurrency
keepalive = 20
timeout = 90
# max_requests = 20000
# max_requests_jitter = 2000
errorlog = "-"
loglevel = "error" if env == "prod" else "warning"
preload_app = False


def worker_int(worker):
    os.kill(worker.pid, signal.SIGINT)


print(
    {
        "workers": workers,
        "worker_class": worker_class,
        "bind": bind,
        "timeout": timeout,
        "keepalive": keepalive,
        "loglevel": loglevel,
    }
)
