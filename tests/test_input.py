import pytest
import pyautogui as pag

from ocvbot import input


move_to_params = (
    (100, 100, 100, -100),
    (200, 200, 100, 100),
    (300, 300, 100, 100),
    (400, 400, 100, 100),
    (500, 5000, 0, 100)
)


#@pytest.mark.parametrize('x,y,xmax,ymax', move_to_params)
#def test_move_to(x, y, xmax, ymax):
    #input.move_to(x, y, xmax, ymax)
    #assert True

def test_click_coord():
    left = 100
    top = 100
    width = 100
    height = 100
    input.Mouse(left, top, width, height).click_coord()