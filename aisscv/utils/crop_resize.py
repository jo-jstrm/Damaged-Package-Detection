#!/usr/bin/env python
"""Resize the image to given size.
Don't strech images, crop and center instead.
Adapted from https://gist.github.com/zed/4221180
"""
import os
import sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from fractions import Fraction
from functools import partial
from multiprocessing import Pool

from PIL import Image # $ sudo apt-get install python-imaging

def crop_resize(image, size, ratio):
    # crop to ratio, center
    w, h = image.size
    if w > ratio * h: # width is larger then necessary
        x, y = (w - ratio * h) // 2, 0
    else: # ratio*height >= width (height is larger)
        x, y = 0, (h - w / ratio) // 2
    image = image.crop((x, y, w - x, h - y))

    # resize
    if [w,h] > size: # don't stretch smaller images
        image.thumbnail(size, Image.ANTIALIAS)
    return image

def crop_resize_mp(input_dir, outputdir, size, ratio):    
    for input_filename in os.listdir(input_dir):
        if input_filename.endswith(".jpg") or input_filename.endswith(".png"):            
            image = crop_resize(Image.open(os.path.join(input_dir, input_filename)),
                                                                        size, ratio)
            # save resized image
            basename, ext = os.path.splitext(os.path.basename(input_filename))
            output_basename = basename + ("_%dx%d" % tuple(size)) + ext
            output_filename = os.path.join(outputdir, output_basename)
            image.save(output_filename)        

def main():
    # parse command-line arguments
    parser = ArgumentParser(description=__doc__,
        formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-s', '--size', type=int, nargs=2,
                        default=[480, 480], metavar='N',
                        help='new image size')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('--outputdir', default=os.curdir, metavar='DIR',
                        help='directory where to save resized images')
    parser.add_argument('--files', type=str,
                        help='image filenames to process')
    args = parser.parse_args()

    # crop, resize using multiple processes    
    crop_resize_mp(input_dir=args.files, outputdir=args.outputdir, size=args.size,
                ratio=Fraction(*args.size))    

if __name__ == "__main__":
    main()