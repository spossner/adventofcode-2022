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
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022


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
        grid = set()
        for row in self.data:
            x, y, z = get_ints(row)
            p = Point3d(x, y, z)
            grid.add(p)
            sides = 6
            for d in ADJACENTS_3D:
                np = translate(p, d)
                if np in grid:
                    sides -= 2  # my side and the side i am covering now
            result += sides  # may be negative

        return result

    def second_part(self):
        grid = set()
        c1 = None
        c2 = None
        for row in self.data:
            x, y, z = get_ints(row)
            p = Point3d(x, y, z)
            grid.add(p)
            c1 = Point3d(min(c1.x, p.x), min(c1.y, p.y), min(c1.z, p.z)) if c1 else p
            c2 = Point3d(max(c2.x, p.x), max(c2.y, p.y), max(c2.z, p.z)) if c2 else p

        # c1 to c2 is transitive hülle.. grow by one to start 3d flood fill
        c1 = Point3d(c1.x - 1, c1.y - 1, c1.z - 1)
        c2 = Point3d(c2.x + 1, c2.y + 1, c2.z + 1)

        queue = deque()
        queue.append(c1)
        seen = set()
        # count the seen surfaces in touched
        touched = 0
        while queue:
            p = queue.popleft()
            if p in seen:  # skip positions already seen
                continue
            seen.add(p)

            for d in ADJACENTS_3D:
                np = translate(p, d)
                if np in grid:  # found surface
                    touched += 1
                elif np.x < c1.x or np.y < c1.y or np.z < c1.z or np.x > c2.x or np.y > c2.y or np.z > c2.z:
                    # print(f"{np} outside of space")
                    pass
                else:
                    queue.append(np)  # found free position.. inspect in a later round
        return touched


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
