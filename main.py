import numpy as np
from fortuns_algorithm import FortuneAlgorithm
from metrix import l2
import matplotlib.pyplot as plt

if __name__ == '__main__':
    points = np.array([[20., 20.], [10., 10.], [20., 30.], [30., 0.]])
    fortuna = FortuneAlgorithm(points, metric=l2)

    fortuna.construct()

    diagram = fortuna.diagram

    plt.scatter(*zip(*points))

    print(diagram.vertices[0].point)

    for p in diagram.vertices:
        plt.scatter(*p.point, color='red')

    for e in diagram.half_edges:
        #print(e.origin, e.destination)
        if e.origin is not None and e.destination is not None:
            plt.plot(*zip(*[e.origin.point, e.destination.point]), color='red')

    plt.show()
