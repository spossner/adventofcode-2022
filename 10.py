import os
import sys
import math
import operator
import re
from collections import deque, defaultdict, namedtuple, Counter
from functools import total_ordering, reduce
from itertools import permutations, zip_longest, count
from os.path import exists
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, fetch
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

    def dump(self, matrix):
        for row in matrix:
            print("".join(row))

    def first_part(self):
        reg = {"x": 1}
        ptr = 0
        blocked = 0
        heap = deque()
        total = 0

        display = [[" " for _ in range(40)] for _ in range(6)]

        for cycle in range(1, 241):
            if blocked == 0 and ptr < len(self.data):
                cmd, arg = fetch(self.data[ptr], 2)
                ptr += 1
                if cmd == "noop":
                    pass
                elif cmd == "addx":
                    blocked = 2
                    heap.append(("x", reg["x"] + int(arg)))
                else:
                    print("UNKNOWN", cmd, arg)

            if (cycle - 20) % 40 == 0:
                total += cycle * reg["x"]
                # print(cycle, reg, blocked, heap, cycle * reg["x"], total)

            pos = cycle - 1
            if abs((pos % 40) - reg["x"]) < 2:
                # print(f"setting {pos}: {int(pos / 40)}, {pos % 40} of {display}")
                display[int(pos / 40)][pos % 40] = "█"

            if blocked > 0:
                blocked -= 1
                if blocked == 0:
                    r, new_value = heap.pop()
                    reg[r] = new_value
        self.dump(display)
        return total

    def second_part(self):
        return self.first_part()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = False

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = ' '
    DATA = None
    #     '''noop
    # addx 3
    # addx -5'''
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
    print(s.first_part() if not PART2 else s.second_part())
