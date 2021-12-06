# coding=UTF-8
"""
Miscellaneous functions, mostly related to calculating time periods.

"""
import datetime
import logging as log
import random as rand
import time

from ocvbot import startup as start


def rand_seconds(min_seconds: int = 0, max_seconds: int = 100) -> float:
    """
    Gets a random integer between two values. Input arguments are in
    miliseconds but output is in seconds. For example, if this function
    generates a random value of 391, it will return a value of 0.391.

    Args:
        min_seconds (int): The minimum number of miliseconds, default is 0.
        max_seconds (int): The maximum number of miliseconds, default is 100.

    Returns:
        Returns a float.

    """
    randval = rand.randint(min_seconds, max_seconds)
    randval = float(randval / 1000)
    # log.debug('Got random value of %s.', randval)
    return randval


def sleep_rand(sleep_min: int = 0, sleep_max: int = 100) -> bool:
    """
    Does nothing for a random period of time. Input arguments are in
    miliseconds.

    Args:
        sleep_min (int): The minimum number of miliseconds to wait, default
                         is 0.
        sleep_max (int): The maximum number of miliseconds to wait, default
                         is 100.

    """
    sleeptime = rand_seconds(min_seconds=sleep_min, max_seconds=sleep_max)
    log.debug('Sleeping for %s seconds.', sleeptime)
    time.sleep(sleeptime)
    return True


def session_duration(human_readable: bool = False) -> int:
    """
    Determines how many seconds the current session has been running.
    This timer is reset when the bot logs in or when the bot restarts.

    Args:
        human_readable (bool): Whether to return the number of seconds
                               the bot has been running, or the amount
                               of time in a HH:MM:SS format, default is
                               false.

    Returns:
          Returns an int containing the number of seconds the bot has
          been running since its last logon.

    """
    current_time = time.time()
    # Get elapsed time by subtracting start time from current time.
    elapsed_time_seconds = round(current_time - start.start_time)

    if human_readable is False:
        return elapsed_time_seconds
    elapsed_time_human_readable = datetime.timedelta(seconds=elapsed_time_seconds)
    log.info("Bot has been running for %s (H:MM:SS)", elapsed_time_human_readable)
    return elapsed_time_human_readable


def sleep_rand_roll(
    chance_range: tuple[int, int] = (10, 20),
    sleep_range: tuple[int, int] = (10000, 60000),
    second_chance_range: tuple[int, int] = (10, 20),
) -> bool:
    """
    Roll for a chance to do nothing for the specified period of time.

    Args:
        chance_range (tuple): The minimum and maximum number that must be
                              rolled for the sleep to trigger. For example,
                              if chance_range is (20, 25), then a random
                              number between 20 and 25 will be chosen as
                              the number that must be rolled for the
                              sleep to trigger, default is (10, 20).
        sleep_range (tuple): The minimum and maximum number of miliseconds
                             to wait if the sleep triggers, default is
                             (10000, 60000).
        second_chance_range (tuple): Same as chance_range, except this is
                                     a second roll for an additional sleep
                                     after the initial sleep, if it is
                                     triggered.

    """

    if start.config["main"]["random_waits"] is False:
        return True

    chance = rand.randint(chance_range[0], chance_range[1])
    roll = rand.randint(1, chance)
    if roll == chance:
        log.debug("Random wait called.")
        sleeptime = rand_seconds(sleep_range[0], sleep_range[1])
        log.info("Sleeping for %s seconds...", round(sleeptime, 1))
        time.sleep(sleeptime)

        second_chance = rand.randint(second_chance_range[0], second_chance_range[1])
        second_roll = rand.randint(1, second_chance)
        if second_roll == second_chance:
            log.info("Additional random wait called.")
            sleeptime = rand_seconds(sleep_range[0], sleep_range[1])
            log.info("Sleeping for %s seconds...", round(sleeptime, 1))
            time.sleep(sleeptime)
    return True
