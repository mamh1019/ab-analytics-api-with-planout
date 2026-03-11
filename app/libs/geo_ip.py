#!/usr/bin/env python
# -*- coding: utf-8 -*-

import geoip2.database
from config.settings import settings


class GeoIP:
    _geo_reader = None

    @classmethod
    def initialize(cls):
        if cls._geo_reader is None:
            mmdb_path = settings.geo_ip_path
            cls._geo_reader = geoip2.database.Reader(mmdb_path)
            print("🚀 GeoIP initialized")

    @classmethod
    def get_country(cls, ip: str) -> str:
        try:
            response = cls._geo_reader.country(ip)
            if response and hasattr(response, "country"):
                geo_country = response.country.iso_code  # pylint: disable=maybe-no-member
                if geo_country is not None:
                    return geo_country
        except Exception:
            return "ZZ"
