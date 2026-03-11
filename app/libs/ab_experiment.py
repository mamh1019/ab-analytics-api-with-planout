# -*- coding: utf-8 -*-

import sys
import os

sys.path.insert(0, os.path.abspath("./app/libs"))

from libs.planout.experiment import DefaultExperiment
from libs.planout.ops.random import UniformChoice, RandomFloat, WeightedChoice
from datetime import datetime

# from config.constants import ABTestConfig


class ABTestExperiment(DefaultExperiment):
    def __init__(self, userid: str, meta: dict):
        self.meta = meta
        self.salt = f"experiment_{meta['id']}"
        self.name = f"experiment_{meta['id']}"
        self.set_auto_exposure_logging(False)

        super().__init__(userid=userid)

    def assign(self, params, userid):  # pylint: disable=W0221
        meta = self.meta

        now = datetime.now()
        start = meta["start_at"]
        end = (
            datetime(2050, 1, 1)
            if meta["end_at"] == "0000-00-00 00:00:00"
            else meta["end_at"]
        )
        if isinstance(start, str):
            start = datetime.strptime(meta["start_at"], "%Y-%m-%d %H:%M:%S")

        if isinstance(end, str):
            end = datetime.strptime(meta["end_at"], "%Y-%m-%d %H:%M:%S")

        if not meta["enabled"] or not (start <= now <= end):
            params.in_experiment = False
            params.participated = False
            params.variation = "default"
            return

        experiment_unit = str(userid) + "." + str(meta["id"])
        part_rate = float(meta.get("part_rate"))
        # part_rate = 1 - (1 - part_rate) ** (1 / ABTestConfig.REPEAT_COUNT)

        params.exp_group = RandomFloat(min=0.0, max=1.0, unit=experiment_unit)
        if params.exp_group < meta.get("participation_rate", part_rate):
            if meta.get("weights"):
                params.variation = WeightedChoice(
                    choices=meta["choices"].split(","),
                    weights=[float(w) for w in meta["weights"].split(",")],
                    unit=userid,
                )
            else:
                params.variation = UniformChoice(
                    choices=meta["choices"].split(","),
                    unit=userid,
                )
            params.in_experiment = True
            params.participated = True
        else:
            params.variation = "default"
            params.in_experiment = False
            params.participated = False
