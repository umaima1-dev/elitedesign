"""Validated parameter models. ``extra=forbid`` so a typo in a recipe is an error,
not a silently ignored setting."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Focus(BaseModel):
    """Rectangle (0..1, relative to the image) that receives extra detail, e.g. a face."""

    model_config = ConfigDict(extra="forbid")
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)
    w: float = Field(gt=0, le=1)
    h: float = Field(gt=0, le=1)


class SketchParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    style: Literal["pencil", "lineart", "hatch", "value"] = "pencil"
    detail: int = Field(60, ge=0, le=100, description="Higher keeps finer detail")
    contrast: int = Field(50, ge=0, le=100)
    shadow: int = Field(50, ge=0, le=100, description="Depth of the dark tones")
    line_weight: float = Field(1.5, ge=0.0, le=8.0)
    line_threshold: int = Field(30, ge=0, le=100, description="Line sensitivity (lineart)")
    levels: int = Field(4, ge=2, le=8, description="Hatch layers / value-study tones")
    hatch_spacing: float = Field(8.0, ge=2.0, le=40.0)
    hatch_flow: bool = True
    hatch_angle: int = Field(45, ge=0, le=179)
    outline: int = Field(20, ge=0, le=100, description="Contour lines mixed into non-lineart styles")
    jitter: int = Field(30, ge=0, le=100, description="Hand-drawn wobble of hatch lines")
    grain: int = Field(30, ge=0, le=100)
    paper: Literal["white", "cream"] = "white"
    grid_cols: int = Field(0, ge=0, le=80, description="Transfer grid, 0 = off")
    focus: Focus | None = None
    focus_boost: int = Field(35, ge=0, le=100)
    seed: int = Field(7, ge=0, le=2**31 - 1)
    print_width_cm: float | None = Field(30.0, gt=0, le=500)


class PBNParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    colors: int = Field(12, ge=2, le=48)
    pre_smooth: int = Field(4, ge=0, le=10, description="Smooths texture before choosing colours")
    cleanup: int = Field(1, ge=0, le=3, description="Majority-filter passes on the colour map")
    min_shape_mm: float = Field(5.0, ge=1.0, le=40.0, description="Smallest shape diameter at print size")
    edge_smooth: int = Field(5, ge=0, le=10)
    line_weight: float = Field(1.0, ge=0.2, le=4.0)
    numbers: bool = True
    legend: bool = True
    view: Literal["canvas", "guide", "painted"] = "canvas"
    seed: int = Field(7, ge=0, le=2**31 - 1)
    print_width_cm: float = Field(30.0, gt=0, le=500)
