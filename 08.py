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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, direct_adjacent_iter, DIRECT_ADJACENTS
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

    def check_field(self, x, y, current_max, visible, total):
        found = 0
        v = int(self.data[y][x])
        if v > current_max:
            if (not visible[y][x]):
                visible[y][x] = True
                found = 1
        return total + found, max(current_max, v)

    def first_part(self):
        w, h = len(self.data[0]), len(self.data)
        total = 0
        visible = [[False for _ in range(w)] for _ in range(h)]

        for x in range(w):
            # VON OBEN
            current_max = -1
            for y in range(0, h):
                total, current_max = self.check_field(x, y, current_max, visible, total)
                if current_max == 9:
                    break
            # von UNTEN
            current_max = -1
            for y in reversed(range(0, h)):
                total, current_max = self.check_field(x, y, current_max, visible, total)
                if current_max == 9:
                    break

        for y in range(h):
            # VON LINKS
            current_max = -1
            for x in range(0, w):
                total, current_max = self.check_field(x, y, current_max, visible, total)
                if current_max == 9:
                    break
            # von RECHTS
            current_max = -1
            for x in reversed(range(0, w)):
                total, current_max = self.check_field(x, y, current_max, visible, total)
                if current_max == 9:
                    break
        return total

    def second_part(self):
        w, h = len(self.data[0]), len(self.data)
        bounds = Rect(0, 0, w, h)
        scenic_max = 0
        for y in range(1, h - 1):
            for x in range(1, w - 1):
                p = Point(x, y)
                v = int(self.data[y][x])
                scenic = []
                for offset in DIRECT_ADJACENTS:
                    count = 0
                    np = translate(p, offset)
                    while np in bounds:
                        count += 1
                        if int(self.data[np.y][np.x]) < v:
                            np = translate(np, offset)
                        else:
                            break
                    scenic.append(count)
                scenic_max = max(scenic_max, reduce(lambda a, v: a * v, scenic))
        return scenic_max


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = ""
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
    print(s.first_part() if not PART2 else s.second_part())
