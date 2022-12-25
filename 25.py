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
from aoc import *
from dotenv import load_dotenv

load_dotenv()

DEV = False
PART2 = False

STRIP = True
SPLIT_LINES = True
SPLIT_CHAR = None
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

SNA2DEC = {
    '2': 2,
    '1': 1,
    '0': 0,
    '-': -1,
    "=": -2
}

DEC2SNA = {
    0: ('0', 0),
    1: ('1', 0),
    2: ('2', 0),
    3: ('=', 1),
    4: ('-', 1)
}


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

    def sna2dec(self, snafu):
        result = 0
        p = 1
        for c in reversed(snafu):
            result += (SNA2DEC[c] * p)
            p *= 5
        return result

    def dec2sna(self, n):
        result = []
        while n > 0:
            r = n % 5
            result.append(DEC2SNA[r][0])
            n = n // 5 + DEC2SNA[r][1]
        return "".join(reversed(result))

    def first_part(self):
        return self.dec2sna(sum(map(lambda s: self.sna2dec(s), self.data)))

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
