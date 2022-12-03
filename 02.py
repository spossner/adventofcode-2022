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

ROCK, PAPER, SCISSORS = 1, 2, 3
LOST, DRAW, WON = 0, 3, 6
ELF_CODE_MAP = {"A": ROCK, "B": PAPER, "C": SCISSORS}
YOU_CODE_MAP = {"X": ROCK, "Y": PAPER, "Z": SCISSORS}
WIN_CODE_MAP = {"X": LOST, "Y": DRAW, "Z": WON}


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

    def compare(self, elf, you):
        if elf == you:
            return DRAW
        if elf == ROCK:
            return WON if you == PAPER else LOST
        if elf == PAPER:
            return WON if you == SCISSORS else LOST
        if elf == SCISSORS:
            return WON if you == ROCK else LOST

    def find_pair(self, elf, result):
        if result == DRAW:
            return elf
        if elf == ROCK:
            return PAPER if result == WON else SCISSORS
        if elf == PAPER:
            return SCISSORS if result == WON else ROCK
        if elf == SCISSORS:
            return ROCK if result == WON else PAPER

    def first_part(self):
        total = 0
        for [elf_code, you_code] in self.data:
            elf, you = ELF_CODE_MAP[elf_code], YOU_CODE_MAP[you_code]
            result = self.compare(elf, you)
            total += result + you
        return total

    def second_part(self):
        total = 0
        for [elf_code, you_code] in self.data:
            elf = ELF_CODE_MAP[elf_code]
            result = WIN_CODE_MAP[you_code]
            you = self.find_pair(elf, result)
            print(elf_code, you_code, elf, you, result)
            total += result + you
        return total


if __name__ == '__main__':
    script = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if '-' in script:
        script = script.split('-')[0]

    DEV = False
    PART2 = True

    STRIP = True
    SPLIT_LINES = True
    SPLIT_CHAR = " "
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
