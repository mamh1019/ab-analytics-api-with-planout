#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Environment:
    PROD = "prod"
    DEV = "dev"


class ResponseCode:
    SUCCESS = 200
    UNAUTHORIZED = 401
    UNPROCESSABLE_ENTITY = 422
    INTERNAL_SERVER_ERROR = 500


class SegmentStatus:
    NONE = "none"  # Not eligible for experiment
    ASSIGNED = "assigned"  # Experiment assigned


class CallbackStatus:
    READY = 0
    DONE = 1


class ABTestConfig:
    RE_ASSIGN_PERCENT = 0.5
    CALLBACK_READY = 0
    CALLBACK_DONE = 1
    REPEAT_COUNT = 30


class KafkaMessage:
    AB_TEST_TOPIC = "ab-test"  ## Main category
    AB_TEST_CATEGORY_USER_CALLBACK = "ab-test-user-callback"  ## Sub category


class RedisKey:
    PREFIX_USER_INFO = "abtest:user:u"
    PREFIX_USER_PAY = "abtest:user:p"
