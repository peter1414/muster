"""
Unit tests for the pure standards-calculation logic, unchanged from the
original app. Locks in the min/competitive/max tier boundaries and the
mm:ss parsing since a mobile client will build UI directly against these.
"""
import pytest

from muster.standards import (
    STANDARDS,
    format_seconds,
    parse_time_to_seconds,
    progress_ratio,
)


def test_format_seconds():
    assert format_seconds(585) == "9:45"
    assert format_seconds(60) == "1:00"
    assert format_seconds(9) == "0:09"


def test_parse_time_to_seconds():
    assert parse_time_to_seconds("9:45") == 585
    assert parse_time_to_seconds(" 1:05 ") == 65


def test_parse_time_to_seconds_rejects_bad_input():
    with pytest.raises(ValueError):
        parse_time_to_seconds("945")
    with pytest.raises(ValueError):
        parse_time_to_seconds("9:99")


@pytest.mark.parametrize(
    "value,expected_tier",
    [
        (30, "below"),
        (50, "min"),
        (80, "competitive"),
        (100, "max"),
        (150, "max"),
    ],
)
def test_progress_ratio_reps_based(value, expected_tier):
    std = STANDARDS["pushups"]
    _ratio, tier = progress_ratio(value, std)
    assert tier == expected_tier


@pytest.mark.parametrize(
    "seconds,expected_tier",
    [
        (700, "below"),   # slower than min(630)
        (630, "min"),     # exactly at the passing line
        (540, "competitive"),
        (495, "max"),
        (400, "max"),     # faster than max still caps at "max"
    ],
)
def test_progress_ratio_time_based(seconds, expected_tier):
    std = STANDARDS["run_1_5mi"]
    _ratio, tier = progress_ratio(seconds, std)
    assert tier == expected_tier


def test_progress_ratio_bounds_are_0_to_1():
    std = STANDARDS["pushups"]
    ratio, _ = progress_ratio(-100, std)
    assert ratio == 0.0
    ratio, _ = progress_ratio(10000, std)
    assert ratio == 1.0
