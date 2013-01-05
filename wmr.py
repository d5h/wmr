#!/usr/bin/env python

import os

import cv2
import matplotlib.pyplot as plt
import numpy as np


class WatermarkRemover(object):

    OPACITY_RANGE = [10, 50]

    @classmethod
    def load_image(cls, path):
        return cls(cv2.imread(path))

    def __init__(self, image):
        self.arr = image
        self.process()

    def process(self, window_size=(40, 40), step=(40, 10), show_rect=False, show_hist=False):
        assert step[0] < window_size[0] or step[1] < window_size[1]
        a = self.arr
        histograms = []
        row_starts = range(0, a.shape[0] - window_size[0], step[0])
        col_starts = range(0, a.shape[1] - window_size[1], step[1])
        for r in row_starts:
            for c in col_starts:
                win = a[r:r + window_size[0], c:c + window_size[1]]
                h = [cv2.calcHist([win], [ch], None, [256], [0, 255])[:, 0] for ch in range(3)]
                h = np.column_stack(h)
                histograms.append(h)

        h_index = 0
        for r in row_starts:
            for c in col_starts:
                if c:
                    h1 = histograms[h_index - 1]
                    h2 = histograms[h_index]
                    d = h2 - h1
                    orig_vars = self.vars_from_hist(h2)
                    orig_ss = np.sqrt(np.sum(d ** 2) / d.size)
                    best_h2 = h2
                    best_ss = orig_ss
                    best_opacity = 0
                    for opacity in range(self.OPACITY_RANGE[0], self.OPACITY_RANGE[1] + 1):
                        new_h2 = self.adjust(h2, d, opacity / 100.)
                        new_vars = self.vars_from_hist(new_h2)
                        if all(new_vars < orig_vars):
                            new_d = new_h2 - h1
                            ss = np.sqrt(np.sum(new_d ** 2) / new_d.size)
                            if ss < best_ss:
                                best_ss = ss
                                best_opacity = opacity
                                best_h2 = new_h2
                                best_d = new_d

                    self.adjust(h2, d, best_opacity / 100.,
                                row_start=r, col_start=c + window_size[1] - step[1],
                                height=window_size[0], width=step[1])
                    histograms[h_index] = best_h2

                    if show_hist and best_opacity:
                        print 'orig=%.2f, new=%.2f, opac=%d' % (orig_ss, best_ss, best_opacity)
                        fig = plt.figure()
                        # Will crash if pure black
                        xmin = min(np.nonzero(h2)[0][0], np.nonzero(best_h2)[0][0])
                        xmax = max(np.nonzero(h2)[0][-1], np.nonzero(best_h2)[0][-1])
                        xs = range(int(xmin), int(xmax) + 1)
                        ax = fig.add_subplot(2, 2, 1)
                        ax.plot(xs, h2[xmin:xmax + 1, 0], 'b-', xs, h2[xmin:xmax + 1, 1], 'g-', xs, h2[xmin:xmax + 1, 2], 'r-')
                        ax.grid(True)
                        plt.xlabel('Base')

                        ax = fig.add_subplot(2, 2, 3)
                        ax.plot(xs, best_h2[xmin:xmax + 1, 0], 'b-', xs, best_h2[xmin:xmax + 1, 1], 'g-', xs, best_h2[xmin:xmax + 1, 2], 'r-')
                        ax.grid(True)
                        plt.xlabel('New')

                        ax = fig.add_subplot(2, 2, 2)
                        ax.plot(xs, d[xmin:xmax + 1, 0], 'b-', xs, d[xmin:xmax + 1, 1], 'g-', xs, d[xmin:xmax + 1, 2], 'r-')
                        ax.grid(True)
                        plt.xlabel('Base Diff')

                        ax = fig.add_subplot(2, 2, 4)
                        ax.plot(xs, best_d[xmin:xmax + 1, 0], 'b-', xs, best_d[xmin:xmax + 1, 1], 'g-', xs, best_d[xmin:xmax + 1, 2], 'r-')
                        ax.grid(True)
                        plt.xlabel('New Diff')

                        plt.show()

                if show_rect and (c or r):
                    canvas = np.copy(a)
                    cv2.rectangle(canvas, (c, r), (c + window_size[1], r + window_size[0]), (0, 0, 255))
                    cv2.imshow("Demo", canvas)
                    cv2.waitKey()


                h_index += 1

    def adjust(self, h, d, alpha, row_start=None, col_start=None, height=0, width=0):
        if row_start is not None:
            window = self.arr[row_start : row_start + height, col_start : col_start + width]
        else:
            window = None

        new_h = np.copy(h)
        for n, hchans in enumerate(d):
            new_n = (n - alpha * 255) / (1 - alpha)
            if 0 <= new_n <= 255:
                for c in range(3):
                    if 0 < hchans[c] and h[new_n, c]: # and d[new_n, c] < 0:
                        new_h[n, c] -= hchans[c]
                        new_h[new_n, c] += hchans[c]
                        if window is not None:
                            self.update_color(window, n, new_n, c)
        return new_h

    def update_color(self, window, old, new, channel):
        for r in range(window.shape[0]):
            for c in range(window.shape[1]):
                if window[r, c, channel] == old:
                    window[r, c, channel] = new

    def vars_from_hist(self, h):
        return np.array([self.var_from_hist(h[:, c]) for c in range(h.shape[1])])

    def var_from_hist(self, h):
        ave = 0.
        n = 0
        for i, b in enumerate(h):
            ave += b * i
            n += b
        ave /= n

        var = 0.
        for i, b in enumerate(h):
            var += b * (i - ave) ** 2

        return var / n


if __name__ == '__main__':
    import sys
    path = sys.argv[1]
    _, ext = os.path.splitext(path)
    wmr = WatermarkRemover.load_image(path)
    cv2.imwrite('output%s' % ext, wmr.arr)
    cv2.imshow("Demo", wmr.arr)
    cv2.waitKey()
