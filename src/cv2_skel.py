#!/usr/bin/env python
# encoding: utf-8

import cv2
import numpy as np
from PIL import Image, ImageDraw
import os
import doctest
from collections import defaultdict, Counter, OrderedDict
from pprint import pprint
from log import Log

log = Log(level=Log.DEBUG)


def get_sys_encoding():
    """
    Get os encoding, i.e. on windows maybe cp396, *nix maybe utf-8
    :return: string of encoding name
    """
    import locale
    import codecs
    return codecs.lookup(locale.getpreferredencoding()).name


def get_console_encoding():
    import sys
    import codecs
    if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
        return codecs.lookup(sys.stdout.encoding).name
    return get_sys_encoding()


# used where non-ascii character may cause chaos
file_encoding = 'utf-8'
sys_encoding = get_sys_encoding()
con_encoding = get_console_encoding()


def enc_sys_to_file(s):
    return unicode(s, sys_encoding).encode(file_encoding)


def enc_file_to_sys(s):
    return unicode(s, file_encoding).encode(sys_encoding)


def get_skel_name(char):
    """
    str(get_skel_name(u'米'))
    7C73_米.pgm
    """
    if not isinstance(char, unicode):
        u = char.decode(file_encoding)
        ch = char
    else:
        u = char
        ch = char.encode(file_encoding)
    return "%04X_%s.pgm" % (ord(u), ch)


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

code_map = OrderedDict(sorted(code_map.items()))


def count_neighbor_pt(arr, p):
    """
    pt num: 1 as end, 2 as connection, 3 or more as junction
    """
    x, y = p
    neighbors = arr[y - 1: y + 2, x - 1:x + 2]
    # log.debug('neighbors:\n', neighbors)
    return np.count_nonzero(neighbors) - 1


def get_8_neighbors(arr, p):
    global code_map
    neighbors = [(p[0] + x, p[1] + y) for x, y in code_map.keys()]
    print('p:', p, neighbors)
    pix_values = [arr[_] for _ in neighbors]
    # log.debug('pix_values:', pix_values)
    return pix_values


# def __get_branch(pts, juncs, ends):
#     i = 0
#     br = []
#     branch_lst = []
#     end_pair = False
#     while i < len(pts):
#         p = pts[i]
#         br.append(p)
#
#         if p in juncs:
#             br = [p]
#             branch_lst.append(br)
#             end_pair = False
#         elif p in ends:
#             if not end_pair:
#                 br = []
#                 branch_lst.append(br)
#         end_pair = not end_pair
#
#         i += 1
#     return branch_lst


# def find_branch_ends(arr):
#     log.debug('arr.shape={}, arr[0,0]={}'.format(arr.shape, arr[0, 0]))
#     h, w = arr.shape
#     x = w - 2
#     y = h - 2
#     ends = dict()
#     while y > 0:
#         while x > 0:
#             p = (x, y)
#             num = count_neighbor_pt(arr, p)
#             if num == 1 or num > 3:
#                 ends[p] = num
#         x = x - 1
#     y = y - 1
#     return ends


def get_branch(cons, im):
    """
    iter cons to distinguish junction and branchs
    :param cons: list of (x,y) seq
    :param im: used for judge triple junctions
    :return: branch list, junction list
    """
    branch_lst = list()
    # junctions = defaultdict(int)
    junctions_map = dict()  # OrderedDict()
    end_lst = list()
    pts = list()

    def set_ends_juncs(k, ends, junc):
        # if k not in junctions:
        #     junctions[k] = 1
        # else:
        #     junctions[k] += 1
        if isinstance(k, list):
            k = tuple(k)
        junctions_map[k] = 1
        end_lst.append(k)

    for i, c in enumerate(cons):

        log.debug('---> con {}, len(con)={}'.format(i, c.shape[0]))

        assert c.ndim == 3 and c.shape[1] == 1, 'cv2 contours shape error'
        c.resize(c.shape[0], 2)
        c = c.tolist()
        # log.debug('len(c)={}'.format(len(c)))
        # log.debug('c:', c)

        p_in_pts = True  # put first pt as junction/ends
        pts.append(c[0])
        for j in range(1, len(c)):
            p = c[j]
            p_prev = c[j - 1]

            t = tuple(p)
            if t in junctions_map:
                junctions_map[t] += 1
                end_lst.append(t)

            if p not in pts:  # unique
                pts.append(p)
                if p_in_pts:  # from repeated to unique pt
                    p_in_pts = False
                    if 2 < count_neighbor_pt(im, p):
                        kp = p
                    else:
                        kp = p_prev
                    set_ends_juncs(kp, end_lst, junctions_map)

            else:  # repeated
                if not p_in_pts:  # from unique to repeated pt
                    p_in_pts = True
                    # test if p is has more than one neighbor in pts
                    # pix_values = get_8_neighbors(im, p)
                    set_ends_juncs(p_prev, end_lst, junctions_map)

            # pts.append(p)

    counter = Counter(junctions_map.values())
    log.debug('len(pts)={}'.format(len(pts)))
    log.debug('junctions:', counter)
    log.debug('end_lst:', end_lst)
    # for jun_pt in junctions:
    #     log.debug('{},'.format(jun_pt))

    ends = []
    juncs = []
    for k, v in junctions_map.items():
        if v == 1:
            ends.append(list(k))
        else:
            juncs.append(list(k))

    indices = sorted([pts.index(list(p)) for p in junctions_map])
    log.debug('indices:', indices)
    for i in range(len(indices) - 1):
        b, e = indices[i], indices[i + 1]
        if e - b == 1:
            log.debug('skip {}: {} - {} == 1'.format(i, e, b))
            continue
        # 由于只记录了一次交叉点，会形成一个 孤立端点 和 分支，跳过它
        if abs(pts[b][0] - pts[e][0]) > 1 or abs(pts[b][0] - pts[e][0]) > 1:
            b += 1
        else:
            e += 1
        branch_lst.append(pts[b:e])

    log.debug('branch_lst:', len(branch_lst), map(len, branch_lst))
    for i in range(len(branch_lst)):
        br = branch_lst[i]
        log.debug('br{}: {} {}'.format(i, br[1], br[-1]))

    return branch_lst, ends, juncs


def img2arr(im):
    return np.fromiter(im.getdata(), dtype=np.uint8)


def arr2img(arr):
    return Image.fromarray(arr, mode='L')


def mark_img(im, ends, juncs):
    """
    draw circle at ends and juncs, see if it's right
    :param im: 2D np.ndarray
    :param ends:
    :param juncs:
    """
    img = arr2img(im)
    img = img.convert('RGB')
    draw = ImageDraw.Draw(img)

    def get_box(p, size=5):
        x, y = p
        bbox = (x - size, y - size, x + size, y + size)
        return tuple(int(round(i)) for i in bbox)

    def label_point(draw, p, linegap=0):
        x, y = p
        draw.text((x - 20, y + linegap), str(p))

    green = '#00ff00'
    red = 'red'
    cnt = 10
    for xy in juncs:
        draw.point(xy, fill=green)
        draw.ellipse(get_box(xy), outline=green)
        label_point(draw, xy, cnt)
        cnt += 10

    for xy in ends:
        draw.point(xy, fill=red)
        draw.ellipse(get_box(xy), outline=red)
        # draw.text(xy, str(xy))
        label_point(draw, xy)
    img.show()


def draw_branch(branches):
    img = Image.new('RGB', (600, 600), 'black')
    draw = ImageDraw.Draw(img)

    def _translate(pt, offset):
        return tuple((pt[0] + offset, pt[1] + offset))

    for i, br in enumerate(branches):

        offset = 0  # 15 * i
        xy = [_translate(p, offset) for p in br]
        fill = '#%06X' % np.random.randint(0, 0xFFFFFF)
        draw.point(xy, fill=fill)

        # apply offset to start of branch and draw
        text_offset = offset + i
        pt = br[-1]
        xy = _translate(pt, text_offset)
        draw.text(xy, str(i), fill=fill)

    img.show(title='Draw Branch')


def __get_branches(cons, im):

    branches = dict()  # (p1, p2) -> list of pts
    ends = []
    indices = []
    # all_pts = []

    for i, c in enumerate(cons):

        log.debug('---> con {}, shape={}'.format(i, c.shape))
        assert c.ndim == 3 and c.shape[1] == 1, 'cv2 contours shape error'
        c.resize(c.shape[0], 2)

        # c = c.tolist()
        c = map(tuple, c.tolist())
        in_pts = False
        pts = []
        for j, q in enumerate(c):

            # 非重复 U，重复 R
            # 一旦由非重复点 U(p) 切换到重复点 R(q)，p 是端点；
            # 反之，一旦由 R(q) 切换到 U(p)，U(p) 是交叉点；
            # 此外，最后一个点无法从 R 切换到 U, 但它是端点；
            # 因此，只要记录下重复的分支段即可
            if q in pts:  # U -> R
                if not in_pts:
                    in_pts = True
                    idx = j-1
                    p = c[idx]
                    ends.append(p)
                    indices.append(idx)
                elif q in ends:
                    ends.append(q)
                    indices.append(j)
                    ends.append(q)
                    indices.append(j)
            else:
                if in_pts:  # R -> U
                    in_pts = False
                    if 2 < count_neighbor_pt(im, q):
                        idx = j
                    else:
                        idx = j-1
                    p = c[idx]
                    ends.append(p)
                    indices.append(idx)
            pts.append(q)

        # Append last point
        if len(ends) % 2 != 0:
            pts.append(c[0])
            idx = len(c)
            p = pts[idx]
            ends.append(p)
            indices.append(idx)

        # Seperate branches
        for i in range(0, len(ends), 2):
            p, q = ends[i:i+2]
            m, n = indices[i:i+2]
            branches[(p, q)] = pts[m:n+1]
            log.debug('{} [{}, {}]'.format(i//2, p, q))

    log.debug('branch ends: %s' % (len(ends)/2.))
    log.debug('branches: %s %s' % (len(branches), map(len, branches.values())))
    return branches


def __get_ends_juncs(branches):
    br_ends = []
    for k in branches.keys():
        br_ends.extend(k)

    cnt = Counter(br_ends)
    ends = []
    juncs = []
    for k, v in cnt.items():
        if v == 1:
            ends.append(k)
        else:
            juncs.append(k)

    log.debug('len(ends) : {}'.format(len(ends)))
    log.debug('len(juncs): {}'.format(len(juncs)))
    return ends, juncs


def main():
    log.debug('cv2 version: {}'.format(cv2.__version__))
    # log.debug('PWD: {}'.format(os.getcwd()))

    dst_dir = 'data/NotoSans'
    char = u"米回既"[0]

    name = get_skel_name(char)
    # name = '1.pgm'
    filename = os.path.join(dst_dir, name)
    filename = filename.decode(file_encoding)

    if not os.path.isfile(filename):
        raise Exception('file <{}> not found'.format(filename))

    im = cv2.imread(filename.encode(sys_encoding), cv2.IMREAD_GRAYSCALE)
    im2 = im.copy()
    r = cv2.findContours(
        im2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cons, hies = r[-2:]

    # ends = find_branch_ends(im)

    # branches, ends, juncs = get_branch(cons, im)
    branches = __get_branches(cons, im)
    ends, juncs = __get_ends_juncs(branches)
    branches = branches.values()

    # mark_img(im, ends, juncs)
    # draw_branch(branches)

    log.debug('done.')


if __name__ == '__main__':
    # doctest.testmod()
    main()
