#!/usr/bin/env python
# encoding: utf-8

import os
from log import Log

log = Log(level=Log.DEBUG)


def get_sys_encoding():
    """
    Get os encoding, i.e. on windows maybe cp396, *nix maybe utf-8
    :return: string of encoding name
    """
    import locale, codecs
    return codecs.lookup(locale.getpreferredencoding()).name


file_encoding = 'utf-8'
sys_encoding = get_sys_encoding()


def main():

    dst_dir = 'data/NotoSans'
    name = u'7C73_米.csv'.encode(sys_encoding)
    filename = os.path.join(dst_dir, name)
    if not os.path.isfile(filename):
        raise Exception('file <{}> not found'.format(filename))

    with file(filename) as f:
        lines = f.readlines()[1:]

    line = lines[0]
    fds = line.split(',')
    log.debug('cols num: {}'.format(len(fds)))

    def _convert(field):
        if '.' not in field:
            return int(field)
        else:
            return float(field)

    data = []
    for line in lines:
        fds = line.split(',')
        data.append([_convert(x) for x in fds[1:10]])
    data.sort(key=lambda info: info[2])
    log.debug('branches info: {}'.format(data))

    for info in data:
        p1 = info[2], info[3]
        p2 = info[5], info[6]
        log.debug('p1={}, p2={}'.format(p1, p2))

    def _count(junctions):
        for j in junctions:
            pass


if __name__ == '__main__':
    main()