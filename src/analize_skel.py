#!/usr/bin/python
# encoding: utf-8

import numpy as np
import cv2
from PIL import Image
from collections import namedtuple
from pprint import pprint

from log import Log
from graph import Graph


log = Log(level=Log.DEBUG)

BranchInfo = namedtuple('BranchInfo', 'id length x y z x2 y2 z2 dist')


def read_branch_info_csv(path):
    with open(path) as f:
        lines = f.read().splitlines()

    info = []
    for line in lines[1:]:
        fields = line.split(';')[1:]

        fds = []
        for i in fields:
            if '.' in i:
                fds.append(float(i))
            else:
                fds.append(int(i))
        fields = fds

        info.append(BranchInfo(*fields))
        # log.debug('fields:', fields)

    log.debug('branch info count:', len(info))
    # pprint(info)
    return info


def read_branch_info_xls(path):
    """
    openpyxl:
    XlsxWriter: https://www.linuxyw.com/464.html
    """
    raise ValueError('Not Implemented')


def read_branch_info(path):
    ext = path.split('.')[-1].lower()
    if ext == 'csv':
        return read_branch_info_csv(path)
    if ext == 'xls':
        return read_branch_info_xls(path)
    raise ValueError('Unsupport format')


def make_graph(info):
    """make graph from branch info

    Arguments:
        info {BranchInfo} -- namedtuple 'id length x y z x2 y2 z2 dist'
    """
    nodes = []
    edges = []
    for fd in info:
        p1 = (fd.x, fd.y)
        p2 = (fd.x2, fd.y2)
        e = p1, p2
        if p1 not in nodes:
            nodes.append(p1)
        if p2 not in nodes:
            nodes.append(p2)
        edges.append(e)

    g = Graph()
    g.add_nodes(nodes)
    g.add_edges(edges)

    # log.debug ('branch graph', len(g), g)
    return g


def correct_direction(info):
    """
    keep direction as left to right, top to bottom
    """
    pass

pix_8_range = [(1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1)]
def get_8_range(pix, p):
    """ range_dict = \
    {0: (1, 0),
     1: (1, -1),
     2: (0, -1),
     3: (-1, -1),
     4: (-1, 0),
     5: (-1, 1),
     6: (0, 1),
     7: (1, 1)
    }
    """
    global pix_8_range
    # x, y =p
    # pixel = pix[x,y]
    indices = (np.array(p) - pix_8_range).tolist()  # get 8 range coordinates
    # log.debug('indices:', indices)
    return [pix[x,y] for x,y in indices]


def scan_skel_data(im, p, p2, scan_direct):

    l = [7,0,1,2,3,4,5,6,7,0]
    def _get_direct(direct):
        """
        3 continual direct code
        """
        i = l.index(direct, 1)
        return l[i-1:i+2]

    ds = _get_direct(scan_direct)
    log.debug('directs:', ds)

    pts = []
    pix = im.load()
    r = get_8_range(pix, p)
    log.debug('pix_8:', r)

    r2 = [r[i] for i in ds]
    log.debug('r2:', r2)


if __name__ == '__main__':

    orig_img_path = './data/AaHeiTi/65E2.bmp'
    skel_img_path = './data/output/AaHeiTi_65E2_skeleton.pgm'
    report_path = './data/output/65E2 Branch information.csv'

    info = read_branch_info(report_path)

    im = cv2.imread(orig_img_path, cv2.IMREAD_GRAYSCALE)
    # log.debug('img shape:', im.shape)
    # log.debug('histogram:', np.histogram(im)[0])
    # log.debug('max min :', im.max(), im.min())

    # !=== calc average_stroke_width = 面积S / 底边b, 即 NPB/NSP
    NPB = np.count_nonzero(im)
    dist_lst = [i.length for i in info]
    NSP = sum(dist_lst)
    average_stroke_width = round(float(NPB) / NSP, 3)
    wrong_stroke_factor = 0.433333333333
    stroke_thresh = wrong_stroke_factor * average_stroke_width
    log.debug('\naverage_stroke_width:', average_stroke_width)
    log.debug('stroke_thresh:', stroke_thresh)

    # !=== sort info
    # info2 = sorted(info, key=lambda item: item.dist)
    # pprint(info2)
    log.debug('\nsorted dist_lst:', sorted(dist_lst))

    # !=== abandon branch shorter than stroke_thresh
    def drop_wrong_branch(branch):
        if branch.length > stroke_thresh:
            return True
        else:
            log.debug('dist=%s, %s droped' % (branch.dist, branch))
            return False
    info3 = filter(drop_wrong_branch, info)
    log.debug('%s branches droped' % (len(info) - len(info3)))

    # skel = cv2.imread(skel_img_path, cv2.IMREAD_GRAYSCALE)
    skel = Image.open(skel_img_path)
    log.debug('skel shape:', skel.size)
    for idx, bi in enumerate(info3):
        log.debug('-- branch', idx)

        # !=== Get direction
        p = bi.x, bi.y
        p2 = bi.x2, bi.y2
        ap = np.array(p)
        ap2 = np.array(p2)
        direct_num = (ap2 - ap)

        def judge_direct(num):
            delta = 6
            if num < -delta:
                return -1
            if num > delta:
                return 1
            return 0
        direct_code = tuple([judge_direct(i) for i in direct_num])

        direct_map = {
            # ( 0,  0): ,  # 'wrong',
            ( 0, -1): 2,  # 'up',
            ( 0,  1): 6,  # 'down',
            (-1,  0): 4,  # 'left',
            (-1, -1): 3,  # 'up left',
            (-1,  1): 5,  # 'down left',
            ( 1,  0): 0,  # 'right',
            ( 1, -1): 1,  # 'up right',
            ( 1,  1): 7,  # 'down right',
        }
        scan_direct = direct_map[direct_code]
        log.debug('direct_code:', direct_code, direct_num, scan_direct)

        # !=== Keep direction as left to right, top to bottom
        pix = skel.load()
        scan_skel_data(skel, p, p2, scan_direct)
