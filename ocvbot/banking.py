# coding=UTF-8
"""
Functions for interacting with the banking window.

Used for:
  - opening the bank
  - closing the bank
  - withdrawing items
  - depositing items

"""
import logging as log

from ocvbot import interface
from ocvbot import misc
from ocvbot import startup as start
from ocvbot import vision as vis

# TODO: Finish enter_bank_pin() function.


# TODO: Rename to "configure_bank_settings"
def bank_settings_check(setting: str, value: str) -> None:
    """
    Ensures specific bank window configuration settings.

    Args:
        setting (str): The setting you wish to configure.
            quantity = Sets the value of the `quantity` setting. Available
                       values are `1`, `5`, `10`, and `all`.
            placeholder = Sets the value of the `placeholder` setting.
                          Available values are `set` and `unset`.
        value (str): The value you wish the setting to have.

    Examples:
        bank_settings_check("quantity", "all")
        bank_settings_check("placeholder", "unset")

    Raises:
        Raises a ValueError if the setting or value is not supported.

        Raises start.BankingError if the setting could not be set.

    """
    if setting == "quantity":
        if value not in ("1", "5", "10", "all", "x"):
            raise ValueError("Unsupported value for quantity setting!")
        setting_unset = f"./needles/bank/settings/{setting}/{value}-unset.png"
        setting_set = f"./needles/bank/settings/{setting}/{value}-set.png"

    elif setting == "placeholder":
        if value == "set":
            setting_unset = "./needles/bank/settings/placeholder/placeholder-unset.png"
            setting_set = "./needles/bank/settings/placeholder/placeholder-set.png"
        elif value == "unset":
            setting_unset = "./needles/bank/settings/placeholder/placeholder-set.png"
            setting_set = "./needles/bank/settings/placeholder/placeholder-unset.png"
        else:
            raise ValueError("Unsupported value for placeholder setting!")

    else:
        raise ValueError("Unsupported bank setting!")

    try:
        log.debug("Checking if bank setting %s is set to %s", setting, value)
        interface.enable_button(
            button_disabled=setting_unset,
            button_disabled_region=vis.GAME_SCREEN,
            button_enabled=setting_set,
            button_enabled_region=vis.GAME_SCREEN,
        )
    except start.NeedleError as error:
        raise start.BankingError("Could not set bank setting!") from error


def close_bank():
    """
    Closes the bank window if it is open.

    Raises:
        Raises start.BankingError if the bank window could not be closed.

    Returns:
        Returns once the bank window has been closed, or is already closed.

    """
    # Must use invert_match here because we want to check for the absence of
    #   the `close` button.
    try:
        interface.enable_button(
            button_disabled="./needles/buttons/close.png",
            button_disabled_region=vis.GAME_SCREEN,
            button_enabled="./needles/buttons/close.png",
            button_enabled_region=vis.GAME_SCREEN,
            invert_match=True,
        )
        return
    except start.NeedleError as error:
        raise start.BankingError("Could not close bank window!") from error


def deposit_inventory() -> None:
    """
    Deposits entire inventory into the bank. Assumes the bank window is
    open and the "deposit inventory" button is visible.

    Raises:
        Raises start.BankingError if the inventory could not be deposited.

    Returns:
        Returns once the inventory has been deposited, or if the inventory is
        already empty.
    """
    try:
        interface.enable_button(
            button_disabled="./needles/bank/deposit-inventory.png",
            button_disabled_region=vis.GAME_SCREEN,
            button_enabled="./needles/side-stones/inventory/empty-inventory.png",
            button_enabled_region=vis.INV,
        )
        return
    except start.NeedleError as error:
        raise start.BankingError("Could not deposit inventory!") from error


def deposit_item(item, quantity) -> None:
    """
    Deposits the given item into the bank. Assumes the bank window is
    open.

    Args:
        item (str): Filepath to an image of the item to deposit as it
                    appears in the player's inventory.
        quantity (str): Quantity of the item to deposit. Available
                        values are `1`, `5`, `10`, and `all`.

    Returns:
        Returns when item was successfully deposited into bank, or there were
        no items of that type in the inventory to begin with.

    Raises:
        Raises a ValueError if `quantity` doesn't match the available values.

        Raises start.BankingError if too many items were deposited by mistake.
        Raises start.BankingError if the item could not be deposited.

    """
    # Count the initial number of the given item in the inventory.
    initial_number_of_items = vis.Vision(region=vis.INV, needle=item).count_needles()
    # If there are no matching items in the inventory to begin with, return.
    if initial_number_of_items == 0:
        log.debug("No items of type %s to deposit", item)
        return

    # Determine the number of of items that should be removed from the inventory.
    if quantity == "1":
        items_to_deposit = 1
    elif quantity == "5":
        items_to_deposit = 5
    elif quantity == "10":
        items_to_deposit = 10
    elif quantity == "all":
        items_to_deposit = initial_number_of_items
    else:
        raise ValueError("Unsupported value for quantity argument!")
    desired_number_of_items = initial_number_of_items - items_to_deposit

    log.info("Attempting to deposit %s of item %s", quantity, item)

    # Make sure the correct quantity is deposited.
    bank_settings_check("quantity", str(quantity))

    # Try clicking on the item multiple times.
    for _ in range(5):

        try:
            vis.Vision(
                region=vis.INV,
                needle=item,
                loop_num=3,
            ).click_needle(sleep_range=(0, 100, 0, 100), move_away=True)
        except start.NeedleError:
            pass

        # Loop and wait until the item has been deposited.
        for _ in range(10):
            misc.sleep_rand(200, 700)
            final_number_of_items = vis.Vision(
                region=vis.INV, needle=item
            ).count_needles()
            if desired_number_of_items == final_number_of_items:
                log.debug("Deposited item %s", item)
                return
            if desired_number_of_items > final_number_of_items:
                raise start.BankingError("Deposited too many items!")

    raise start.BankingError("Could not deposit items!")


def enter_bank_pin(pin=(start.config["main"]["bank_pin"])) -> bool:
    """
    Enters the user's bank PIN. Assumes the bank window is open.

    Args:
        pin (tuple): A 4-tuple of the player's PIN.

    Examples:
        enter_bank_pin(pin=1234)

    Returns:
        Returns True if the bank PIN was successfully entered or PIN
        window could not be found, returns False if PIN was incorrect

    """
    pin = tuple(str(pin))
    # Confirm that the bank PIN screen is actually present.
    try:
        bank_pin_screen = vis.Vision(
            region=vis.GAME_SCREEN, needle="./needles/.png", loop_num=1
        ).wait_for_needle()
    except start.NeedleError:
        return True

    # Loop through the different PIN screens for each of the 4 digits.
    for pin_ordinal in range(1, 4):

        # Wait for the first/second/third/fourth PIN prompt screen to
        #   appear.
        pin_ordinal_prompt = vis.Vision(
            region=vis.GAME_SCREEN, needle="./needles/" + str(pin_ordinal), loop_num=1
        ).wait_for_needle()

        # Enter the first/second/third/fourth digit of the PIN.
        if pin_ordinal_prompt is True:
            enter_digit = vis.Vision(
                region=vis.GAME_SCREEN,
                needle="./needles/" + pin[pin_ordinal],
                loop_num=1,
            ).click_needle()
    return True


# TODO: Instead of using direction, use a list of supported banks, since some
#   bank booths look different from others.
def open_bank(direction) -> None:
    """
    Opens the bank. Assumes the player is within 2 tiles of a bank boot and
    the client is fully zoomed in.

    Args:
        direction (str): The cardinal direction of the bank booth relative to
                         the player.  Must be `north`, `south`, `east`, or
                         `west`.

    Examples:
        open_bank("west")

    Returns:
        Returns if bank was opened successfully or is already open.

    Raises:
        Raises a ValueError if an invalid direction is given.

        Raises start.BankingError if the bank could not be opened.

    """
    if direction not in ("north", "south", "east", "west"):
        raise ValueError("Must provide a cardinal direction to open bank!")

    log.info("Attempting to open bank window.")

    tile_ranges = [
        f"./needles/game-screen/bank/bank-booth-{direction}-1-tile.png",
        f"./needles/game-screen/bank/bank-booth-{direction}-2-tiles.png",
    ]
    # Try multiple times to open the bank window, while looping through 1-tile
    #   and 2-tile distance versions of the needle.
    for _ in range(5):
        for tile in tile_ranges:
            try:
                interface.enable_button(
                    button_disabled=tile,
                    button_disabled_region=vis.GAME_SCREEN,
                    button_enabled="./needles/buttons/close.png",
                    button_enabled_region=vis.GAME_SCREEN,
                    loop_num=3,
                    conf=0.85,
                )
                return
            except start.NeedleError:
                pass

    raise start.BankingError("Unable to open bank window!")


# TODO: Use code from deposit_item() to check that correct quantity is withdrawn.
def withdrawal_item(
    item_bank: str, item_inv: str, conf: float = 0.95, quantity: str = "all"
) -> None:
    """
    Withdrawals an item from the bank. Assumes the bank window is open and
    the item to withdrawal is visible. Does NOT check if the correct
    quantity is withdrawn.

    Args:
        item_bank (str): Filepath to an image of the item to withdrawal as it
                         appears in the bank window.
        item_inv (str): Filepath to an image of the item to withdrawal as it
                        appears in the player's inventory.
        conf (float): See the `conf` arg of the vision.Vision class. Default is
                      0.95
        quantity (str): The number of items to withdrawal. Available
                        options are `1`, `5`, `10`, or `all`. Default is `all`.

    Examples:
        withdrawal_item(item_bank="./needles/items/raw-anchovies-bank.png",
                        item_inv="./needles/items/raw-anchovies.png",
                        conf=0.98)

    Returns:
        Returns if the item was successfully withdrawn from bank,

    Raises:
        Raises start.BankingError if item could not be withdrawn.

    """
    log.info("Attempting to withdrawal item: %s", item_bank)
    try:

        # Make sure no placeholders are left behind, as this makes image
        #   matching much more difficult -- placeholders look very similar
        #   to regular "real" items.
        bank_settings_check("placeholder", "unset")

        # Ensure the correct quantity is withdrawn.
        bank_settings_check("quantity", str(quantity))

        interface.enable_button(
            button_disabled=item_bank,
            button_disabled_region=vis.BANK_ITEMS_WINDOW,
            button_enabled=item_inv,
            button_enabled_region=vis.INV,
            loop_num=10,
            conf=conf,
        )

    except Exception as error:
        raise start.BankingError("Could not withdrawal item!") from error
