#!/usr/bin/env python

import cv
import matplotlib.pyplot as plt


def plot(vec):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    x = range(len(vec))
    b = [c[0] for c in vec]
    g = [c[1] for c in vec]
    r = [c[2] for c in vec]
    ax.plot(x, r, 'r-', x, g, 'g-', x, b, 'b-')
    plt.show()

if __name__ == '__main__':
    from argparse import ArgumentParser

    ap = ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('-r', type=int, default=-1)
    ap.add_argument('-c', type=int, default=-1)
    args = ap.parse_args()

    m = cv.LoadImageM(args.image)
    if args.r != -1:
        vec = [m[args.r, i] for i in range(m.cols)]
    elif args.c != -1:
        vec = [m[i, args.c] for i in range(m.rows)]

    plot(vec)
