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
from aoc import Point, Rect, NORTH, rot_ccw, rot_cw, translate, batched, get_ints
from dotenv import load_dotenv

load_dotenv()


class Monkey:
    def __init__(self, items, operation, check: int, next_true: int, next_false: int):
        self.items = deque(items)
        self.operation = operation
        self.check = check
        self.next_true = next_true
        self.next_false = next_false
        self.inspect_count = 0


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

    def first_part(self, part1=True):
        monkeys = []
        common_check = 1
        for rows in batched(self.data, 7):
            print(rows)
            monkey = Monkey(
                get_ints(rows[1]),
                rows[2][19:],
                get_ints(rows[3])[0],
                get_ints(rows[4])[0],
                get_ints(rows[5])[0]
            )
            monkeys.append(monkey)
            common_check *= monkey.check
        for round in range(20 if part1 else 10_000):
            for monkey in monkeys:
                while monkey.items:
                    old = monkey.items.popleft()
                    new = eval(monkey.operation)
                    new = int(new / 3) if part1 else new % common_check
                    monkey.inspect_count += 1
                    if new % monkey.check == 0:
                        monkeys[monkey.next_true].items.append(new)
                    else:
                        monkeys[monkey.next_false].items.append(new)
            # for i, monkey in enumerate(monkeys):
            #     print(f"Monkey {i}: {monkey.items} in {monkey.inspect_count}")
            print(reduce(lambda a, b: a * b,
                         map(lambda monkey: monkey.inspect_count, sorted(monkeys, key=lambda monkey: monkey.inspect_count)[-2:])))

        pass

    def second_part(self):
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
