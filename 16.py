import os
import random
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
PART2 = False

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

    def get_valves(self):
        valves = {}
        p = re.compile("Valve\s([A-Z]{2})\s.*=(\d+);.*valve[s]?\s([A-Z ,]+)")
        for row in self.data:
            m = p.match(row)
            valve = m.group(1)
            rate = int(m.group(2))
            neighbours = list(map(lambda v: v.strip(), m.group(3).split(",")))
            print(valve, rate, neighbours)
            valves[valve] = (rate, neighbours)  # rate, opened, list of neighbours
        return valves

    def first_part(self):
        result = 0
        valves = self.get_valves()
        seen = set()
        queue = deque()
        queue.append(("AA", tuple(), 0, "_", ("AA",)))
        for minute in range(1, 31):
            print(f"{minute}: {len(queue)}")
            for _ in range(len(queue)):
                state = queue.popleft()
                current_valve, opened, total, path, just_walked = state
                rate, neighbours = valves[current_valve]

                if ((current_valve, opened) in seen):
                    continue

                seen.add((current_valve, opened))

                if rate > 0 and current_valve not in opened:
                    pressure = (30 - minute) * rate
                    new_total = total + pressure
                    if new_total > result:
                        result = new_total
                    queue.append(
                        (current_valve, opened + (current_valve,), new_total, f"{path}{current_valve}o", (current_valve,)))
                for n in neighbours:
                    if n not in just_walked:
                        queue.append((n, opened, total, f"{path}{current_valve}", just_walked + (current_valve,)))
        return result

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
