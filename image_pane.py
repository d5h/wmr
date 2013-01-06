#!/usr/bin/env python

import sys

from PyQt4 import QtCore, QtGui
from qimage2ndarray import array2qimage

from wmr import WatermarkRemover


class ClickableImageLabel(QtGui.QLabel):

    def set_callbacks(self, on_press):
        self.on_press = on_press

    def mousePressEvent(self, event):
        self.on_press(event)

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass


class ImagePane(QtGui.QWidget):

    def __init__(self, path):
        super(ImagePane, self).__init__()
        self.path = path

        hbox = QtGui.QHBoxLayout(self)
        self.label = ClickableImageLabel(self)
        self.pixmap = QtGui.QPixmap(path)
        self.label.setPixmap(self.pixmap)
        hbox.addWidget(self.label)
        self.setLayout(hbox)

        cursor_img = QtGui.QPixmap('cursor40.png')
        cursor = QtGui.QCursor(cursor_img)
        self.label.setCursor(cursor)

        self.show()

    def catch_mouse(self, on_press):
        self.label.set_callbacks(on_press)


class ImageWmrGlue(object):

    def __init__(self, wmr, win):
        self.wmr = wmr
        self.win = win
        win.catch_mouse(self.process_press)

    def set_cursor_size(self, size):
        self.cursor_size = size

    def process_press(self, event):
        center = event.posF()
        cx = center.x()
        cy = center.y()
        x = cx - self.cursor_size / 2
        y = cy - self.cursor_size / 2
        self.wmr.set_roi(x, y, self.cursor_size, self.cursor_size)
        self.wmr.process()

        img = array2qimage(self.wmr.image[:, :, ::-1])
        self.win.pixmap.convertFromImage(img)
        self.win.label.repaint()


def main(path):
    wmr = WatermarkRemover.load_image(path)

    app = QtGui.QApplication(sys.argv)
    win = ImagePane(path)
    glue = ImageWmrGlue(wmr, win)
    glue.set_cursor_size(40)

    sys.exit(app.exec_())


if __name__ == '__main__':
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('path')
    args = ap.parse_args()

    main(args.path)
