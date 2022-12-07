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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate
from dotenv import load_dotenv

load_dotenv()

File = namedtuple('File', ['name', 'size'])


class Folder:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.files = []
        self.sub_folders = []

    def add_file(self, name, size):
        self.files.append(File(name, size))

    def get_folder(self, name):
        if name == "..":
            return self.parent;
        return next(filter(lambda d: d.name == name, self.sub_folders))

    def add_folder(self, name):
        f = Folder(name, self)
        self.sub_folders.append(f)
        return f

    def collect_sizes(self):
        size = 0
        details = []

        for d in self.sub_folders:
            s, d = d.collect_sizes()
            size += s
            details.extend(d)

        for f in self.files:
            size += f.size

        details.append(size)
        return size, details


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
        root = Folder("/")
        ptr = root
        for line in self.data:
            if line[0] == "$":
                if line[1] == 'ls':
                    continue
                if line[2] == '/':
                    ptr = root
                    continue
                ptr = ptr.get_folder(line[2])
            else:
                if line[0] == "dir":
                    ptr.add_folder(line[1])
                else:
                    ptr.add_file(line[1], int(line[0]))
        size, details = root.collect_sizes()
        print(sum(filter(lambda s: s <= 100000, details)))
        return size, details

    def second_part(self):
        size, details = self.first_part()
        total = 70_000_000
        needed = 30_000_000
        unused = total - size
        missing = needed - unused
        for s in sorted(details):
            if s >= missing:
                return s


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = ' '
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
