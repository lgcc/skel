#!/usr/bin/python
# encoding: utf-8

from mahotas.thin import thin
import numpy as np
import mahotas
from PIL import Image


if __name__ == '__main__':

    path = '../../data/tiao-shape.bmp'
    im = mahotas.imread(path)
    img = (im == 0)
    # print im
    # res = thin(im)

    img[img] = 255

    Image.fromarray(img, mode='1').show()