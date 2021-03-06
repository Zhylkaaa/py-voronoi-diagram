import numpy as np


class Metric:

    @staticmethod
    def compute_breakpoint(point1, point2, l):
        """
        :param point1: first focus of parabola
        :param point2: second focus of parabola
        :param l: directrix y coordinate
        :return: breakpoint y position
        """
        pass

    @staticmethod
    def compute_convergence_point(point1, point2, point3):
        """
        :param point1: first site
        :param point2: second site
        :param point3: third site
        :return: convergence point defined by this points
        """
        pass


class l2(Metric):

    @staticmethod
    def compute_breakpoint(point1, point2, l):
        x1, y1 = point1
        x2, y2 = point2

        eps = 1e-6

        d1 = 0.5/((y1 - l) + eps)
        d2 = 0.5/((y2 - l) + eps)

        a = d1 - d2
        b = 2.0 * (d2*x2 - d1*x1)
        c = (x1*x1 - l*l + y1*y1) * d1 - (x2*x2 - l*l + y2*y2) * d2
        #c = x1*x1*d1 - (y1 + l) * 0.5 - x2*x2*d2 + (y2 + l)*0.5

        delta = b*b - 4.0*a*c

        #if delta < 0: # TODO: corner case what to do when parabolas doesn't intersect
        #    print(delta)

        return (-b + np.sqrt(np.abs(delta))) / (2.0*a + eps)

    @staticmethod
    def compute_convergence_point(point1, point2, point3):
        v1 = (point1-point2)[[1, 0]]
        v2 = (point2 - point3)[[1, 0]]
        v1[0] = -v1[0]
        v2[0] = -v2[0]

        delta = (point3 - point1) * 0.5

        eps = 1e-6

        t = (delta[0] * v2[1] - delta[1]*v2[0]) / (v1[0] * v2[1] - v1[1]*v2[0] + eps)

        center = 0.5 * (point1 + point2) + t*v1

        r = np.sqrt(np.sum((point1 - center)**2))

        y = center[1] - r

        return y, center
