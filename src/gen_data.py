#!/usr/bin/python
# encoding: utf-8

from __future__ import print_function
from PIL import Image, ImageDraw, ImageFont
from os.path import dirname, splitext, exists, isdir
import os

# import functools
# print = functools.partial(print, file=os.sys.stderr)


def gen_glyph_bmp(ttf_path, code_char, outpath=None):
    font = ImageFont.truetype(ttf_path, 484)
    if font:
        if isinstance(code_char, str):
            chars = unicode(code_char, 'utf-8')
        elif isinstance(code_char, int):
            chars = [unichr(code_char)]
        else:
            print ('wrong arg in <gen_glyph_bmp>')
            return None

        bkg_clr, fgr_clr = 0, 255
        # bkg_clr, fgr_clr = 255, 0
        for char in chars:
            # w, h = font.getsize(char)
            # img = Image.new('L', (w+10,h+10), bkg_clr)

            img = Image.new('L', (1000,1000), bkg_clr)
            draw = ImageDraw.Draw(img)
            draw.text((100, 100), char, font=font, fill=fgr_clr)

            bbox = img.getbbox()
            # print('bbox=', bbox)

            if 0x4E00 <= ord(char) <= 0x9FA5:
                margins = (-40,-60, 40, 60)
            else:
                margins = (-30,-70, 30, 70)  # left, upper, right, lower
            crop_box = [p + m for p, m in zip(bbox, margins)]
            img = img.crop(crop_box)

            if not outpath:
                outpath = splitext(ttf_path)
            if not exists(outpath):
                os.mkdir(outpath)
            elif not isdir(outpath):
                print('%s not a path' % outpath, file=os.sys.stderr)

            # Our image it not binary due to antialiasing in the font,
            # however, Fiji Skeleton3D needs 8-grey scale image
            # so we use method belowe to get "binary 8-grey" image
            img = img.convert('1').convert('L')

            img.save(outpath + os.sep + '%04X' % ord(char) + '.bmp')
        return chars


def convert_binary(filename, out=False):
    im = Image.open(path)
    im = im.convert('L')
    im = im.convert('1')
    if out:
        im.save(path[:path.rindex('.')] + '.bmp')


if __name__ == '__main__':

    # path = '../../data/skel.bmp'

    # im = Image.new('1', (5,5), 255)
    # draw = ImageDraw.Draw(im)
    # draw.line((2,1, 2,3), fill=0, width=1)
    # im.show()
    # path = '../../data/tiao-shape.png'

    char_string = "十任既龝条米"
    fontfile = "/Users/xm012/Documents/proj/cpp/ksingle/fonts/AaHeiTi.ttf"
    outpath='./data/AaHeiTi'
    chars = gen_glyph_bmp(fontfile, char_string, outpath=outpath)

    if chars:
        for c, u in zip(char_string.decode('utf-8'), chars):
            print(c.encode('utf-8'), '%04X.bmp' % ord(u))

    # gen_glyph_bmp('/Users/xm012/Library/Fonts/字体管家仿宋简v1.1.ttf',
    #     'AMP条既',
    #     './data/AaFangSong')

    print('Done.')