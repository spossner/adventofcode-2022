import os
import sys
import math
import operator
import re
import time
from collections import deque, defaultdict, namedtuple, Counter
from functools import total_ordering, reduce
from itertools import permutations, zip_longest, count
from os.path import exists
import bisect

import requests
import networkx as nx
import numpy as np
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate
from dotenv import load_dotenv

load_dotenv()


class SlidingWindow:
    def __init__(self, arr):
        self.window = defaultdict(int)
        self.length = 0
        for v in arr:
            self.add(v)

    def add(self, i):
        self.window[i] += 1
        if self.window[i] == 1:
            self.length += 1

    def delete(self, i):
        self.window[i] -= 1
        if self.window[i] == 0:
            self.length -= 1

    def __len__(self):
        return self.length

    def __str__(self):
        return str(self.window)


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
        window_size = 14 if PART2 else 4
        window = SlidingWindow(self.data[0:window_size])
        for i in range(window_size, len(self.data)):
            if len(window) == window_size:
                return i
            window.delete(self.data[i - window_size])
            window.add(self.data[i])
        return -1

    def second_part(self):
        return self.first_part()


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = False
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
    start = time.time()
    print(s.first_part() if not PART2 else s.second_part())
    end = time.time()
    print(f"took {end - start} s")
