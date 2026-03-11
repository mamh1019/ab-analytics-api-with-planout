#!/usr/bin/env python
# -*- coding: utf-8 -*-

from models.base.model import Model
from helpers.util import is_empty
from fastapi import HTTPException
from app.db.interface import IUser, ISegmentParams
from libs.geo_ip import GeoIP
from libs.date import Date
from helpers.query import Query
from app.config.constants import ABTestConfig


class ABTest(Model):
    async def get_app_id(self, api_key: str):
        sql = "SELECT app_id FROM app_api_keys WHERE api_key = :api_key"
        token_info = await self.fetchone(sql, {"api_key": api_key})
        if is_empty(token_info):
            raise HTTPException(status_code=400, detail="Invalid app token")

        return token_info.get("app_id")

    def get_ab_user_map_table(self, app_id: int):
        return f"ab_user_{(app_id % 10)}"

    def get_user_map_table(self, app_id: int):
        return f"app_user_map_{(app_id % 10)}"

    async def get_user_info(
        self, app_id: int, user_params: ISegmentParams, ip: str
    ) -> IUser:
        user_info = IUser()
        user_info.app_id = app_id
        user_info.uid = user_params.uid
        user_map_table = self.get_user_map_table(app_id)

        sql = f"SELECT * FROM {user_map_table} WHERE uid = :uid AND app_id = :app_id"
        user_map = await self.fetchone(
            sql, {"uid": user_info.uid, "app_id": user_info.app_id}
        )

        user_info.platform = user_params.platform
        user_info.country = (
            GeoIP.get_country(ip) if user_info.country == "ZZ" else user_info.country
        )

        if is_empty(user_map):
            user_map = {
                "app_id": user_info.app_id,
                "uid": user_info.uid,
                "platform": user_info.platform,
                "country": user_info.country,
                "join_date": int(Date.now()),
            }
            sql = Query.build_insert_statement(
                user_map_table, list(user_map.keys()), ignore=True
            )
            await self.execute(sql, user_map)

        user_info = user_info.model_copy(update=user_map)
        user_info.version = user_params.version

        return user_info

    async def get_ab_info(self, app_id: int):
        sql = "SELECT * FROM ab_experiment WHERE app_id = :app_id AND start_at <= now() AND enabled = 1"
        return await self.fetchall(sql, {"app_id": app_id})

    async def get_ab_user_info(self, app_id: int, uid: int, ab_id: int):
        sql = f"SELECT * FROM {self.get_ab_user_map_table(app_id)} WHERE uid = :uid AND app_id = :app_id AND ab_id = :ab_id"
        return await self.fetchone(sql, {"app_id": app_id, "uid": uid, "ab_id": ab_id})

    async def get_ab_info_with_user_info(self, app_id: int, uid: int):
        sql = f"""
            SELECT t1.*, t2.enabled, t2.parameters
            FROM {self.get_ab_user_map_table(app_id)} t1
            LEFT JOIN ab_experiment t2 ON t1.ab_id = t2.id
            WHERE t1.uid = :uid AND t1.app_id = :app_id 
        """
        res = await self.fetchone(sql, {"app_id": app_id, "uid": uid})
        return res

    async def set_ab_user_info(
        self,
        app_id: int,
        uid: int,
        ab_id: int,
        variation: str,
        callback: int = ABTestConfig.CALLBACK_READY,
    ):
        now = Date.now("%Y-%m-%d %H:%M:%S")
        ab_user = {
            "app_id": app_id,
            "uid": uid,
            "ab_id": ab_id,
            "ab_grp": variation,
            "callback": callback,
            "created_at": now,
            "updated_at": now,
        }
        sql = Query.build_insert_statement(
            self.get_ab_user_map_table(app_id),
            list(ab_user.keys()),
            dup_update_columns=[
                "ab_id",
                "ab_grp",
                "callback",
                "created_at",
                "updated_at",
            ],
        )
        await self.execute(sql, ab_user)

        ab_user["log_date"] = Date.now("%Y%m%d")
        del ab_user["created_at"]
        del ab_user["updated_at"]
        # set logs
        sql = Query.build_insert_statement(
            "ab_user_logs",
            list(ab_user.keys()),
            ignore=True,
        )
        await self.execute(sql, ab_user)

    async def update_ab_user_info_callback(
        self, app_id: int, uid: int, ab_user_info: dict
    ):
        """Set flag when callback is successfully received from client."""
        ab_user = {
            "uid": uid,
            "app_id": app_id,
            "ab_id": ab_user_info["ab_id"],
            "callback": ABTestConfig.CALLBACK_DONE,
            "updated_at": Date.now("%Y-%m-%d %H:%M:%S"),
        }
        sql = Query.build_update_statement(
            self.get_ab_user_map_table(app_id),
            ["callback", "updated_at"],
            ["uid", "app_id", "ab_id"],
        )
        await self.commit(sql, ab_user)

        ab_user["log_date"] = Date.now("%Y%m%d")
        ab_user["ab_grp"] = ab_user_info["ab_grp"]
        del ab_user["updated_at"]
        # set logs
        sql = Query.build_insert_statement(
            "ab_user_logs",
            list(ab_user.keys()),
            ignore=True,
        )
        await self.execute(sql, ab_user)
