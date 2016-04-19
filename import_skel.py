#!/usr/bin/env python
# encoding: utf-8
"""
run in fontlab, import json-style skel data to glyphs
"""
from __future__ import print_function
import os
import json


class Log(object):
    DEBUG, INFO, WARN, ERROR = 1, 2, 3, 4
    debug = info = None

    def __init__(self, level=None):
        if level == None:
            level = Log.INFO
        d = {False: lambda *arg: None, True: self._print}
        self.debug = d[level <= Log.DEBUG]
        self.info = d[level <= Log.INFO]
        self.warn = d[level <= Log.WARN]
        self.error = d[level <= Log.ERROR]

    def _print(self, *arg, **kw):
        print(*arg, **kw)


log = Log(level=Log.DEBUG)


# def get_sys_encoding():
#     """
#     get os encoding, i.e. on windows maybe cp396, *nix maybe utf-8
#     :return: string of encoding name
#     """
#     import locale, codecs
#     return codecs.lookup(locale.getpreferredencoding()).name


pt_size = 484
scale = float(fl.font.upm) / 484
offset = 850
matrix = Matrix(scale, 0, 0, -scale, 0, offset)


def transform(g):
    global matrix
    g.Transform(matrix)


def main():
    # sys_encoding = get_sys_encoding()
    # file_encoding = 'utf-8'

    macro_path = os.path.join(fl.userpath, 'Macros')
    pwd = os.path.join(macro_path, 'Skel')
    os.chdir(pwd)

    name = 'xx.json'
    path = 'src/data/output/json'

    filename = os.path.join(path, name)

    with open(filename) as f:
        segs = json.load(f)

    g = fl.glyph
    idx = fl.iglyph

    fl.SetUndo(idx)
    # add pts to glyph
    ns = list()
    for pts in segs:
        ns.append(Node(0x8011, Point(*pts[0])))
        for i in range(1, len(pts)):
            ns.append(Node(nLINE, Point(*pts[i])))
        g.Add(ns)
        ns[:] = []

    # optimize to reduce pts
    nodes_num = 0
    loop_cnt = 0
    while len(g) != nodes_num:
        nodes_num = len(g)
        loop_cnt += 1
        fl.CallCommand(fl_cmd.ActionOptimize)

    transform(g)

    fl.UpdateGlyph(idx)

    cons_num = g.GetContoursNumber()
    log.debug('contours=%s, loop_count=%s' % (cons_num, loop_cnt))


if __name__ == '__main__':
    main()
