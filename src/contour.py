#!/usr/bin/python
# encoding: utf-8

import numpy as np
import cv2
from pprint import pprint
from PIL import Image
from collections import defaultdict


def find_contour(im):
    thresh = im
    im2, cons, hies = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if cons:
        cnt = cons[0]
        rect = cv2.boundingRect(cnt)
        x,y,w,h = rect
    else:
        print ('no contours found')

    # print len(cons)
    # pprint (cons)

    # print len(hies)
    # pprint (hies)

    if np.any(im2):
        pprint (im2)
        pprint (cons)
        pprint (hies)


def find_junction(im, w, h):
    juncs = defaultdict(list)
    im = im < 0x7F
    i = 1
    while i < h-1:
        # print 'scan line', i
        j = 1
        while j < w -1:
            # print 'col', j
            if not im[i, j]:
                j += 1
                continue
            m = slice(i-1, i+2)
            n = slice(j-1, j+2)
            view = im[m,n]
            num = np.count_nonzero(view)
            if num == 2:
                print 'double end:', i, j
                # juncs[num].append((i,j))
            elif num == 3:
                print 'triple neighbor:', i, j
                # juncs[num].append((i,j))
            elif num == 4:
                print 'quadruple junction:', i, j
                juncs[num].append((i,j))
            elif num == 5:
                print 'cross junction:', i, j
                juncs[num].append((i,j))
            elif num == 1:
                pass
            else:
                print 'kidding me ?!', i, j, num
            j += 1
        i += 1

    im = im >= 0x7F
    return juncs


if __name__ == '__main__':

    # path = '../../data/tiao-shape_skel.pgm'
    # path = 'Tagged skeleton.png'
    path = '../../data/tiao-shape_skel.bmp'
    # path = '../../data/skel.bmp'
    im = cv2.imread(path)
    imgray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)

    ret, thresh = cv2.threshold(imgray, 127, 255, 0)
    h, w = thresh.shape
    juncs = find_junction(thresh, w, h)
    print 'juncs:', juncs

    cv2.imshow('win', thresh)
    cv2.waitKey()
    cv2.destroyWindow('win')