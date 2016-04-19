#!/usr/bin/env python
# encoding: utf-8

from PIL import Image, ImageDraw, ImageFont
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


def font_2_img(chars, path, dst_dir):
    if not os.path.isfile(path):
        raise Exception('no font file exist')

    fg, bg = 255, 0
    pt_size = 400
    w = h = 400

    file_encoding = 'utf-8'
    uni_chars = chars.decode(file_encoding)

    for ch in uni_chars:
        im = Image.new('L', (w, h), bg)
        draw = ImageDraw.Draw(im)
        font = ImageFont.truetype(path, size=pt_size)

        size = draw.textsize(ch, font)
        # im = im.resize(size)

        c = ch.encode(file_encoding)
        draw.text((0, 0), ch, fill=fg, font=font)

        im = im.convert('1').convert('L')

        out_name = ("%04X_%s.bmp" % (ord(ch), ch))
        im.save(os.path.join(dst_dir, out_name))

        log.debug(ch, 'size:', size)


if __name__ == '__main__':
    dst_dir = './data/NotoSans'
    chars = "米回既"
    path = '../../../_ccData/NotoSansHans-Regular.otf'

    font_2_img(chars, path, dst_dir)
