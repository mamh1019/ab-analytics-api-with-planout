#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    #######################################################################
    # Project Settings
    #######################################################################
    app_name: str = "AB Analytics API with Planout"
    env: str
    swagger_ui_parameters: dict = {"tryItOutEnabled": True}
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    contact: dict = {
        "name": "mamh1019@gmail.com",
        "email": "mamh1019@gmail.com",
    }

    #######################################################################
    # Operation Settings
    #######################################################################
    redis_cache: bool = True

    #######################################################################
    # Kafka Settings
    #######################################################################
    kafka_brokers: str
    kafka_abtest_topic: str

    #######################################################################
    # Redis Settings
    #######################################################################
    redis_host: str
    redis_port: int
    redis_db: int

    #######################################################################
    # Database Settings
    #######################################################################
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    database_echo: bool
    database_echo_pool: bool
    database_pool_pre_ping: bool
    database_pool_size: int
    database_max_overflow: int
    database_pool_timeout: int
    database_pool_recycle: int

    #######################################################################
    # Resource Settings
    #######################################################################
    root_path: str = os.path.dirname(os.path.dirname(__file__))
    geo_ip_path: str = os.path.join(root_path, "resources", "GeoIP2-Country.mmdb")

    @property
    def database_url(self) -> str:
        # Encode password (handle special characters)
        password_encoded = quote_plus(self.database_password)

        # Return in SQLAlchemy URL format
        return f"mysql+aiomysql://{self.database_user}:{password_encoded}@{self.database_host}:{self.database_port}/{self.database_name}"


settings = Settings()
