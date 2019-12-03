import numpy as np
from Event import Event, EventType
from Events import Events
from BeachLine import Arc, BeachLine
from metrix import l2
from voronoi_diagram import VoronoiDiagram

from enum import Enum


class Side(Enum):
    left = 0
    bottom = 1
    right = 2
    top = 3


class FortuneAlgorithm:
    metrics = {'l2': l2}

    def __init__(self, points, named_metric='l2', metric=None):

        self.diagram = VoronoiDiagram(points)

        if metric is not None:
            self.metric = metric
            self.compute_convergence_point = metric.compute_convergence_point
        elif named_metric in FortuneAlgorithm.metrics:
            self.metric = FortuneAlgorithm.metrics[named_metric]
            self.compute_convergence_point = metric.compute_convergence_point
        else:
            raise ValueError('Can\'t resolve metric function', metric, 'please choose from list, \
            or implement your own. list: ', FortuneAlgorithm.metrics.keys())

        self.beach_line = BeachLine(self.metric.compute_breakpoint)

    def construct(self):
        events = Events()

        for s in self.diagram.sites:
            event = Event(s.point[1], EventType.site, site=s, point=s.point)
            events.insert(event)

        not_valid_events = set()

        while not events.empty():
            event = events.pop()

            if event in not_valid_events:
                continue

            if event.type == EventType.site:
                self.handle_site_event(event, not_valid_events, events)
            else:
                self.handle_circle_event(event, not_valid_events, events)

    def break_arc_by_site(self, arc, site):
        middle_arc = Arc(site)

        left_arc = Arc(arc.site)
        left_arc.left_half_edge = arc.left_half_edge

        right_arc = Arc(arc.site)
        right_arc.right_half_edge = arc.right_half_edge

        self.beach_line.replace(arc, middle_arc)
        self.beach_line.insert_before(middle_arc, left_arc)
        self.beach_line.insert_after(middle_arc, right_arc)

        return middle_arc

    def add_edge(self, left, right):
        left.right_half_edge = self.diagram.add_half_edge(left.site.face)
        right.left_half_edge = self.diagram.add_half_edge(right.site.face)

        left.right_half_edge.twin = right.left_half_edge
        right.left_half_edge.twin = left.right_half_edge

    def add_event(self, left, middle, right, events, beachline_y):
        y, convergence_point = self.metric.compute_convergence_point(left.site.point, middle.site.point,
                                                                     right.site.point)

        is_below = y <= beachline_y

        left_point_is_moving_right = left.site.point[1] < middle.site.point[1]
        right_point_is_moving_right = middle.site.point[1] < right.site.point[1]

        left_initial_x = left.site.point[0] if left_point_is_moving_right else middle.site.point[0]
        right_initial_x = middle.site.point[0] if right_point_is_moving_right else right.site.point[0]

        is_valid = ((left_point_is_moving_right and left_initial_x < convergence_point[0]) or
                    ((not left_point_is_moving_right) and left_initial_x > convergence_point[0])) and \
                   ((right_point_is_moving_right and right_initial_x < convergence_point[0]) or
                    ((not right_point_is_moving_right) and right_initial_x > convergence_point[0]))

        if is_valid and is_below:
            event = Event(y, EventType.circle, point=convergence_point, arc=middle)
            middle.event = event
            events.insert(event)

    def handle_site_event(self, event, not_valid_events, events):
        site = event.site

        if self.beach_line.is_empty():
            self.beach_line.set_root(Arc(site))
            return

        arc_above = self.beach_line.get_arc_above(site.point, site.point[1])

        if arc_above.event is not None:
            not_valid_events.add(arc_above.event)

        middle_arc = self.break_arc_by_site(arc_above, site)
        left_arc = middle_arc.prev
        right_arc = middle_arc.next

        self.add_edge(left_arc, middle_arc)

        middle_arc.right_half_edge = middle_arc.left_half_edge
        right_arc.left_half_edge = left_arc.right_half_edge

        if left_arc.prev is not None:
            self.add_event(left_arc.prev, left_arc, middle_arc, events, site.point[1])

        if right_arc.next is not None:
            self.add_event(middle_arc, right_arc, right_arc.next, events, site.point[1])

    def remove_arc(self, arc, vertex):
        arc.prev.right_half_edge.origin = vertex
        arc.left_half_edge.destination = vertex

        arc.right_half_edge.origin = vertex
        arc.next.left_half_edge.destination = vertex

        arc.left_half_edge.next = arc.right_half_edge
        arc.right_half_edge.prev = arc.left_half_edge

        self.beach_line.delete(arc)

        prev_half_edge = arc.prev.right_half_edge
        next_half_edge = arc.next.left_half_edge

        self.add_edge(arc.prev, arc.next)

        arc.prev.right_half_edge.destination = vertex
        arc.next.left_half_edge.origin = vertex

        self.prev_half_edge(arc.prev.right_half_edge, prev_half_edge)
        self.prev_half_edge(next_half_edge, arc.next.left_half_edge)

    def prev_half_edge(self, prev, next):
        prev.next = next
        next.prev = prev

    def handle_circle_event(self, event, not_valid_events, events):
        point = event.point
        arc = event.arc

        voronoi_vertex = self.diagram.add_vertex(point)

        left_arc = arc.prev
        right_arc = arc.next

        if left_arc is not None and left_arc.event is not None:
            not_valid_events.add(left_arc.event)

        if right_arc is not None and right_arc.event is not None:
            not_valid_events.add(right_arc.event)

        self.remove_arc(arc, voronoi_vertex)

        if left_arc.prev is not None:
            self.add_event(left_arc.prev, left_arc, right_arc, events, event.y)

        if right_arc.next is not None:
            self.add_event(left_arc, right_arc, right_arc.next, events, event.y)

    def adjust_box(self, x_left, y_left, x_right, y_right, points):
        delta = np.array([0.05, 0.05])
        for p in points:
            x_left = np.min(x_left, p.point[0] + delta[0])
            y_left = np.min(y_left, p.point[1] + delta[1])

            x_right = np.max(x_right, p.point[0] + delta[0])
            y_right = np.max(y_right, p.point[1] + delta[1])

        return x_left, y_left, x_right, y_right

    def get_intersection(self, x_left, y_left, x_right, y_right, origin, direction):
        intersection = None
        side = Side.left

        t1, t2 = None, None

        if direction[0] > 0.:
            t1 = (x_right - origin[0]) / direction[0]
            side = Side.right
            intersection = origin + t1 * direction
        elif direction[0] < 0.:
            t1 = (x_left - origin[0]) / direction[0]
            side = Side.left
            intersection = origin + t1 * direction

        if direction[1] > 0.:
            t2 = (y_right - origin[1]) / direction[1]

            if t2 < t1:
                side = Side.top
                intersection = origin + t2 * direction
        elif direction[1] < 0.:
            t2 = (y_left - origin[1]) / direction[1]

            if t2 < t1:
                side = Side.bottom
                intersection = origin + t2 * direction

        return intersection, side

    def bound(self, x_left, y_left, x_right, y_right):
        #x_left, y_left, x_right, y_right = self.adjust_box(x_left, y_left, x_right, y_right, self.diagram.sites)
        #x_left, y_left, x_right, y_right = self.adjust_box(x_left, y_left, x_right, y_right, self.diagram.vertices)

        if not self.beach_line.is_empty():
            left_arc = self.beach_line.get_leftmost_arc()
            right_arc = left_arc.next

            while right_arc is not None:
                direction = (left_arc.site.point - right_arc.site.point)[[1, 0]]
                direction[0] *= -1

                origin = (left_arc.site.point + right_arc.site.point) * 0.5

                intersection, side = self.get_intersection(x_left, y_left, x_right, y_right, origin, direction)

                vertex = self.diagram.add_vertex(intersection)

                left_arc.right_half_edge.origin = vertex
                right_arc.left_half_edge.destination = vertex

                left_arc = right_arc
                right_arc = right_arc.next
