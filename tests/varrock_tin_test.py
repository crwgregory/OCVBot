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
from ocvbot import skills
from ocvbot import misc

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

    prefix = "./needles/game-screen/varrock-east-mine/bronze/"
    haystack_map = "./haystacks/varrock-east-mine.png"
    drop_ore_config = False

    ore = "./needles/items/tin-ore.png"
    mining = skills.Mining(
        rocks=[
            (prefix + "north-tin-full.png", prefix + "north-tin-empty.png"),
            (prefix + "west-tin-full.png", prefix + "west-tin-empty.png"),
        ],
        ore=ore,
        drop_sapphire=False,
        drop_emerald=False,
        drop_ruby=False,
        drop_diamond=False,
        drop_clue_geode=False,
    )

    bank_from_mine = [
        ((253, 181), 5, (35, 35), (1, 6)),
        ((112, 158), 5, (20, 20), (1, 6)),
        ((108, 194), 1, (10, 4), (3, 8)),
    ]

    mine_from_bank = [
        ((240, 161), 5, (35, 35), (1, 6)),
        ((262, 365), 5, (25, 25), (1, 6)),
        ((225, 419), 1, (4, 4), (3, 8)),
    ]

    for _ in range(10000):
        try:
            mining.mine_multiple_rocks()
            misc.sleep_rand_roll(chance_range=(200, 300))
        except start.TimeoutException:
            misc.sleep_rand_roll(chance_range=(50, 60))
        except start.InventoryFull:
            misc.sleep_rand_roll(chance_range=(50, 60), sleep_range=(1000, 120000))
            if drop_ore_config is True:
                mining.drop_inv_ore()
            else:
                behavior.travel(bank_from_mine, haystack_map)
                banking.open_bank("south")
                misc.sleep_rand_roll()

                # Deposit all possible mined items.
                for item in [
                    ore,
                    "./needles/items/uncut-sapphire.png",
                    "./needles/items/uncut-emerald.png",
                    "./needles/items/uncut-ruby.png",
                    "./needles/items/uncut-diamond.png",
                    "./needles/items/clue-geode.png",
                ]:
                    banking.deposit_item(item=item, quantity="all")

                behavior.travel(mine_from_bank, haystack_map)
                misc.sleep_rand_roll()
            # Roll for randomized actions when the inventory is full.
            behavior.logout_break_range()

            misc.session_duration(human_readable=True)
        # Logout when anything else unexpected occurs.
        except (Exception, start.InefficientUseOfInventory):
            behavior.logout()


    return 


if __name__ == "__main__":
    main()
