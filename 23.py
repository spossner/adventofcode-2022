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
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
# '''.....
# ..##.
# ..#..
# .....
# ..##.
# .....'''

AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

CHECK = (((NORTH, NORTH_EAST, NORTH_WEST), NORTH),
         ((SOUTH, SOUTH_EAST, SOUTH_WEST), SOUTH),
         ((WEST, NORTH_WEST, SOUTH_WEST), WEST),
         ((EAST, NORTH_EAST, SOUTH_EAST), EAST))


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

    def dump(self, elves, bounds):
        for y in range(bounds.y, bounds.y + bounds.h):
            for x in range(bounds.x, bounds.x + bounds.w):
                print("#" if Point(x, y) in elves else ".", end="")
            print()
        print()

    def first_part(self):
        result = 0
        bounds = Rect()
        elves = set()
        for y, row in enumerate(self.data):
            for x, v in enumerate(row):
                if v == '#':
                    p = Point(x, y)
                    elves.add(p)
                    bounds.extend(p)

        if DEV:
            print("== Initial State ==")
            self.dump(elves, bounds)

        for round in count() if PART2 else range(10):
            new_state = defaultdict(list)
            for e in elves:
                adjacent_found = False
                desired = None
                for i in range(4):
                    c = CHECK[(round + i) % len(CHECK)]
                    check_found = False
                    for offset in c[0]:
                        if translate(e, offset) in elves:  # found elf in check
                            adjacent_found = True
                            check_found = True
                            break
                    if not desired and not check_found:
                        desired = translate(e, c[1])
                    if desired and adjacent_found:  # found already desired new position and at least one adjacent elf -> break and move the elf
                        break
                new_state[desired if adjacent_found and desired else e].append(e)

            new_elves = set()
            for np, e_list in new_state.items():
                if not np:
                    print("hhhääähh")
                if len(e_list) == 1:
                    new_elves.add(np)  # move to new position
                    bounds.extend(np)
                else:
                    new_elves.update(e_list)  # all eves stay at their position
            if PART2 and elves == new_elves:
                return round + 1
            elves = new_elves
            if DEV:
                print(f"== End of Round {round + 1} ==")
                self.dump(elves, bounds)

        return bounds.w * bounds.h - len(elves)

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
