import os


def get_board_list():
    loc = os.path.dirname(__file__)
    loc = os.path.join(loc, "board_list.csv")
    with open(loc) as fp:
        boards = fp.readlines()
        boards = [b.replace("\n", "") for b in boards]
    return boards
