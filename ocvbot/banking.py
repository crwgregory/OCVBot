# coding=UTF-8
"""
Functions for interacting with the banking window.

Used for opening the bank, withdrawing items, and depositing items.

"""
import logging as log

from ocvbot import misc
from ocvbot import startup as start
from ocvbot import vision as vis


def bank_settings_check(setting: str, value: str) -> bool:
    """
    Checks for specific bank window configuration settings.
    Currently only the `quantity` setting is supported.

    Args:
        setting (str): The setting you wish to configure.
            quantity = Sets the value of the `quantity` setting. Available values
                       are `1`, `5`, `10`, and `all`.
        value (str): The value you wish the setting to have.

    Examples:
        bank_settings_check("quantity", "all")

    Returns:
        Returns True if the value was successfully set or was already set.
        Returns False otherwise.

    """
    log.debug("Checking if bank setting %s is set to %s", setting, value)

    # Check if the setting is already at the desired value.
    value_already_set = vis.Vision(
        region=vis.game_screen,
        needle="./needles/bank/settings/" + setting + "/" + value + "-set.png",
        loop_num=1,
    ).wait_for_needle()
    if value_already_set is True:
        log.debug("Bank setting %s is already set to %s", setting, value)
        return True

    # If not, try to bring the setting to the desired value.
    for _ in range(1, 5):
        vis.Vision(
            region=vis.game_screen,
            needle="./needles/bank/settings/"
            + setting
            + "/"
            + value
            + "-unset.png",
            loop_num=1,
        ).click_needle(move_away=True)

        value_set = vis.Vision(
            region=vis.game_screen,
            needle="./needles/bank/settings/"
            + setting
            + "/"
            + value
            + "-set.png",
            loop_num=5,
        ).wait_for_needle()
        if value_set is True:
            log.info("Bank setting %s has been set to %s", setting, value)
            return True
    log.warning("Bank setting %s was unable to be set to %s!", setting, value)
    return False


def open_bank(direction) -> bool:
    """
    Opens the bank, assuming the player is within 2 tiles of the booth.

    Args:
        direction (str): The direction of the bank booth. Must be `north`,
                         `south`, `east`, or `west`.

    Raises:
        Raises an exception if the bank could not be opened.

    Returns:
        Returns True if bank was opened successfully.

    """
    # Check if bank is already open.
    bank_open = vis.Vision(
        region=vis.game_screen, needle="./needles/buttons/close.png", loop_num=1
    ).wait_for_needle()
    if bank_open is True:
        log.info("Bank already open!")
        return True

    # TODO: Deal with bank PINs.
    log.info("Attempting to open bank.")
    for _ in range(1, 10):
        one_tile = vis.Vision(
            region=vis.game_screen,
            needle="./needles/game-screen/bank/bank-booth-" + direction + "-1-tile.png",
            loop_num=1,
            conf=0.85,
        ).click_needle()

        two_tiles = vis.Vision(
            region=vis.game_screen,
            needle="./needles/game-screen/bank/bank-booth-"
            + direction
            + "-2-tiles.png",
            loop_num=1,
            conf=0.85,
        ).click_needle()

        if one_tile is True or two_tiles is True:
            bank_open = vis.Vision(
                region=vis.game_screen,
                needle="./needles/buttons/close.png",
                loop_num=30,
            ).wait_for_needle()
            if bank_open is True:
                return True
            # else:
            # pin = enter_bank_pin()
            # if pin is True:
            # return True

        misc.sleep_rand(1000, 3000)

    raise Exception("Unable to open bank!")


def enter_bank_pin(pin=tuple(str(start.config["main"]["bank_pin"]))) -> bool:
    """
    Enters the user's bank PIN.

    Args:
        pin (tuple): A 4-tuple of the player's PIN.

    Returns:

    """
    # Confirm that the bank PIN screen is actually present.
    bank_pin_screen = vis.Vision(
        region=vis.game_screen, needle="./needles/.png", loop_num=1
    ).wait_for_needle(get_tuple=False)
    if bank_pin_screen is False:
        return False

    # Loop through the different PIN screens for each of the 4 digits.
    for pin_ordinal in range(1, 4):

        # Wait for the first/second/third/fourth PIN prompt screen to
        #   appear.
        pin_ordinal_prompt = vis.Vision(
            region=vis.game_screen, needle="./needles/" + str(pin_ordinal), loop_num=1
        ).wait_for_needle(get_tuple=False)

        # Enter the first/second/third/fourth digit of the PIN.
        if pin_ordinal_prompt is True:
            # TODO:
            enter_digit = vis.Vision(
                region=vis.game_screen,
                needle="./needles/" + pin[pin_ordinal],
                loop_num=1,
            ).click_needle()
    return True


def withdrawal_item(
    item_bank: str, item_inv: str, conf: float = 0.95, quantity: str = "all"
) -> bool:
    """
    Withdrawals an item from the bank.

    Args:
        item_bank (str): Filepath to an image of the item to withdrawal as it
                         appears in the bank window.
        item_inv (str): Filepath to an image of the item to withdrawal as it
                        appears in the player's inventory.
        conf (float): See the `conf` arg of the vision.Vision object. Default is
                      0.95
        quantity (str): The number of items to withdrawal. Available
                        options are `1`, `5`, `10`, or `all`. Default is `all`.

    Returns:
        Returns True if the item was successfully withdrawn from bank,
        returns False otherwise.

    """
    log.info("Attempting to withdrawal item: %s", item_bank)
    # Ensure the correct quantity is withdrawn.
    bank_settings_check("quantity", quantity)

    # Try multiple times to withdrawal the item.
    for _ in range(1, 3):
        vis.Vision(
            region=vis.bank_items_window, needle=item_bank, loop_num=3, conf=conf
        ).click_needle()

        # Wait for item to appear in inventory.
        item_in_inventory = vis.Vision(
            region=vis.inv, needle=item_inv, loop_num=25, conf=conf
        ).wait_for_needle()
        if item_in_inventory is True:
            return True
    log.warning("Could not withdrawal item: %s", item_bank)
    return False


def deposit_inventory():
    """
    Deposits entire inventory into the bank.

    Returns:
        Returns True if the item was successfully deposited into the bank,
        returns False otherwise.

    """
    log.info("Depositing inventory")
    for _ in range(1, 5):
        vis.Vision(
            region=vis.game_screen,
            needle="./needles/bank/deposit-inventory.png",
            loop_num=3,
        ).click_needle()
        misc.sleep_rand(500, 1000)
        misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))

        # Wait until the inventory is empty.
        inv_empty = vis.Vision(
            region=vis.inv,
            needle="./needles/side-stones/inventory/empty-inventory.png",
            loop_sleep_range=(100, 300),
            conf=0.9,
            loop_num=10,
        ).wait_for_needle()
        # Only continue if the inventory is empty.
        if inv_empty is True:
            return True
    log.warning("Unable to deposit inventory!")
    return False


def deposit_item(
    item_bank: str,
    item_inv: str,
    conf: float = 0.95,
) -> bool:
    """
    Deposits an item into the bank.

    Args:
        item_bank (str): Filepath to an image of the item to deposit as it
                         appears in the bank window.
        item_inv (str): Filepath to an image of the item to deposit as it
                        appears in the player's inventory.
        conf (float): See the `conf` arg of the vision.Vision object. Default is
                      0.95
        quantity (str): The number of items to deposit. Available
                        options are `1`, `5`, `10`, or `all`. Default is `all`.

    Returns:
        Returns True if the item was successfully deposited into the bank,
        returns False otherwise.

    """
    log.info("Attempting to deposit cooked food.")
    for _ in range(1, 5):
        vis.Vision(
            region=vis.game_screen,
            needle="./needles/bank/deposit-inventory.png",
            loop_num=3,
        ).click_needle()
        misc.sleep_rand(500, 1000)
        misc.sleep_rand_roll(chance_range=(10, 20), sleep_range=(100, 10000))
        # Make sure inventory is empty.
        inv_full = vis.Vision(
            region=vis.inv,
            needle=item_inv,
            loop_sleep_range=(100, 300),
            loop_num=3,
            conf=0.8,
        ).wait_for_needle()
        # Only continue if the inventory is empty.
        if inv_full is False:
            break
    if inv_full is True:
        raise Exception("Could not empty inventory!")
    return True
