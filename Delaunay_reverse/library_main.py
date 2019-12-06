import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt

def run(n):
    import time

    points = np.array([np.random.uniform(0, 30, size=(2,)) for _ in range(n)])

    start = time.time()
    vor = Voronoi(points) # implemented with Delaunay triangulation
    end = time.time()

    #voronoi_plot_2d(vor)
    #plt.show()

    return end - start


if __name__ == '__main__':

    times = []

    ns = [10, 50, 100, 200, 400, 500, 1000, 3000, 5000, 7000, 10000, 12000]

    for i in ns:
        time = run(i)
        times.append(time)

    plt.plot(ns, times, marker='o')
    plt.show()
