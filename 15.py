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

DEV = True
PART2 = True

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None


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

    def first_part(self):
        beacons = set()
        sensors = set()
        bounds = Rect()
        max_bounds = Rect()
        left_most = defaultdict(list)
        for row in self.data:
            sx, sy, bx, by = get_ints(row)
            s = Point(sx, sy)
            b = Point(bx, by)
            d = manhattan_distance(s, b)
            bounds.extend(s, b)
            max_bounds.extend(s, b, Point(sx - d, sy), Point(sx + d, sy))
            beacons.add(b)
            sensors.add(s)
            left_most[sx - d].append([s, 1, (d << 1) + 1])

        print(bounds, max_bounds, left_most, beacons, sensors)
        no = 10 if DEV else 2_000_000
        max_width = 20 if DEV else 4_000_000
        diamonds = []
        row = defaultdict(int)
        print("scan lines")
        for x in range(max_bounds.x, max_bounds.x + max_bounds.w):
            if x % 100_000 == 0:
                print(".", end="")
            if x in left_most:
                diamonds.extend(left_most[x])

            col_ranges = []

            for d in diamonds:
                s = d[0]
                r = d[1] >> 1
                span = range(s.y - r, s.y + r + 1)
                col_ranges.append(span)
                if not PART2 and no in span:
                    p = Point(x, no)
                    if p not in beacons and p not in sensors:
                        row[x] += 1
                if x < s.x:
                    d[1] += 2
                else:
                    d[1] -= 2
            diamonds = list(filter(lambda d: d[1] > 0, diamonds))

            col_ranges.sort(key=lambda r: r.start)
            large_range = col_ranges[0]
            for r in col_ranges[1:]:
                if r.start <= large_range.stop:
                    large_range = range(large_range.start, max(large_range.stop, r.stop))
            if 0 <= x <= max_width:
                if 0 not in large_range or max_width not in large_range:
                    hole = Point(x, large_range.stop)
                    print(f"\nfound hole at ({hole}:", hole.x * 4_000_000 + hole.y)

        print()
        if not PART2:
            # 4096105 too low
            # 4883971 better after using the max right side as well.. before stopped at right sensor/beacon..?
            return len(row)

    def second_part(self):
        # 12691026767556
        return self.first_part()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

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

    print(f"DAY {int(script)}")
    s = Solution(DATA, PART2, DEV, STRIP, SPLIT_LINES, SPLIT_CHAR)
    print("RESULT", s.first_part() if not PART2 else s.second_part())
