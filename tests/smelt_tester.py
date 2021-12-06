#!/usr/bin/env python3
# coding=UTF-8
"""
Simple screenshot tool for quickly capturing the OSRS client window.
Compresses screenshot with pngcrush if it's available.
Automatically censors player's username with ImageMagick if it's available.

Produces an image in the format of `osrs_$(date +%Y-%m-%d_%H-%M-%S).png`
in the current directory.

Syntax:
    python3 screnshot.py [DELAY]

Example:
    python3 screenshot.py 5 = Wait 5 seconds before taking screenshot.

Optional positional arguments:
    DELAY (int): The number of seconds to wait before taking the
                 screenshot, default is 0.

"""
import datetime
import logging as log
import os
import pathlib
import subprocess
import sys
import time

import pyautogui as pag

current_dir = os.getcwd()

# Ensure ocvbot files are added to sys.path so they can be imported.
SCRIPTPATH = str(pathlib.Path(__file__).parent.parent.absolute())
sys.path.insert(1, SCRIPTPATH)
# Importing ocvbot modules changes the current dir to the directory the files are in.
from ocvbot import vision as vis, startup as start
from ocvbot import banking
from ocvbot import behavior
from ocvbot import inputs
from ocvbot import interface

vis.init()
log.basicConfig(
    format="%(asctime)s -- %(filename)s.%(funcName)s - %(message)s", level="INFO"
)
ARGUMENTS: int = len(sys.argv)

# If the name of the script is the only argument given, set the optional
#   arguments to their default values.
if ARGUMENTS == 1:
    DELAY = 0
elif ARGUMENTS == 2:
    DELAY = int(sys.argv[1])
else:
    raise Exception("Unsupported arguments!")


def main(region: tuple[int, int, int, int] = vis.CLIENT) -> str:
    """
    Takes a screenshot of the OSRS client window.

    Returns:
        Returns the filepath to the screenshot.
    """
    if DELAY > 0:
        log.info("Waiting %s seconds ...", DELAY)
        time.sleep(DELAY)

    banking.open_bank("west")
    banking.withdrawal_item(
        item_bank='./../ocvbot/needles/items/tin-ore-bank.png', 
        item_inv='./../ocvbot/needles/items/tin-ore.png', 
        conf=0.99,
        quantity='x')
    banking.withdrawal_item(
        item_bank='./../ocvbot/needles/items/copper-ore-bank.png', 
        item_inv='./../ocvbot/needles/items/copper-ore.png', 
        conf=0.99,
        quantity='x')

    bank_coords = [((91, 207), 3, (4, 7), (3, 9))]
    smelter_coords = [((112, 122), 1, (2, 2), (8, 12))]
    smelter_source = "./../ocvbot/needles/game-screen/al-kharid-smelt/furnace.png"
    behavior.travel(smelter_coords, './../ocvbot/haystacks/al-kharid.png')
    
    vis.Vision(
        region=vis.GAME_SCREEN,
        needle='./../ocvbot/needles/game-screen/al-kharid-smelt/furnace.png',
        loop_num=3,
        loop_sleep_range=(500, 1000),
        conf=0.85,
    ).click_needle()

    interface.enable_button(
        button_disabled='./../ocvbot/needles/items/copper-ore.png',
        button_disabled_region=vis.CHAT_MENU,
        button_enabled='./../ocvbot/needles/items/copper-ore.png',
        button_enabled_region=vis.CHAT_MENU,
        loop_num=10,
        conf=0.95,
    )

    inputs.Keyboard().keypress(key="space")
    
    
    return 


if __name__ == "__main__":
    main()
