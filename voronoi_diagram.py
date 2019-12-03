import numpy as np


class VoronoiDiagram:

    def __init__(self, points):
        self.sites = []
        self.faces = []

        for idx, p in enumerate(points):
            self.sites.append(Site(idx, p, None))
            self.faces.append(Face(self.sites[-1], None))
            self.sites[-1].face = self.faces[-1]

        self.vertices = []
        self.half_edges = []

    def add_half_edge(self, face):
        half_edge = HalfEdge(face)

        if face.edge is None:
            face.edge = half_edge

        self.half_edges.append(half_edge)
        return half_edge

    def add_vertex(self, point):

        vertex = Vertex(np.array(point))

        self.vertices.append(vertex)

        return vertex


class Site:

    def __init__(self, idx, point, face):
        self.idx = idx
        self.point = point
        self.face = face


class Vertex:

    def __init__(self, point):
        self.point = point


class HalfEdge:

    def __init__(self, incident_face, origin=None, destination=None, twin=None, prev=None, next=None):
        self.origin = origin
        self.destination = destination
        self.twin = twin
        self.incident_face = incident_face
        self.prev = prev
        self.next = next


class Face:

    def __init__(self, site, edge=None):
        self.site = site
        self.edge = edge
