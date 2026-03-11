#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import random
from fastapi.routing import APIRouter
from fastapi import Request, Depends
from dependency.auth import parse_api_key
from decorators.wrap_api import wrap_api
from helpers.util import get_ip
from db.connection import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from db.interface import (
    IUser,
    IExperimentConditions,
    ISegmentParams,
    ISegmentResponse,
    ISegmentCallbackParams,
    ISegmentCallbackResponse,
)
from models.abtest import ABTest
from libs.ab_experiment import ABTestExperiment
from config.constants import SegmentStatus, ABTestConfig, CallbackStatus, KafkaMessage
from helpers.util import is_empty
from libs.kafka import Kafka
from libs.redis_client import get_cached_user_info

router = APIRouter()


@router.post(
    "/segment",
    summary="AB Experiment Info Reception & Assignment API",
    response_model=ISegmentResponse,
    description="""Checks user's A/B group participation. If the response status is `assigned`, the user can receive AB group data.""",
)
@wrap_api
async def segment(
    _request: Request,
    params: ISegmentParams,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(parse_api_key),
):
    # token check
    model: ABTest = ABTest(db)
    app_id = await model.get_app_id(api_key)
    if params.uid <= 0:
        return ISegmentResponse(status=SegmentStatus.NONE).to_dict(exclude_none=True)

    # data load
    user_info: IUser = await get_cached_user_info(_request, app_id, params.uid)
    if is_empty(user_info):
        user_info = await model.get_user_info(app_id, params, get_ip(_request))

    need_assigned: bool = True

    # define response
    response = ISegmentResponse(status=SegmentStatus.NONE)

    # Check if user is currently participating in an experiment
    # If experiment is active, return ongoing experiment data
    # If experiment is expired, determine re-participation eligibility
    ab_user_info = await model.get_ab_info_with_user_info(app_id, user_info.uid)
    if is_empty(ab_user_info):
        # If user has no experiment participation history, assign to matching experiment
        need_assigned = True
    else:
        if ab_user_info.enabled == 0:
            # Determine re-participation eligibility after experiment expiration
            # Decision based on re-assignment probability (adjustable via config)
            need_assigned = (
                True if random.random() < ABTestConfig.RE_ASSIGN_PERCENT else False
            )
        elif ab_user_info.enabled == 1:
            # User callback already received and experiment is active, return existing info
            need_assigned = False
            response = ISegmentResponse(
                status=SegmentStatus.ASSIGNED,
                callback_done=ab_user_info.callback,
                abtest_id=ab_user_info.ab_id,
                abtest_group=ab_user_info.ab_grp,
                abtest_parameters=_get_group_parameters(
                    json.loads(ab_user_info.parameters), ab_user_info.ab_grp
                ),
            )

    if need_assigned is True:
        ab_info = await model.get_ab_info(user_info.app_id)

        # Multiple experiments can run simultaneously, but only one applies
        # Query multiple experiments to find the first matching one
        for row in ab_info:
            conditions = IExperimentConditions(**json.loads(row.conditions))
            conditions_check = False

            # Check user data from database
            for key in conditions.keys(exclude_none=True):
                if key == "platform" and user_info.platform not in list(
                    conditions.platform
                ):
                    conditions_check = True
                    break
                if key == "country" and user_info.country not in list(
                    conditions.country
                ):
                    conditions_check = True
                    break
                if key == "media_source" and user_info.media_source not in list(
                    conditions.media_source
                ):
                    conditions_check = True
                    break
                if key == "version" and user_info.version not in list(
                    conditions.version
                ):
                    conditions_check = True
                    break
                if (
                    key == "created_after"
                    and user_info.join_date < conditions.created_after
                ):
                    # User cannot participate if join date is before created_after
                    conditions_check = True
                    break
                if (
                    key == "created_before"
                    and user_info.join_date > conditions.created_before
                ):
                    # User cannot participate if join date is after created_before
                    conditions_check = True
                    break
                if key == "is_payer" and user_info.pay_count <= 0:
                    conditions_check = True
                    break
                if key == "pay_amount" and user_info.pay_amount < conditions.pay_amount:
                    conditions_check = True
                    break

            if conditions_check:
                continue

            # Set experiment group
            exp = ABTestExperiment(userid=user_info.uid, meta=row)
            in_experiment = exp.get("in_experiment")
            abtest_id = row["id"]
            abtest_group = exp.get("variation")

            if in_experiment:
                response.status = SegmentStatus.ASSIGNED
                response.callback_done = CallbackStatus.READY
                response.abtest_id = abtest_id
                response.abtest_group = abtest_group
                response.abtest_parameters = _get_group_parameters(
                    json.loads(row.parameters), abtest_group
                )
                break

    return response.to_dict(exclude_none=True)


def _get_group_parameters(abtest_parameters: dict, abtest_group: str) -> dict:
    if abtest_group in abtest_parameters:
        return abtest_parameters[abtest_group]
    else:
        return {}


@router.post(
    "/segment/callback",
    summary="Client AB Group Receipt Confirmation API",
    response_model=ISegmentCallbackResponse,
    description="When a client receives A/B data assigned via Segment API, it sends a callback to the server for receipt confirmation.<BR> The user is classified as an A/B user in metrics only after this callback is received.",
)
@wrap_api
async def callback(
    _request: Request,
    params: ISegmentCallbackParams,
    db: AsyncSession = Depends(get_db),
    api_key: str = Depends(parse_api_key),
):
    # token check
    model: ABTest = ABTest(db)
    app_id = await model.get_app_id(api_key)
    ab_user_info = await model.get_ab_user_info(app_id, params.uid, params.abtest_id)

    if (
        not is_empty(ab_user_info)
        and ab_user_info.callback == ABTestConfig.CALLBACK_READY
    ):
        await model.update_ab_user_info_callback(app_id, params.uid, ab_user_info)

        kafka_instance = Kafka.instance()
        await kafka_instance.send(
            KafkaMessage.AB_TEST_CATEGORY_USER_CALLBACK, dict(ab_user_info)
        )

    return ISegmentCallbackResponse(message="success").to_dict()
