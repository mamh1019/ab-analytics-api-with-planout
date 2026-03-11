#!/usr/bin/env python
# -*- coding: utf-8 -*-

# models/base.py
from typing import Optional, Dict, Any, List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from helpers.query import Query  # build_insert_statement 사용 가정


class Model:
    __tablename__ = ""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def fetchall(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        res = await self.db.execute(text(query), params or {})
        return list(res.mappings().all())

    async def fetchone(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        rows = await self.fetchall(query, params)
        return rows[0] if rows else None

    async def execute(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> None:
        await self.db.execute(text(query), params or {})

    async def commit(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        await self.execute(query, params)
        await self.db.commit()

    async def _insert(
        self,
        params: Dict[str, Any],
        ignore: bool = False,
        update_fields: Optional[list] = None,
    ) -> None:
        cols = list(params.keys())
        sql = Query.build_insert_statement(
            table=self.__tablename__,
            columns=cols,
            dup_update_columns=update_fields,
            ignore=ignore,
        )
        await self.commit(sql, params)
