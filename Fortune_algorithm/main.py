import numpy as np
from fortuns_algorithm import FortuneAlgorithm
from metrix import l2
import matplotlib.pyplot as plt

def run(n, a, b):
    import time

    points = np.array([np.random.uniform(a, b, size=(2,)) for _ in range(n)])

    fortuna = FortuneAlgorithm(points, metric=l2)

    start = time.time()
    fortuna.construct()

    fortuna.bound(a-1.5, a-1.5, b + 1.5, b + 1.5)
    end = time.time()

    diagram = fortuna.diagram

    return diagram, points, end - start

if __name__ == '__main__':
    # (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,1), (2,2), (2,0)
    #points = np.array([np.array((0,0)), np.array((0,1)), np.array((0,2)), np.array((1,0)), np.array((1,1)), np.array((1,2)), np.array((2,1)), np.array((2,2)), np.array((2,0))])

    #points = np.array([(0, 0), (0, 1.), (0.5, 0.5), (1., 0), (1., 1.)])

    times = []

    '''ns = [10, 50, 100, 200, 400, 500, 1000, 3000, 5000, 7000, 10000, 12000]

    for i in ns:
        diagram, points, time = run(i, 0, 30)
        times.append(time)

    plt.plot(ns, times, marker='o')
    plt.show()'''

    a, b = 0, 2

    points = np.array([np.random.uniform(a, b, size=(2,)) for _ in range(100)])

    plt.xlim((a-1, b + 0.4))
    plt.ylim((a-1, b + 0.4))

    plt.scatter(*zip(*points), s=6)

    fortuna = FortuneAlgorithm(points, metric=l2)
    fortuna.construct()
    fortuna.bound(a-1.5, a-1.5, b + 1.5, b + 1.5)

    diagram = fortuna.diagram

    for p in diagram.vertices:
        plt.scatter(*p.point, color='red', s=6)

    for e in diagram.half_edges:
        #print(e.origin, e.destination)
        if e.origin is not None and e.destination is not None:
            plt.plot(*zip(*[e.origin.point, e.destination.point]), color='red', linewidth=1)

    plt.show()
