#!/usr/bin/env python

import cv


class WatermarkRemover(object):

    @classmethod
    def load_image(cls, path):
        return cls(cv.LoadImageM(path))

    def __init__(self, image):
        self.mat = image
        self.detect_constants()

    def detect_alphas(self):
        m = self.mat
        self.alphas = set()
        for r in range(m.rows):
            for c in range(m.cols):
                if c == 0:
                    x, y, z = m[r, c]
                else:
                    nx, ny, nz = m[r, c]
                    if x and y and z and round(nx / x, 3) == round(ny / y, 3) == round(nz / z, 3):
                        self.alphas.add(round(nx / x, 3))
                        if round(nx / x, 3) not in (0.0, 1.0):
                            m[r, c] = (256.0, 0.0, 0.0)
                    x, y, z = nx, ny, nz
        self.alphas -= {0.0, 1.0}
        cv.NamedWindow('demo', cv.CV_WINDOW_AUTOSIZE)
        cv.ShowImage('demo', m)
        cv.WaitKey()

    def detect_constants(self):
        m = self.mat
        self.constants = set()
        for r in range(m.rows):
            for c in range(m.cols):
                if c == 0:
                    x, y, z = m[r, c]
                else:
                    nx, ny, nz = m[r, c]
                    if self.approx_same(nx - x, ny - y, nz - z):
                        a = ave(nx - x, ny - y, nz - z)
                        if 5 < a:
                            self.constants.add(a)
                            m[r, c] = (0., 0., 255.)
                    x, y, z = nx, ny, nz
        cv.NamedWindow('demo', cv.CV_WINDOW_AUTOSIZE)
        cv.ShowImage('demo', m)
        cv.WaitKey()

    def approx_same(self, *args):
        a = ave(*args)
        epsilon = 5
        return all(abs(a - x) < epsilon for x in args)

def ave(*args):
    return sum(args) / len(args)


if __name__ == '__main__':
    import sys
    WatermarkRemover.load_image(sys.argv[1])
