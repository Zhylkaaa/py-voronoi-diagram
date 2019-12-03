import numpy as np
from enum import Enum


class EventType(Enum):
    site = 0
    circle = 1

    def __lt__(self, other):
        return self.value < other.value


class Event:
    def __init__(self, y, event_type, site=None, arc=None, point=None):
        self.y = y
        self.site = site
        self.type = event_type
        self.arc = arc
        self.point = point

    def __lt__(self, other):
        return self.y > other.y or (self.y == other.y and self.y < other.y)

    def __hash__(self):
        return hash(tuple(self.point))
