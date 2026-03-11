#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################
## bootstrap
###############################################################
from dotenv import load_dotenv
import sys

# import alias
sys.path.append("./app")
load_dotenv(override=True, verbose=True)

# packages
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from config import settings, Environment, ResponseCode
from routers import router
from contextlib import asynccontextmanager
from libs.kafka import Kafka
from libs.geo_ip import GeoIP
from libs.redis_client import RedisClient
from db.session import async_engine


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("init resources")
    await RedisClient.init_app(app)
    kafka = Kafka()
    await kafka.start(settings.kafka_brokers)
    GeoIP.initialize()
    yield
    await kafka.stop()
    await async_engine.dispose()
    await RedisClient.close_app(app)
    print("clear resources")


if settings.env != Environment.PROD:
    app = FastAPI(
        title=settings.app_name,
        swagger_ui_parameters=settings.swagger_ui_parameters,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        contact=settings.contact,
        lifespan=lifespan,
    )
else:
    app = FastAPI(docs_url=None, redoc_url=None, lifespan=lifespan)

app.include_router(router, prefix="/api")

print("################## Server Started ##################")
print(f"env: {settings.env}")
print(f"app_name: {settings.app_name}")
print(f"kafka_brokers: {settings.kafka_brokers}")
print(f"kafka_abtest_topic: {settings.kafka_abtest_topic}")
print(f"database_name: {settings.database_name}")
print(f"database_echo: {settings.database_echo}")
print(f"database_echo_pool: {settings.database_echo_pool}")
print(f"database_pool_pre_ping: {settings.database_pool_pre_ping}")
print(f"database_pool_size: {settings.database_pool_size}")
print(f"database_max_overflow: {settings.database_max_overflow}")
print(f"database_pool_recycle: {settings.database_pool_recycle}")
print(f"database_pool_timeout: {settings.database_pool_timeout}")
print("###################################################")


###############################################################
## exception handler
###############################################################
@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(_: Request, exc: RequestValidationError):
    # Pass FastAPI default format (exc.errors()) as details
    response_message = {
        "code": ResponseCode.UNPROCESSABLE_ENTITY,
        "message": "Validation error",
        "details": exc.errors(),  # [{type, loc, msg, input, ...}, ...]
    }

    return JSONResponse(
        status_code=ResponseCode.UNPROCESSABLE_ENTITY,
        content=response_message,
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: Exception):
    response_message = {
        "code": exc.status_code,
        "message": exc.detail,
        "details": None,
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=response_message,
    )


@app.exception_handler(Exception)
async def all_exception_handler(_: Request, exc: Exception):
    exc_type = type(exc).__name__
    exc_message = str(exc)
    full_message = f"{exc_type}: {exc_message}"
    response_message = {
        "code": ResponseCode.INTERNAL_SERVER_ERROR,
        "message": full_message,
    }

    return JSONResponse(
        status_code=ResponseCode.INTERNAL_SERVER_ERROR,
        content=response_message,
    )


###############################################################
## health check
###############################################################
@app.get("/")
async def index():
    return JSONResponse(status_code=401, content={"detail": "Unauthorized"})


@app.get("/live")
async def live():
    return {"status": "ok", "env": settings.env}
