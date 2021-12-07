# coding=utf-8
"""
Module for invoking main bot scripts.

Most main scripts define a preset list of `scenarios`, which the user
must choose from. Each scenario has a predetermined configuration that will
used for training that skill. For example, the `varrock-east-mine` scenario
for the `miner` script is configured to only mine two specific iron rocks
within Varrock East Mine.

See `config.yaml.example` for more info.
See `docs/scenarios/` for the required client configuration settings in
each scenario.

"""
import glob
import logging as log
import os
import pathlib
import random as rand
import sys
import traceback

# Global TODOs:
# TODO: Transition to use proper exceptions rather than checking for a False return value.
# TODO: Use snake_case for all image files and paths.
# TODO: Fix installation method to use `pip install -e .` so we don't need to
#   edit the sys.path variables.

# TODO: See if these statements are really necessary since they're in init.py
# Make sure the program's working directory is the directory in which
#   this file is located.
os.chdir(os.path.dirname(__file__))
# Ensure ocvbot files are added to sys.path.
SCRIPTPATH = str(pathlib.Path(__file__).parent.parent.absolute())
sys.path.insert(1, SCRIPTPATH)

from ocvbot import banking
from ocvbot import behavior
from ocvbot import misc
from ocvbot import skills
from ocvbot import startup as start
from ocvbot import vision as vis


def miner(scenario: str, loops: int = 10000) -> None:
    """
    Script for mining rocks in a handful of locations. Banking support is
    limited.

    Args:
        scenario (str): See the `magic` section of `config.yaml.example` for
                        the available options.
        loops (int): Number of loops to run the given scenario. Changing this
                     is only useful for testing purposes. Default is 10000.

        See `/docs/scenarios/` for the required client
        configuration settings for each scenario.

    Raises:
        Raises a ValueError if an unsupported scenario is passed.

    """
    # TODO: Function is too large. Refactor.
    log.info("Launching miner script with scenario %s.", scenario)
    # Make the path to the rock needles shorter.
    prefix = "./needles/game-screen/" + scenario + "/"
    haystack_map = "./haystacks/" + scenario + ".png"

    # Read the config file to get argument values.
    drop_sapphire_config = start.config["mining"]["drop_sapphire"]
    drop_emerald_config = start.config["mining"]["drop_emerald"]
    drop_ruby_config = start.config["mining"]["drop_ruby"]
    drop_diamond_config = start.config["mining"]["drop_diamond"]
    drop_clue_geode_config = start.config["mining"]["drop_clue_geode"]
    # Determine if the player will be dropping the ore or banking it.
    # This var is forced to True in scenarios where banking is not
    #   supported.
    drop_ore_config = start.config["mining"]["drop_ore"]

    bank_from_mine = None
    mine_from_bank = None

    # CONFIGURE SCENARIO PARAMETERS ---------------------------------------------------------------

    if scenario == "varrock-east-mine":
        ore = "./needles/items/iron-ore.png"
        mining = skills.Mining(
            rocks=[
                (prefix + "north-full2.png", prefix + "north-empty.png"),
                (prefix + "west-full.png", prefix + "west-empty.png"),
            ],
            ore=ore,
            drop_sapphire=drop_sapphire_config,
            drop_emerald=drop_emerald_config,
            drop_ruby=drop_ruby_config,
            drop_diamond=drop_diamond_config,
            drop_clue_geode=drop_clue_geode_config,
        )

        bank_from_mine = [
            ((253, 181), 5, (35, 35), (1, 6)),
            ((112, 158), 5, (20, 20), (1, 6)),
            ((108, 194), 1, (10, 4), (3, 8)),
        ]

        mine_from_bank = [
            ((240, 161), 5, (35, 35), (1, 6)),
            ((262, 365), 5, (25, 25), (1, 6)),
            ((240, 399), 1, (4, 4), (3, 8)),
        ]

    elif scenario == "varrock-east-mine-tin":
        haystack_map = "./haystacks/varrock-east-mine.png"
        ore = "./needles/items/tin-ore.png"
        mining = skills.Mining(
            rocks=[
                (prefix + "west-tin-full.png", prefix + "west-tin-empty.png"),
                (prefix + "north-tin-full.png", prefix + "north-tin-empty.png"),
            ],
            ore=ore,
            drop_sapphire=drop_sapphire_config,
            drop_emerald=drop_emerald_config,
            drop_ruby=drop_ruby_config,
            drop_diamond=drop_diamond_config,
            drop_clue_geode=drop_clue_geode_config,
            mine_rock_empty_needle_recheck=1,
            mine_rock_loop=3,
            raise_on_rock_mine_timeout=False,
        )
        bank_from_mine = [
            ((253, 181), 5, (35, 35), (1, 6)),
            ((112, 150), 5, (20, 20), (1, 6)),
            ((108, 194), 1, (10, 4), (3, 8)),
        ]

        mine_from_bank = [
            ((240, 161), 5, (35, 35), (1, 6)),
            ((262, 365), 5, (25, 25), (1, 6)),
            ((224, 419), 1, (4, 4), (3, 8)),
        ]

    elif scenario == "varrock-east-mine-copper":
        haystack_map = "./haystacks/varrock-east-mine.png"
        ore = "./needles/items/copper-ore.png"
        mining = skills.Mining(
            rocks=[
                (prefix + "south-copper-full.png", prefix + "south-copper-empty.png"),
                (prefix + "east-copper-full.png", prefix + "east-copper-empty.png"),
            ],
            ore=ore,
            drop_sapphire=drop_sapphire_config,
            drop_emerald=drop_emerald_config,
            drop_ruby=drop_ruby_config,
            drop_diamond=drop_diamond_config,
            drop_clue_geode=drop_clue_geode_config,
            mine_rock_empty_needle_recheck=1,
            mine_rock_loop=3,
            raise_on_rock_mine_timeout=False,
        )
        bank_from_mine = [
            ((253, 181), 5, (35, 35), (1, 6)),
            ((112, 158), 5, (20, 20), (1, 6)),
            ((108, 194), 1, (10, 4), (3, 8)),
        ]

        mine_from_bank = [
            ((240, 161), 5, (35, 35), (1, 6)),
            ((262, 365), 5, (25, 25), (1, 6)),
            ((237, 411), 1, (4, 4), (3, 8)),
        ]

    elif scenario == "lumbridge-mine":
        drop_ore_config = True  # Banking not supported.
        ore = "./needles/items/copper-ore.png"
        mining = skills.Mining(
            rocks=[
                (prefix + "east-full.png", prefix + "east-empty.png"),
                (prefix + "south-full.png", prefix + "south-empty.png"),
            ],
            ore=ore,
            drop_sapphire=drop_sapphire_config,
            drop_emerald=drop_emerald_config,
            drop_ruby=drop_ruby_config,
            drop_diamond=drop_diamond_config,
            drop_clue_geode=drop_clue_geode_config,
        )

    elif scenario == "camdozaal-mine":
        drop_ore_config = True  # Banking not supported.
        ore = "./needles/items/barronite-deposit.png"
        mining = skills.Mining(
            rocks=[
                (prefix + "east-full.png", prefix + "east-empty.png"),
                (prefix + "west-full.png", prefix + "west-empty.png"),
            ],
            ore=ore,
            drop_sapphire=drop_sapphire_config,
            drop_emerald=drop_emerald_config,
            drop_ruby=drop_ruby_config,
            drop_diamond=drop_diamond_config,
            drop_clue_geode=drop_clue_geode_config,
        )
    else:
        raise ValueError("Scenario not supported!")

    # MAIN FUNCTION LOOP --------------------------------------------------------------------------
    for _ in range(loops):
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
        except (Exception, start.InefficientUseOfInventory) as error:
            log.error(error)
            behavior.logout()


def alchemist(alch_item_type, loops: int = 10000) -> None:
    """
    Script for training high alchemy.

    Args:
        alch_item_type (str): See the `magic` section of `config.yaml.example`
                              for the available options.
        loops (int): Number of loops to run the given scenario. Changing this
                     is only useful for testing purposes. Default is 10000.

    """
    spell = "./needles/side-stones/spellbook/high-alchemy.png"
    if alch_item_type == "bank-note":
        target = "./needles/items/bank-note.png"
    else:
        target = f"./needles/items/{alch_item_type}.png"

    behavior.open_side_stone("spellbook")
    for _ in range(loops):
        try:
            skills.Magic(
                spell=spell,
                target=target,
                inventory=True,
                conf=0.5,
                region=vis.INV_LEFT_HALF,
                move_duration_range=(0, 200),
            ).cast_spell()
            misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))

            # Every once in a while, print the amount of time the bot has been running.
            # Also roll for randomized logout.
            if rand.randint(1, 50) == 50:
                misc.session_duration(human_readable=True)
                behavior.logout_break_range()

        # This will occur when we're out of runes or out of items to alch.
        except start.NeedleError as error:
            raise error


def spellcaster(scenario: str, loops: int = 10000) -> None:
    """
    Script for training magic with combat spells.

    Args:
        scenario (str): See the `magic` section of `config.yaml.example` for
                        the available options.
        loops (int): Number of loops to run the given scenario. Changing this
                     is only useful for testing purposes. Default is 10000.

        See `/docs/scenarios/` for the required client
        configuration settings for each scenario.

    Raises:
        Raises a ValueError if an unsupported scenario is passed.

    """
    log.info("Launching spellcaster script with scenario %s.", scenario)

    if scenario == "curse-varrock-castle":
        spell = "./needles/side-stones/spellbook/curse.png"
        target = "./needles/game-screen/varrock/monk-of-zamorak.png"
        haystack_map = "./haystacks/varrock-castle.png"
        behavior.travel([((75, 128), 1, (4, 4), (5, 10))], haystack_map)
    else:
        raise ValueError("Scenario not supported!")

    behavior.open_side_stone("spellbook")
    for _ in range(loops):
        skills.Magic(
            spell=spell,
            target=target,
            conf=0.75,
            region=vis.GAME_SCREEN,
        ).cast_spell()
        misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))

        # Every once in a while, print the amount of time the bot has been running.
        # Also roll for randomized logout.
        if rand.randint(1, 50) == 50:
            misc.session_duration(human_readable=True)
            behavior.logout_break_range()

def smelting(bar_type: str, loops: int = 10000) -> None:
    
    bank_coords = [((88, 207), 3, (3, 3), (3, 9))]
    smelter_coords = [((112, 120), 1, (2, 2), (8, 12))]
    smelter_source = "./needles/game-screen/al-kharid-smelt/furnace.png"
    map = './haystacks/al-kharid.png'

    smelter = skills.Smelting(
        smelter_needle=smelter_source,
        bar_type=bar_type,
    )

    banking.open_bank("west")
    for _ in range(loops):
        # sense withdrawing ore is dependant on the type of smelting, I put it into the skill class 
        # lil' bit of an 'anti-pattern' from other scripts. Should I refactor?
        smelter.withdraw_ore() 

        misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))
        behavior.travel(smelter_coords, map)
        
        smelter.smelt()

        misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))
        behavior.travel(bank_coords, map)
        banking.open_bank("west")
        banking.deposit_inventory()

        behavior.logout_break_range()
        misc.session_duration(human_readable=True)


def chef(item: str, location: str, loops: int = 10000) -> None:
    """
    Cooks a given item at a given location.

    Args:
        item (str): See the `cooking` section of `config.yaml.example` for
                    the available options.
        location (str): See the `cooking` section of `config.yaml.example` for
                       the available options.
        loops (int): Number of loops to run the given scenario. Changing this
                     is only useful for testing purposes. Default is 10000.

    Raises:
        Raises a ValueError if an unsupported location is passed.


    """
    if location == "al-kharid":
        bank_coords = [((91, 207), 3, (4, 7), (3, 9))]
        range_coords = [((103, 148), 1, (5, 5), (8, 12))]
        heat_source = "./needles/game-screen/al-kharid/range.png"
        # Assumes starting location is the bank.
        banking.open_bank("west")
    else:
        raise ValueError("Unsupported value for location!")

    log.info("Launching chef script with item %s and location %s.", item, location)
    # Must have staff of water equipped!
    # TODO: In Al Kharid, deal with the door to the house with the range
    #   possibly being shut.
    haystack_map = f"./haystacks/{location}.png"
    item_inv = f"./needles/items/{item}.png"
    item_bank = f"./needles/items/{item}-bank.png"

    for _ in range(loops):
        try:
            # Conf is higher than default because raw food looks very
            #   similar to cooked food.
            banking.withdrawal_item(item_bank=item_bank, item_inv=item_inv, conf=0.99)
            log.info("Withdrawing raw food.")
            misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))
            # Go to range.
            behavior.travel(range_coords, haystack_map)
            # Cook food.
            skills.Cooking(item_inv, item_bank, heat_source).cook_item()
            # Go back to bank and deposit cooked food.
            behavior.travel(bank_coords, haystack_map)
            banking.open_bank("west")
            misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))
            banking.deposit_inventory()
            # Roll for randomized logout.
            behavior.logout_break_range()
            misc.session_duration(human_readable=True)

        except Exception:
            print(traceback.format_exc())
            behavior.logout()
            return
    return


def smith(bar: str, item: str, location: str, loops: int = 10000):
    """
    Smiths bars at an anvil.

    Args:
        bar (str): See the `smithing` section of `config.yaml.example` for
                   the available options.
        location (str): See the `smithing` section of `config.yaml.example` for
                       the available options.
        loops (int): Number of loops to run the given scenario. Changing this
                     is only useful for testing purposes. Default is 10000.

    Raises:
        Raises a ValueError if an unsupported location is passed.

    """
    if location == "varrock":
        haystack_map = "./haystacks/varrock-west-bank.png"
        bank_coords = [((88, 93), 1, (4, 5), (7, 9))]
        anvil_coords = [((97, 130), 1, (3, 3), (7, 9))]
        anvil = "./needles/game-screen/varrock/anvil.png"
    else:
        raise ValueError("Unsupported value for location!")

    # We can use banked versions of the smith item because the smithing menu
    #   has the same background as the bank menu.
    bar = f"./needles/items/{bar}.png"
    item = f"./needles/items/{item}-bank.png"

    # Determine how many bars are needed to smith the given item.
    if "platebody" in item:
        bars_required = 5
    elif "scimitar" in item:
        bars_required = 2
    elif "axe" in item or "warhammer" in item:
        bars_required = 3
    else:
        raise Exception("Unsupported value of item!")

    behavior.open_side_stone("inventory")
    for _ in range(loops):
        if location == "varrock":
            banking.open_bank("east")
        banking.deposit_inventory()
        misc.sleep_rand_roll(chance_range=(20, 30))

        # Ensure we have bars in the bank.
        have_bars = vis.Vision(
            region=vis.GAME_SCREEN, needle=bar, conf=0.9999
        ).find_needle()
        # Stop script if we don't
        if have_bars is False:
            log.info("Out of bars, stopping script.")
            return

        banking.withdrawal_item(
            item_bank="./needles/items/hammer-bank.png",
            item_inv="./needles/items/hammer.png",
            quantity="1",
            conf=0.9,
        )
        misc.sleep_rand_roll(chance_range=(20, 30))
        banking.withdrawal_item(item_bank=bar, item_inv=bar, conf=0.99)
        misc.sleep_rand_roll(chance_range=(20, 30))

        # Check if we withdrew a full inventory of bars. Stop script if we didn't
        bars_in_inventory = vis.Vision(region=vis.INV, needle=bar).count_needles()
        if bars_in_inventory != 27:
            log.warning("Out of bars, stopping script.")
            return

        behavior.travel(anvil_coords, haystack_map)
        skills.Smithing(
            item_in_menu=item,
            bar_type=bar,
            bars_required=bars_required,
            anvil=anvil,
        ).smith_items()
        misc.sleep_rand_roll(chance_range=(20, 30))
        behavior.travel(bank_coords, haystack_map)
        misc.session_duration(human_readable=True)
        # Roll for randomized logout.
        behavior.logout_break_range()
        misc.sleep_rand_roll(chance_range=(20, 30))


def test():
    banking.deposit_inventory()


def cleanup():
    """
    Cleans up leftover screenshots created by PyAutoGUI.
    """
    glob_string = ".screenshot2*[0-9][0-9][0-9][0-9][0-9][0-9].png"
    for filepath in glob.glob(glob_string):
        os.remove(filepath)


script = start.config["main"]["script"]


def main():
    """
    Calls the main botting script defined in the config file.

    """
    cleanup()
    vis.init()

    if script == "mining":
        miner(start.config[script]["location"])

    elif script == "magic":
        if start.config[script]["scenario"] == "high-alchemy":
            alchemist(start.config[script]["alch_item_type"])
        else:
            spellcaster(start.config[script]["scenario"])

    elif script == "cooking":
        chef(
            item=start.config[script]["item"],
            location=start.config[script]["location"],
        )

    elif script == "smithing":
        smith(
            bar=start.config[script]["bar"],
            item=start.config[script]["item"],
            location=start.config[script]["location"],
        )

    elif script == "smelting":
        smelting(
            bar_type=start.config[script]["bar"],
        )

    elif script == "test":
        test()

    else:
        log.critical("Unknown value provided for 'script' key in config file!")
        raise RuntimeError("Unknown value provided for 'script' key in config file!")

    cleanup()
    sys.exit(0)


if __name__ == "__main__":
    main()
