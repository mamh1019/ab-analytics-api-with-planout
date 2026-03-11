#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fastapi.routing import APIRouter
from .abtest.controller import router as abtest_router

router = APIRouter()
router.include_router(abtest_router, prefix="/abtest")


#######################################################################
# 테스트 라우터
#######################################################################
from .tests.controller import router as tests_router

router.include_router(tests_router, prefix="/tests")
