import os
import sys
import math
import operator
import re
from collections import *
from functools import *
from itertools import *
from os.path import exists
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import *
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = True

STRIP = True
SPLIT_LINES = False
SPLIT_CHAR = ''
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022


class BlockedException(Exception):
    pass


State = namedtuple("State", "i h", defaults=[0, 0])


class Solution:
    def __init__(self, data):
        if data and STRIP and type(data) == str:
            data = data.strip()
        if data and SPLIT_LINES and type(data) == str:
            data = data.splitlines()
        if data and SPLIT_CHAR is not None:
            if SPLIT_CHAR == '':
                data = [list(row) for row in data] if SPLIT_LINES else list(data)
            else:
                data = [row.split(SPLIT_CHAR) for row in data] if SPLIT_LINES else data.split(SPLIT_CHAR)
        self.data = data

    def first_part(self):
        result = 0
        print(self.data)

        return result

    '''
    Second approach:
    just treat each row and shape as bitmask number
    
    empty row
    0000000 = 0
    
    complete row
    1111111 = 127
    
    sqaure at start position
    0011000 = 24
    0011000 = 24
    
    ...
    
    6318421
    426
    '''

    def dump(self, field, height=0):
        if height == 0:
            height = field.index(0)
        for y in reversed(range(height)):
            print(f"{y + 1:3} " + f"|{field[y]:07b}|".replace("0", ".").replace("1", "#"))
        print("    +-------+\n")

    def first_part(self):
        shapes = (
            (0b0011110,),  # dash
            (0b0001000,
             0b0011100,
             0b0001000,),  # diamond
            (0b0011100,
             0b0000100,
             0b0000100,),  # hook (note the reverse order from bottom to top)
            (0b0010000,
             0b0010000,
             0b0010000,
             0b0010000,),  # pipe
            (0b0011000,
             0b0011000,)  # square
        )
        field = [0] * 10_000_000
        height = 0
        additional_height = 0
        ptr = 0

        seen = {}

        i = 0
        COUNT = 1_000_000_000_000 if PART2 else 2022
        while i < COUNT:
            # if i in (16, 51):
            #     self.dump(field)

            if height > 0:
                key = (i % len(shapes), ptr % len(self.data), field[height - 1])
                if key in seen:
                    state = seen[key]
                    d = i - state.i
                    print(f"{i}: already seen at {state} with current height {height}... {d} steps brought {height - state.h} height")

                    steps = math.floor((COUNT - i) / d)
                    print(steps)

                    i = i + (steps * d)
                    additional_height += steps * (height - state.h)

                    # while i + d < COUNT:
                    #     i = i + d
                    #     additional_height += (height - state.h)
                    seen.clear()
                    print(f"fast forward to {i} with additional height {additional_height} :-D")
                    new_key = (i % len(shapes), ptr % len(self.data), field[height - 1])
                    print(new_key)
                else:
                    # if i in (16, 17, 51, 52):
                    #     print(i, i % len(shapes), ptr % len(self.data), field[height - 1])
                    seen[key] = State(i, height)

            sprite = list(shapes[i % len(shapes)])
            pos = height + 3

            while True:
                direction = self.data[ptr % len(self.data)]
                ptr += 1
                # try to move left/right
                new_sprite = []
                try:
                    for l, row in enumerate(sprite):
                        if (direction == "<" and row & 64) or (direction == ">" and row & 1):  # max left or max right
                            raise BlockedException()
                        row = row << 1 if direction == "<" else row >> 1
                        if field[pos + l] & row:
                            raise BlockedException()
                        new_sprite.append(row)
                    sprite = new_sprite  # moved all rows.. replace sprite
                except BlockedException:
                    pass  # not moved.. keep sprite unchanged

                # try to move down
                try:
                    for l, row in enumerate(sprite):
                        if pos - 1 < 0 or field[pos - 1 + l] & row:
                            raise BlockedException()
                    pos -= 1
                except BlockedException:
                    # come to rest at pos
                    for l, row in enumerate(sprite):
                        field[pos + l] = field[pos + l] | row
                    height = max(height, pos + len(sprite))  # update height

                    break

            i += 1  # next loop
            # self.dump(field)

        return height + additional_height

    def second_part(self):
        return self.first_part()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DATA_URL = f"https://adventofcode.com/{YEAR}/day/{int(script)}/input"

    if not DATA:
        file_name = f"{script}-dev{DEV if type(DEV) != bool else ''}.txt" if DEV else f"{script}.txt"
        if exists(file_name):
            with open(file_name) as f:
                DATA = f.read()
        elif AOC_SESSION and DATA_URL:
            DATA = requests.get(DATA_URL, headers={'Cookie': f"session={AOC_SESSION}"}).text
            with open(file_name, "w") as f:
                f.write(DATA)

    print(f"DAY {int(script)}")
    s = Solution(DATA)
    print("RESULT", s.first_part() if not PART2 else s.second_part())
