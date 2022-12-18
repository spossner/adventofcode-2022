from __future__ import annotations

import copy
import os
import random
import sys
import time
from abc import abstractmethod
from collections import defaultdict
from itertools import combinations, count
from os.path import exists

import requests
from aoc import *
from dotenv import load_dotenv

load_dotenv()

DEV = True
PART2 = False

STRIP = True
SPLIT_LINES = False
SPLIT_CHAR = ''
DATA = None
AOC_SESSION = os.environ.get('AOC_SESSION')
YEAR = 2022

DOWN = Point(0, -1)
UP = Point(0, 1)
LEFT = WEST
RIGHT = EAST
DIRECTIONS = {
    '>': RIGHT,
    '<': LEFT,
}


class Shape:
    def __init__(self, outline: Rect):
        self._outline = outline

    def translate(self, offset: Union[Point, tuple]):
        self.outline.translate(offset)
        return self

    def move_to(self, x: int, y: int):
        self.outline.move_to(Point(x, y))
        return self

    @abstractmethod
    def pixel(self, p: Union[Point, tuple]):
        pass

    @property
    def outline(self):
        return self._outline

    def intersect(self, other: Shape):
        intersection = self.outline.intersection(other.outline)
        for p in intersection:
            if self.pixel(p) and other.pixel(p):
                return True
        return False

    def __contains__(self, other):
        if type(other) == Point or type(other) == tuple and len(other) > 1:
            return self.pixel(other)
        return False


class SolidShape(Shape):
    def __init__(self, w: int, h: int):
        super().__init__(Rect(0, 0, w, h))

    def pixel(self, p: Point) -> int:
        return 1 if p in self.outline else 0

    def intersect(self, other: Shape):
        if isinstance(other, SolidShape):
            return bool(self.outline.intersection(other.outline))  # check intersection not empty
        return super().intersect(other)

    def __contains__(self, other):
        if isinstance(other, SolidShape):
            return other.outline in self.outline
        if type(other) == Point:
            return other in self.outline
        return super().__contains__(other)


class Sprite(Shape):
    def __init__(self, sprite):
        super().__init__(Rect(0, 0, len(sprite[0]) if sprite else 0, len(sprite)))
        self.sprite = sprite

    def pixel(self, p: Union[Point, tuple]):
        return self.sprite[p[1] - self.outline.y][p[0] - self.outline.x] if p in self.outline else 0


class Dash(SolidShape):
    def __init__(self):
        super().__init__(4, 1)


class Pipe(SolidShape):
    def __init__(self):
        super().__init__(1, 4)


class Square(SolidShape):
    def __init__(self):
        super().__init__(2, 2)


class Diamond(Sprite):
    def __init__(self):
        super().__init__(((0, 1, 0), (1, 1, 1), (0, 1, 0)))


class Hook(Sprite):
    def __init__(self):
        super().__init__(((1, 1, 1), (0, 0, 1), (0, 0, 1)))


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

    def dump(self, shapes, bounds=None, min_width=0):
        if not bounds:
            bounds = Rect(0, 0, 1, 1)
            for s in shapes:
                bounds.extend(s.outline)
            bounds.h += 2

        bounds.w = max(bounds.w, min_width)

        for y in reversed(range(bounds.h)):
            print("|", end="")
            for x in range(bounds.w):
                p = Point(x, y)
                try:
                    if next(filter(lambda s: p in s, shapes)):
                        print("#", end="")
                except StopIteration:
                    print(".", end="")
            print("|")
        print(f"+{'-' * bounds.w}+\n")

    def first_part(self):
        result = 0
        spawner = [Dash, Diamond, Hook, Pipe, Square]
        moves = self.data
        shapes = defaultdict(list)
        all_shapes = []
        WIDTH = 7
        ptr = 0
        bounds = Rect(0, -1, 7, 1)
        for i in range(1_000_000_000_000 if PART2 else 2022):
            if i % 100_000 == 0:
                print(".", end="")
            new_shape = spawner[i % len(spawner)]().move_to(2, bounds.y + bounds.h + 3)
            for _ in count():
                dummy = copy.deepcopy(new_shape)
                move = moves[ptr]
                ptr = (ptr + 1) % len(moves)

                dummy.translate(DIRECTIONS[move])

                touching_shapes = set()
                for y in range(dummy.outline.y, dummy.outline.y + dummy.outline.h):
                    for s in shapes[y]:
                        touching_shapes.add(s)

                try:
                    if dummy.outline.x < 0 or dummy.outline.x + dummy.outline.w > WIDTH or next(
                            filter(lambda s: dummy.intersect(s), touching_shapes)):
                        # collision -> reset to new_shape
                        # print(move, "COLLISION")
                        dummy = copy.deepcopy(new_shape)
                except StopIteration:
                    # print(move, "OK")
                    pass

                dummy.translate(DOWN)
                touching_shapes = set()
                for y in range(dummy.outline.y, dummy.outline.y + dummy.outline.h):
                    for s in shapes[y]:
                        touching_shapes.add(s)
                try:
                    if dummy.outline.y < 0 or next(
                            filter(lambda s: dummy.intersect(s), touching_shapes)):
                        # collision - move up again
                        dummy.translate(UP)

                        # all_shapes.append(dummy)
                        for y in range(dummy.outline.y, dummy.outline.y + dummy.outline.h):
                            shapes[y].append(dummy)
                        bounds.extend(dummy.outline)
                        break
                except StopIteration:
                    new_shape = dummy  # go on with dummy as new shape

            # self.dump(all_shapes, min_width=WIDTH)
        print(bounds, bounds.h + bounds.y)

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
