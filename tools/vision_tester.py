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


def pngcrush(filename: str) -> None:
    try:
        subprocess.call(["pngcrush", "-ow ", filename])
    except FileNotFoundError:
        log.warning("pngcrush not present!")


def censor_username(filename: str) -> None:
    try:
        subprocess.run(
            (
                "convert"
                + " "
                + filename
                + " -fill black"
                + ' -draw "rectangle 7 458 190 474"'
                + " "
                + filename
            ),
            check=True,
            shell=True,
        )
    except FileNotFoundError:
        log.warning("ImageMagick not present!")


def main(region: tuple[int, int, int, int] = vis.CLIENT) -> str:
    """
    Takes a screenshot of the OSRS client window.

    Returns:
        Returns the filepath to the screenshot.
    """
    if DELAY > 0:
        log.info("Waiting %s seconds ...", DELAY)
        time.sleep(DELAY)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = str("osrs_" + timestamp + ".vision.png")
    pag.screenshot(file_name, region=region)

    # Determine if we're logged in or logged out.
    # client_status = vis.orient()[0]
    # log.debug(client_status)
    # needle = vis.Vision(
    #     region=vis.GAME_SCREEN,
    #     needle='./../ocvbot/needles/game-screen/al-kharid/furnace.png',
    #     loop_num=3,
    #     loop_sleep_range=(500, 1000),
    #     conf=0.85,
    # ).find_needle()
    # print(needle)
    # log.debug(needle)

    vis.Vision(
        region=vis.GAME_SCREEN,
        needle='./../ocvbot/needles/game-screen/al-kharid/furnace.png',
        loop_num=3,
        loop_sleep_range=(500, 1000),
        conf=0.85,
    ).click_needle()

    # if client_status == "logged_in":
    #     # If the client is logged in, censor the player's username
    #     #   by drawing a black rectangle over it with ImageMagick.
    #     censor_username(file_name)
    pngcrush(file_name)
    # Move the file into the current dir.
    new_file_name = current_dir + "/" + file_name
    os.rename(file_name, new_file_name)
    return new_file_name


if __name__ == "__main__":
    main()
