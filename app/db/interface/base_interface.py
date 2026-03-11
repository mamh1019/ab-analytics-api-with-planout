#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pydantic import BaseModel


class IBaseInterface(BaseModel):
    def to_dict(self, exclude_none: bool = False):
        return self.model_dump(exclude_none=exclude_none)

    def keys(self, exclude_none: bool = False):
        return self.model_dump(exclude_none=exclude_none).keys()
