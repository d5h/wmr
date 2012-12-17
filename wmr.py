#!/usr/bin/env python

import cv


class WatermarkRemover(object):

    @classmethod
    def load_image(cls, path):
        return cls(cv.LoadImageM(path))

    def __init__(self, image):
        self.mat = image
        self.detect_constants()

    def detect_constants(self):
        m = self.mat
        const = 0
        for r in range(m.rows):
            for c in range(m.cols):
                if c == 0:
                    x, y, z = m[r, c]
                else:
                    nx, ny, nz = m[r, c]
                    if self.approx_same(nx - x, ny - y, nz - z):
                        a = ave(nx - x, ny - y, nz - z)
                        if 5 < a < 30:
                            if self.approx_same(-const, a):
                                const = 0
                            else:
                                const = a
                    if const:
                        m[r, c] = (nx - const, ny - const, nz - const)
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
