import numpy as np
from fortuns_algorithm import FortuneAlgorithm
from metrix import l2
import matplotlib.pyplot as plt

if __name__ == '__main__':
    points = np.array([[2., 2.], [1., 1.], [2., 3.], [3., 0.]])

    points = np.array([np.random.uniform(0, 5, size=(2,)) for _ in range(10)])

    fortuna = FortuneAlgorithm(points, metric=l2)

    fortuna.construct()

    fortuna.bound(-1.5, -1.5, 6.5, 6.5)

    diagram = fortuna.diagram

    plt.xlim((-1, 6))
    plt.ylim((-1, 6))

    plt.scatter(*zip(*points))

    for p in diagram.vertices:
        plt.scatter(*p.point, color='red')


    for e in diagram.half_edges:
        #print(e.origin, e.destination)
        if e.origin is not None and e.destination is not None:
            plt.plot(*zip(*[e.origin.point, e.destination.point]), color='red')

    plt.show()
