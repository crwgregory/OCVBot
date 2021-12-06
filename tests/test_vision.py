# coding=UTF-8
"""
Unit tests for the vision.py module.
Linux only. Requires feh.
"""
import os

import pytest

import init_tests

# This statement exists to prevent the OCVBot imports from being re-ordered.
pass

# OCVBot modules must be imported after init_tests.
from ocvbot import vision as vis

image_directory = (os.path.dirname(__file__)) + "/test_vision/"

# COUNT_NEEDLES -----------------------------------------------------------------------------------

count_needles_pass_params = (
    ("./needles/items/iron-bar.png", 27, "01"),
    ("./needles/items/raw-anchovies.png", 8, "02"),
    ("./needles/items/raw-anchovies.png", 0, "03"),
    ("./needles/items/raw-anchovies.png", 18, "04"),
)


@pytest.mark.parametrize("params", count_needles_pass_params)
def test_count_needles_pass(params) -> None:
    needle_path, correct_number_of_needles, test_number = params
    init_tests.feh("count_needles", "pass", test_number, image_directory)
    result = vis.Vision(region=vis.INV, needle=needle_path, conf=0.988).count_needles()
    assert result == correct_number_of_needles
    init_tests.kill_feh()
    