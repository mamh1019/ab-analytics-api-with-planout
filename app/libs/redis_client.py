# -*- coding: utf-8 -*-
#
# redis_ops.py
# FastAPI lifespan + redis.asyncio 버전 (namespace 스타일)

import redis.asyncio as aioredis
from typing import Optional
from fastapi import Request
from config.settings import settings
from app.db.interface import IUser
from config.constants import RedisKey


class RedisClient:
    """FastAPI 프로세스(워커)당 1개의 Redis 인스턴스 관리"""

    @staticmethod
    async def init_app(app) -> None:
        if getattr(app.state, "redis", None) is None:
            app.state.redis = aioredis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                db=settings.redis_db,
                decode_responses=True,
                encoding="utf-8",
                retry_on_timeout=True,
            )
            await app.state.redis.ping()
            print("🚀 Redis Initialized")

    @staticmethod
    async def close_app(app) -> None:
        r: Optional[aioredis.Redis] = getattr(app.state, "redis", None)
        if r is not None:
            await r.close()
            await r.connection_pool.disconnect()
            print("🛑 Redis Closed")
            app.state.redis = None

    @staticmethod
    def from_request(request: Request) -> aioredis.Redis:
        r = getattr(request.app.state, "redis", None)
        if r is None:
            raise RuntimeError("Redis not initialized. Did you wire lifespan?")
        return r


# ---------- Composite Helper ----------
def build_user_info_key(app_id: int, uid: int) -> str:
    return f"{RedisKey.PREFIX_USER_INFO}:{app_id}:{uid}"


def build_user_pay_key(app_id: int, uid: int) -> str:
    return f"{RedisKey.PREFIX_USER_PAY}:{app_id}:{uid}"


async def get_cached_user_info(
    request: Request, app_id: int, uid: int
) -> Optional[IUser]:
    if not settings.redis_cache:
        return None

    """
    Redis 해시 기반에서 유저 정보 + 결제 정보를 합쳐서 IUser 객체 반환
    - 유저 정보가 없으면 None
    - 결제 정보가 없으면 pay_count=0, pay_amount=0.0
    """
    cli = RedisClient.from_request(request)

    # --- 유저 정보 조회 (Hash) ---
    user_data = await cli.hgetall(build_user_info_key(app_id, uid))
    if not user_data:  # 키 없음 → None 반환
        return None

    # --- IUser 인스턴스 생성 ---
    user = IUser()
    user.app_id = int(app_id)
    user.uid = int(user_data.get("uid", uid))
    user.platform = user_data.get("platform", user.platform)
    user.country = user_data.get("country", user.country)
    user.media_source = user_data.get("media_source", user.media_source)
    user.join_date = int(user_data.get("join_date", 0))

    # --- 결제 정보 조회 (Hash) ---
    pay_data = await cli.hgetall(build_user_pay_key(app_id, uid))
    if pay_data:
        user.pay_count = int(pay_data.get("pay_count", 0))
        user.pay_amount = float(pay_data.get("pay_amount", 0))
    else:
        user.pay_count = 0
        user.pay_amount = 0.0

    return user
