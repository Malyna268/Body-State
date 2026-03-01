"""Schemas for Guardian Core inputs and outputs."""

from __future__ import annotations

from pydantic import BaseModel


class GuardianRequest(BaseModel):
    context: dict


class GuardianResponse(BaseModel):
    decision: dict
