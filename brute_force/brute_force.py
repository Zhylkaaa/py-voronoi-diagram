import numpy as np
import functools
import matplotlib.pyplot as plt
import copy


def qsort(table, l, r, comparator=lambda x, y: x < y):
    if l == r:
        return
    m = (l + r) // 2
    pivot = table[m]
    j = l

    tmp = copy.copy(table[r - 1])
    table[r - 1] = table[m]
    table[m] = tmp

    for i in range(l, r - 1):
        if comparator(table[i], pivot):

            tmp = copy.copy(table[i])
            table[i] = table[j]
            table[j] = tmp

            j += 1

    tmp = copy.copy(table[r - 1])
    table[r - 1] = table[j]
    table[j] = tmp

    qsort(table, l, j, comparator)
    qsort(table, j + 1, r, comparator)


class Vertex(object):

    def __init__(self, point, direction, idx, site, next=None, prev=None):
        self.point = point
        self.direction = direction
        self.idx = idx
        self.site = site
        self.next = next
        self.prev = prev

    def __copy__(self):
        new_one = type(self)(self.point, self.direction, self.idx, self.site, self.next, self.prev)
        return new_one


class Face:

    def __init__(self, site):
        self.vertex = []
        self.site = site


def det(a, b, c):
    return a[0] * b[1] + a[1] * c[0] + b[0] * c[1] - b[1] * c[0] - a[1] * b[0] - a[0] * c[1]


def get_orientation(point, segment_start, segment_end, eps=1e-6):
    orientation = det(segment_start, segment_end, point)
    if orientation < -eps:
        return -1
    elif orientation > eps:
        return 1
    else:
        return 0


def check_point(point_idx, site_idx, points, vertices):
    point = points[point_idx]
    site = points[site_idx]

    is_valid = True

    for v in vertices:

        orientation = get_orientation((point + site) * 0.5, v.point, v.point + v.direction)
        if orientation == 1:
            is_valid = False

    if is_valid:
        direction = (point - site)[[1, 0]]
        direction[1] *= -1
        vertices.append(Vertex((point + site) * 0.5, direction, point_idx, site))


def validate_vertices(vertices):
    result = []

    for i in vertices:
        is_valid = True

        for j in vertices:

            if i is j:
                continue

            orientation = get_orientation(i.point, j.point, j.point + j.direction)

            if orientation == 1 and sqr_dist(i.point, i.site) > sqr_dist(j.point, i.site):
                is_valid = False

        if is_valid:
            result.append(i)

    return result


def compute_voronoi_vertices(idx, points):
    vertices = []

    i = idx - 1
    j = idx + 1

    use_i = True

    while i >= 0 and j < len(points):

        if use_i:
            check_point(i, idx, points, vertices)
            i -= 1
        else:
            check_point(j, idx, points, vertices)
            j += 1

        use_i = not use_i

    while i >= 0:
        check_point(i, idx, points, vertices)
        i -= 1

    while j < len(points):
        check_point(j, idx, points, vertices)
        j += 1

    return validate_vertices(vertices)


def sqr_dist(a, b):
    return np.sum((a - b) ** 2)


def comparator(b, c, a, eps=1e-6):
    orientation = det(a.point, b.point, c.point)

    if orientation <= eps and orientation >= -eps:
        return sqr_dist(a.point, b.point) < sqr_dist(a.point, c.point)
    else:
        return orientation > eps


def find_leftmost(points):
    p0 = points[0]
    idx = 0

    for i, p in enumerate(points[1:]):
        if p0.point[1] > p.point[1]:
            p0 = p
            idx = i + 1
        elif p0.point[1] == p.point[1] and p0.point[0] > p.point[0]:
            p0 = p
            idx = i + 1
    return p0, idx


def intersection_t(p1, p2, eps=1e-6):
    r = p1.direction
    s = p2.direction * (-1)

    rxs = r[0] * s[1] - r[1] * s[0]  # if rxs = 0 then lines colinear

    if rxs > eps or rxs < -eps:
        q_p = p2.point - p1.point
        t = (q_p[0] * s[1] - q_p[1] * s[0]) / rxs
        return t
    else:
        return None


def create_face(vertices):
    if len(vertices) == 0:
        return Face(None)

    p0, _ = find_leftmost(vertices)

    cmp = functools.partial(comparator, a=p0)

    qsort(vertices, 0, len(vertices), cmp)

    vertices.reverse()


    idx = 0
    n = len(vertices)

    face = Face(vertices[0].site)

    while True:
        t = intersection_t(vertices[idx], vertices[(idx + 1) % n])

        if t is not None and t > 0.:
            direction = (vertices[idx].point - vertices[idx].site)[[1, 0]]
            direction[0] *= -1

            vertex = Vertex(vertices[idx].point + t * vertices[idx].direction,
                            direction,
                            None, vertices[idx].site)

            vertices[idx].next = vertex
            vertices[(idx + 1) % n].prev = vertex

            face.vertex.append(vertex)

        idx = (idx + 1) % n
        if idx == 0:
            break

    for v in vertices:

        if v.next is not None:
            v.next.prev = v.prev

        if v.prev is not None:
            v.prev.next = v.next

    return face


def get_intersection_with_box(x_left, y_left, x_right, y_right, v):

    direction = v.direction
    origin = v.point

    intersection = None
    t1, t2 = None, None

    if direction[0] > 0.:
        t1 = (x_right - origin[0]) / direction[0]
        intersection = origin + t1 * direction
    elif direction[0] < 0.:
        t1 = (x_left - origin[0]) / direction[0]
        intersection = origin + t1 * direction

    if direction[1] > 0.:
        t2 = (y_right - origin[1]) / direction[1]

        if t2 < t1:
            intersection = origin + t2 * direction
    elif direction[1] < 0.:
        t2 = (y_left - origin[1]) / direction[1]

        if t2 < t1:
            intersection = origin + t2 * direction

    return intersection


def bound_faces(faces, x_left, y_left, x_right, y_right):  # TODO: bound diagram

    for face in faces:

        verts = face.vertex.copy()

        for v in verts:

            if v.prev is None:
                intersection = get_intersection_with_box(x_left, y_left, x_right, y_right, v)

                vertex = Vertex(intersection, None, None, v.site)

                v.prev = vertex
                vertex.next = v
                face.vertex.append(vertex)

            if v.next is None:
                intersection = get_intersection_with_box(x_left, y_left, x_right, y_right, v)

                vertex = Vertex(intersection, None, None, v.site)

                v.next = vertex
                vertex.prev = v
                face.vertex.append(vertex)


def alphabetic(a, b):
    return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1])


def compute_voronoi_diagram(points, x_left, y_left, x_right, y_right):
    #print(points)

    qsort(points, 0, len(points), comparator=alphabetic)

    #print(points)

    voronoi_vertices = [[] for _ in range(len(points))]

    for i in range(len(points)):
        voronoi_vertices[i] = compute_voronoi_vertices(i, points)

    faces = [create_face(vertices) for vertices in voronoi_vertices]

    bound_faces(faces, x_left, y_left, x_right, y_right)

    return faces, voronoi_vertices


def run(n):
    #points = np.array([np.array([2., 2.]), np.array([1., 1.]), np.array([2., 3.]), np.array([3., 0.])])

    points = np.array([np.random.uniform(0, 4, size=(2,)) for _ in range(n)])

    #points = np.array([(0, 0), (0, 1.), (0.5, 0.5), (1., 0), (1., 1.)])

    plt.scatter(*zip(*points))

    plt.xlim((-1, 5.1))
    plt.ylim((-1, 5.1))

    import time
    start = time.time()
    faces, voronoi_vertices = compute_voronoi_diagram(points, -2, -2, 6, 6)
    end = time.time()
    #colors = ['c', 'm', 'k', 'r']

    '''for i, vertices in enumerate(voronoi_vertices):
        for v in vertices:
            plt.scatter(*v.point, color='green')
            plt.plot(*zip(*[v.point, v.point + v.direction]), color=colors[i], linestyle='dashed')'''

    for i, face in enumerate(faces):
        for v in face.vertex:
            #print('main: ', v.point)
            plt.scatter(*v.point, color='red')
            if v.next is not None:
                plt.plot(*zip(*[v.point, v.next.point]), color='red')

    plt.show()

    return end - start

# TODO: add merging of diagrams (remove intersections between diagrams)

if __name__ == '__main__':
    times = []

    #ns = [10, 50, 100, 200, 400, 500, 1000]

    ns = [20]

    for i in ns:
        time = run(i)
        times.append(time)

    plt.plot(ns, times, marker='o')
    plt.show()
