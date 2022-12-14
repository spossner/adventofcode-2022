import os
import sys
import math
import operator
import re
from collections import *
from functools import *
from itertools import *
from os.path import *
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import *
from dotenv import load_dotenv

load_dotenv()


class Solution:
    def __init__(self, data, modified=False, dev=False, do_strip=False, do_splitlines=True, split_char=None):
        if data and do_strip and type(data) == str:
            data = data.strip()
        if data and do_splitlines and type(data) == str:
            data = data.splitlines()
        if data and split_char is not None:
            if split_char == '':
                data = [list(row) for row in data] if do_splitlines else list(data)
            else:
                data = [row.split(split_char) for row in data] if do_splitlines else data.split(split_char)
        self.data = data
        self.modified = modified
        self.dev = dev

    def dump_grid(self, grid, bounds):
        for row in grid[bounds.y:bounds.y + bounds.h + 3]:
            print("".join(row[bounds.x - 10:bounds.x + bounds.w + 10]))

    def first_part(self, is_part1=True):
        result = 0
        start = Point(500, 0)
        bounds = Rect(start.x, start.y, 1, 1)
        grid = [["."] * 1_000 for _ in range(500)]
        grid[start.y][start.x] = "+"

        for row in self.data:
            path = get_ints(row)
            pos = None
            for x, y in batched(path, 2):
                next_pos = Point(x, y)
                bounds.extend(next_pos)
                grid[next_pos.y][next_pos.x] = "#"
                if pos:
                    for p in iter_from_to(pos, next_pos):
                        grid[p.y][p.x] = "#"
                pos = next_pos
        if not is_part1:
            grid[bounds.y + bounds.h + 1] = ["#"] * 1_000

        for i in count():
            s = start
            while True:
                if is_part1 and s not in bounds:
                    print(s, bounds)
                    self.dump_grid(grid, bounds)
                    return i
                new_s = None
                for tests in (SOUTH, SOUTH_WEST, SOUTH_EAST):
                    new_pos = translate(s, tests)
                    if grid[new_pos.y][new_pos.x] == ".":
                        new_s = new_pos
                        break
                if new_s is None:
                    grid[s.y][s.x] = "o"
                    bounds.extend(s)
                    if s == start:  # start was filled
                        self.dump_grid(grid, bounds)
                        return sum(map(lambda row: len(list(filter(lambda v: v == "o", row))), grid))

                    break  # sand rest
                s = new_s

        return result

    def second_part(self):
        # 25118 too low :-o
        # for whatever reason the bottom is too far away in test data.. mmhhh
        return self.first_part(False)


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = None
    DATA = None
    AOC_SESSION = os.environ.get('AOC_SESSION')

    DATA_URL = f"https://adventofcode.com/2022/day/{int(script)}/input"

    if not DATA:
        file_name = f"{script}-dev{DEV if type(DEV) != bool else ''}.txt" if DEV else f"{script}.txt"
        if exists(file_name):
            with open(file_name) as f:
                DATA = f.read()
        elif AOC_SESSION and DATA_URL:
            DATA = requests.get(DATA_URL, headers={'Cookie': f"session={AOC_SESSION}"}).text
            with open(file_name, "w") as f:
                f.write(DATA)

    s = Solution(DATA, PART2, DEV, STRIP, SPLIT_LINES, SPLIT_CHAR)
    print("RESULT", s.first_part() if not PART2 else s.second_part())
