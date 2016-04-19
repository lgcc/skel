#!/usr/bin/env python
# encoding: utf-8

import numpy as np
import cv2
from collections import (Counter, defaultdict)
from pprint import pprint
import json

from log import Log
log = Log(level=Log.DEBUG)

drawing = False  # true if mouse is pressed
mode = True  # if True, draw rectangle. Press 'm' to toggle to curve
ix, iy = -1, -1


def mouseCallBack(event, x, y, flags, params):
    global drawing, mode, ix, iy

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if mode == True:
                cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), -1)
            else:
                cv2.circle(img, (x, y), 5, (0, 0, 255), -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == True:
            cv2.rectangle(img, (ix, iy), (x, y), (0, 255, 0), -1)
        else:
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)


def remove_repeat(cons, nodes=None):
    con = []
    juncs = {}
    total_skipped = 0
    junction_found = 0
    end_found = 0
    # new_cons = []
    for i, c in enumerate(cons):

        if isinstance(c, np.ndarray):
            if c.ndim > 2 and c.shape[1:] == (1, 2):
                c.resize(c.shape[0], 2)
            c = c.tolist()
        # new_cons.extend(c)

        skipped = 0
        for j, p in enumerate(c):

            if not p in con:  # first encounter
                if nodes and nodes.count(p) == 1:  # end
                    juncs[tuple(p)] = 1
                    end_found += 1
                con.append(p)
            elif nodes:
                cnt = nodes.count(p)
                if cnt > 1:  # junction
                    # log.debug(j, 'junction:', p)
                    con.append(p)
                    juncs[tuple(p)] = cnt
                    junction_found += 1

                elif cnt == 1:
                    raise ValueError('1 should have been processed above')

                else:
                    skipped += 1

        total_skipped += skipped
        log.debug(
            i, 'skipped %4s, len(cons[%s])=%s' % (skipped, i, len(cons[i])))
    log.debug('len(con) =', len(con), con[0])
    log.debug('total_skipped=%s, junction_found=%s, end_found=%s' %
              (total_skipped, junction_found, end_found))
    log.debug('juncs:', Counter(juncs.values()))
    return con


def get_nodes(stroke_thresh=None):
    from collections import namedtuple
    BranchInfo = namedtuple('BranchInfo', 'id length x y z x2 y2 z2 dist')

    branch_info = \
        [(1, 290.142, 67, 214, 0, 181, 214, 0, 114),
         (1, 151.828, 67, 301, 0, 67, 452, 0, 151),
            (1, 140.853, 67, 452, 0, 182, 393, 0, 129.252),
            (1, 116.243, 67, 301, 0, 182, 298, 0, 115.039),
            (1, 114, 67, 214, 0, 181, 214, 0, 114),
            (1, 87.828, 67, 214, 0, 67, 301, 0, 87),
            (1, 85.243, 181, 214, 0, 182, 298, 0, 84.006),
            (1, 38.627, 166, 361, 0, 182, 393, 0, 35.777),
            (1, 30.627, 202, 413, 0, 182, 393, 0, 28.284),
            (1, 11.071, 62, 461, 0, 67, 452, 0, 10.296),
            (1, 10.899, 190, 305, 0, 182, 298, 0, 10.63),
            (2, 284.953, 438, 456, 0, 321, 323, 0, 177.138),
            (2, 274.362, 147, 488, 0, 321, 323, 0, 239.794),
            (2, 157.971, 333, 284, 0, 345, 131, 0, 153.47),
            (2, 95.243, 251, 130, 0, 345, 131, 0, 94.005),
            (2, 94.971, 262, 194, 0, 250, 284, 0, 90.796),
            (2, 94.243, 426, 285, 0, 333, 284, 0, 93.005),
            (2, 79.414, 424, 130, 0, 345, 131, 0, 79.006),
            (2, 75.828, 250, 284, 0, 325, 286, 0, 75.027),
            (2, 38.657, 321, 323, 0, 325, 286, 0, 37.216),
            (2, 8.828, 325, 286, 0, 333, 284, 0, 8.246),
            (2, 5.828, 245, 286, 0, 250, 284, 0, 5.385)]

    info = [BranchInfo(*_) for _ in branch_info]
    if stroke_thresh:
        info = filter(lambda x: x.length > stroke_thresh, info)
    nodes = []
    edges = []
    for fd in info:
        p1 = [fd.x, fd.y]
        p2 = [fd.x2, fd.y2]
        e = p1, p2
        edges.append(e)
        nodes.append(p1)
        nodes.append(p2)
    # log.debug('nodes:', len(nodes), nodes)
    return nodes, edges


def divide_branch(con, nodes):
    cons = []
    indices = []
    for i in range(len(con)):
        if con[i] in nodes:
            # log.debug(con[i], 'in indices')
            indices.append(i)
    log.debug('indices:', len(indices), indices)


def test(path):
    im = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    cv2.namedWindow('im')
    cv2.namedWindow('im2')

    last_barPos = -1

    def pos_changed(pos):
        global last_barPos
        if last_barPos != pos:
            last_barPos = pos
            return True

    def find_contours(x):
        if pos_changed(x):
            log.debug('x:', x)

    def nothing(x):
        pass

    switch = '0: CCOMP \n1: TREE \n2: LIST'
    cv2.createTrackbar(switch, 'im', 0, 2, nothing)
    cv2.createTrackbar('Color', 'im2', 0, 255, nothing)
    cv2.createTrackbar('Thickness', 'im2', 0, 30, nothing)

    while 1:
        cv2.imshow('im', im)
        # cv2.imshow('im2', im2)

        k = cv2.waitKey(0) & 0xFF
        if k == 27:
            break
        elif k == 'm':  # toggle mode
            mode = not mode

        pos = cv2.getTrackbarPos(switch, 'im')
        if last_barPos != pos:
            last_barPos = pos
            im2 = im.copy()
            options = [cv2.RETR_CCOMP, cv2.RETR_TREE, cv2.RETR_LIST]
            op = options[last_barPos]
            im2, cons, hies = cv2.findContours(im2, op, cv2.CHAIN_APPROX_NONE)
            log.debug('ret:', len(cons))
            log.debug(
                'option:', ['cv2.RETR_CCOMP', 'cv2.RETR_TREE', 'cv2.RETR_LIST'][last_barPos])
            log.debug('hies:\n', hies)
            log.debug('non_zero:', np.count_nonzero(im), np.count_nonzero(im2))

        color = cv2.getTrackbarPos('Color', 'im2')
        thickness = cv2.getTrackbarPos('Thickness', 'im2')
        cv2.drawContours(im2, cons, -1, color, thickness)
        cv2.imshow('im2', im2)

    cv2.destroyAllWindows()


def _get_branch(cons, nodes, edges):

    def _set_list_start(lst, elems):
        # change start
        for idx in range(len(lst)):
            if lst[idx] in elems:
                break
        if idx > 0:
            lst = lst[idx:] + lst[:idx]
            log.debug('change start to', idx)
        # if not lst[-1] in nodes:
        #     lst.append(lst[0])
        #     log.debug('append start to the end')
        return lst

    new_cons = []
    for c in cons:
        if isinstance(c, np.ndarray):
            if c.ndim > 2 and c.shape[1:] == (1, 2):
                c.resize(c.shape[0], 2)
            c = c.tolist()
            c = _set_list_start(c, nodes)
        new_cons.extend(c)
    log.debug('new_cons[0]:', new_cons[0])

    con = new_cons
    con_num = len(con)
    log.debug('len(con_num):', con_num)

    indices = []
    for i in range(con_num):  # get index of node in con
        p = con[i]
        if p in nodes:
            indices.append(i)

    indices.append(con_num - 1)
    in_edge_cnt = 0

    edge_idx = []
    edge_showed = []
    for i in range(len(indices) - 1):
        b, e = indices[i], indices[i + 1]
        p1, p2 = con[b], con[e]

        s1 = (p1, p2)
        s2 = (p2, p1)
        size = e - b + 1

        # t = ([67, 214], [181, 214])  # circle here
        # if p1 in t:
        #     log.warn('repeated:', p1, p2, size, b, e)

        if s1 in edges and (not (s1, size) in edge_showed):
            in_edge_cnt += 1
            edge_idx.append((b, e + 1))
            edge_showed.append((s1, size))
        elif s2 in edges and (not (s2, size) in edge_showed):
            in_edge_cnt += 1
            edge_idx.append((b, e + 1))
            edge_showed.append((s2, size))

    log.debug('edges=%s, in_edge_cnt=%s' % (len(edges), in_edge_cnt))
    log.debug('indices:', len(indices), indices[0], indices[-1])
    # log.debug('missing edge:', [i for i in edges if not i in edge_showed])
    # pprint(edge_showed)

    branches = []
    for b, e in edge_idx:
        branches.append(con[b:e])
    log.debug('branches:', len(branches))

    return branches


code_map = {
    (-1, -1): 3,
    (-1, 0): 4,
    (-1, 1): 5,
    (0, -1): 2,
    # (0, 0): -1,
    (0, 1): 6,
    (1, -1): 1,
    (1, 0): 0,
    (1, 1): 7,
}


def get_freeman_link(branch, start=None, end=None):
    global code_map
    if not isinstance(branch, np.ndarray):
        branch = np.array(branch)

    if not start:
        start = 0
    if not end:
        end = len(branch)

    linkcode = [code_map[tuple(np.sign(d))] for d in np.diff(branch, axis=0)]
    return linkcode[start:end]


def invert_freeman_code(code):
    """
    return code value representing the opposite direction
    """
    return (code - 4 + 8) % 8


def get_freeman_aver(link):
    if not link:
        return 0, 0
    sx = sy = 0
    for x, y in link:
        sx += x
        sy += y
    return sx / len(link), sy / len(link)


def stats_freeman_link(link):
    """
    return link average and variance(方差)
    """
    pass


def is_link_similiar(l1, l2):
    pass


def _is_close(p1, p2, square_thresh):
    x, y = p1
    x2, y2 = p2
    return (x - x2)**2 + (y - y2)**2 < square_thresh


def _is_same(p1, p2):
    return tuple(p1) == tuple(p2)


def _merge_branch(branches, groups):
    # Get link code
    direct_codes = [get_freeman_link(br) for br in branches]
    aver_codes = [float(sum(br)) / len(br) for br in direct_codes]

    def s_cmp(a, b):
        """
        compress 8-direction to 4 to get simple compare
        """
        return (a % 4) - (b % 4)

    for k in groups:
        lst = groups[k]

        # if len(lst) == 3:

        s_direction = []
        for i, r, _ in lst:
            dr = aver_codes[i]
            if r != 0:  # -1 means should reverse
                dr = invert_freeman_code(dr)
            s_direction.append([dr, i])

        s_direction.sort(key=lambda k: k[0])  # sort from 0 to 7
        # log.debug('s_direction:', s_direction)

        # 计算环形距离
        s_direction.append(s_direction[0])
        l = [dr for dr, _ in s_direction]

        s_dist = []
        for i in range(len(l) - 1):
            dist = abs(l[i + 1] - l[i])
            if dist > 4:
                dist = 8 - dist
            s_dist.append(dist)
        # log.debug('s_dist:', s_dist)

        # 距离最远的分支对应该是一条道上的
        max_idx = 0
        max_val = 0
        for i in range(len(s_dist)):
            if max_val < s_dist[i]:
                max_val = s_dist[i]
                max_idx = i
        br1 = s_direction[max_idx][1]
        br2 = s_direction[max_idx + 1][1]
        log.debug("max_idx=%s, br1=%02s, br2=%02s, max_val=%s" %
                  (max_idx, br1, br2, max_val))

        # if len(lst) == 5:
        #     pass

    return None


def _in_merge_branch(branches, exam_branches, indices, square_thresh, directs):

    log.debug('length check:', len(branches), len(exam_branches), len(indices))

    # Calc direction codes
    aver_map = []
    for i, br in zip(indices, exam_branches):
        link = get_freeman_link(br)
        aver = 1.0 * sum(link) / len(link)
        aver_map.append([aver, i])
    aver_map.sort(key=lambda x: x[0])
    log.debug('aver_map:', aver_map)

    # Calc loop-distance
    aver_map.append(aver_map[0])
    aver_dists = []
    for i in range(len(aver_map) - 1):
        a, b = aver_map[i][0], aver_map[i + 1][0]
        dist = abs(a - b)
        if dist > 4:  # in 8 length circle, fastest dist is 4
            dist = 8 - dist
        aver_dists.append(dist)
    # log.debug('aver_dists:', aver_dists)

    # Fartest distance, plus dist > 2, should be comprised
    max_idx = 0
    max_val = 0
    for i in range(len(aver_dists)):
        if max_val < aver_dists[i]:
            max_val = aver_dists[i]
            max_idx = i

    br1 = aver_map[max_idx][1]
    br2 = aver_map[max_idx + 1][1]
    aver_map.pop()
    log.debug("max_idx=%s, br1=%02s, br2=%02s, max_val=%s" %
              (max_idx, br1, br2, max_val))

    # 2 is half dist of 4(which is a fartest dist in a loop of length 8)
    if max_val < 2:
        log.debug('Stop combination at condition max_val < 2')
        return

    if len(branches) < 2:
        log.debug('Stop combination at condition len(branches) < 2')
        return

    m = min(br1, br2)
    n = max(br1, br2)

    t, t2 = max_idx, (max_idx + 1) % len(exam_branches)
    t, t2 = min(t, t2), max(t, t2)

    d2 = - directs.pop(t2)
    d1 = directs.pop(t)
    branches.append(branches[m][::d1] + branches[n][::d2])

    branches.pop(n)
    branches.pop(m)

    exam_branches.pop(t2)
    exam_branches.pop(t)

    indices.pop(t2)
    indices.pop(t)

    if len(exam_branches) > 2:
        _in_merge_branch(
            branches, exam_branches, indices, square_thresh, directs)


def merge_branch(branches, junctions, start, end, square_thresh):
    if not junctions:
        return
    junc = junctions[-1]
    exam_branches = []
    exam_indices = []
    directs = []

    for i, br in enumerate(branches):

        b, e = br[0], br[-1]
        if _is_close(b, junc, square_thresh):  # 靠近头
            nbr = br[start:end]
            exam_branches.append(nbr)
            exam_indices.append(i)
            directs.append(1)
            if not nbr:
                log.error(i, 'A empty nbr', len(br))

        elif _is_close(e, junc, square_thresh):  # 靠近尾
            directs.append(-1)
            nbr = br[-end - 1: len(br) - start]
            exam_branches.append(nbr)
            exam_indices.append(i)
            if not nbr:
                log.error(i, 'B empty nbr', len(br))

    if len(exam_branches) > 1:
        log.debug('Process:', len(junctions) - 1)
        _in_merge_branch(
            branches, exam_branches, exam_indices, square_thresh, directs)
    else:
        log.debug('Skip:', len(junctions) - 1)

    # 尾递归，继续处理下一个交叉点
    merge_branch(branches, junctions[:-1], start, end, square_thresh)


def main(path):
    im = cv2.imread(skel_path, cv2.IMREAD_GRAYSCALE)
    im2 = im.copy()
    if cv2.__version__.startswith('2'):
        cons, hies = cv2.findContours(im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    else: #if cv2.__version__.startswith('3'):
        im2, cons, hies = cv2.findContours(im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    average_stroke_width = 30
    stroke_thresh = 14
    dist_thresh = 14
    square_thresh = dist_thresh ** 2

    nodes, edges = get_nodes(stroke_thresh)
    # single_con = remove_repeat(cons, nodes)
    # divide_branch(single_con, nodes)

    branches = _get_branch(cons, nodes, edges)
    # json.dump(branches, file('./data/output/json/xx.json', 'wb'))

    # Show image to tell if it's right
    # from display import display_sep, display_multi
    # plt = display_sep(branches)
    # plt.show()

    # Mark branch whose ends are equal or close to each other
    # Find junctions, if a node show more than once, there's junction
    ns = map(tuple, nodes)
    ns_cnt = Counter(ns)
    ns_stats = Counter(ns_cnt.values())

    junctions = filter(lambda k: ns_cnt[k] > 1, ns_cnt)
    log.debug('nodes stats:', ns_stats)
    log.debug('junctions:', len(junctions))  # , '\njunctions:', junctions[0])

    # ToDo: Break up branch where it has obvious corner
    # ToDo: Check junction with shape image; correct distorted branch

    # Walk through junction, find branch close to it, storing as: junction ->
    # list
    groups = defaultdict(list)
    for n in junctions:
        for i, br in enumerate(branches):
            b, e = br[0], br[-1]
            if _is_close(n, b, square_thresh):
                groups[n].append((i, 0, b))
            elif _is_close(n, e, square_thresh):
                groups[n].append((i, -1, e))
    log.debug('groups:', len(groups), Counter(
        [len(v) for v in groups.values()]))
    # pprint (groups.items())

    for k, v in groups.items():
        if groups.values().count(v) > 1:
            del groups[k]
    log.debug('groups (uniqued):', Counter([len(v) for v in groups.values()]))

    # Until now, I have branch, branch group indices
    # Time for similiar freeman code link

    # ToDo: seperate single branch first by any condition below
    #  a. branch with two ends(no junction shows up)
    #  b. branch start point == end point (like a circle)

    start, end = stroke_thresh, int(average_stroke_width * 1.5)
    merge_branch(branches, junctions, start, end, square_thresh)

    log.debug('branches:', len(branches))
    json.dump(branches, file('./data/output/json/xx.json', 'wb'))


if __name__ == '__main__':
    # skel_path = './data/output/AaHeiTi_4FEB_skeleton.pgm'
    skel_path = './data/output/AaHeiTi_65E2_skeleton.pgm'

    main(skel_path)
