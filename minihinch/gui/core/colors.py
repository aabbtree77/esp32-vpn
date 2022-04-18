# colors.py Standard color constants for nano-gui

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2020 Peter Hinch

from color_setup import ssd

# Code can be portable between 4-bit and other drivers by calling create_color
def create_color(idx, r, g, b):
    c = ssd.rgb(r, g, b)
    if not hasattr(ssd, 'lut'):
        return c
    if not 0 <= idx <= 15:
        raise ValueError('Color nos must be 0..15')
    x = idx << 1
    ssd.lut[x] = c & 0xff
    ssd.lut[x + 1] = c >> 8
    return idx

if hasattr(ssd, 'lut'):  # Colors defined by LUT
    BLACK = create_color(0, 0, 0, 0)
    GREEN = create_color(1, 0, 255, 0)
    RED = create_color(2, 255, 0, 0)
    LIGHTRED = create_color(3, 140, 0, 0)
    BLUE = create_color(4, 0, 0, 255)
    YELLOW = create_color(5, 255, 255, 0)
    GREY = create_color(6, 100, 100, 100)
    MAGENTA = create_color(7, 255, 0, 255)
    CYAN = create_color(8, 0, 255, 255)
    LIGHTGREEN = create_color(9, 0, 100, 0)
    DARKGREEN = create_color(10, 0, 80, 0)
    DARKBLUE = create_color(11, 0, 0, 90)
    # 12, 13, 14 free for user definition
    WHITE = create_color(15, 255, 255, 255)
else:
    BLACK = ssd.rgb(0, 0, 0)
    GREEN = ssd.rgb(0, 255, 0)
    RED = ssd.rgb(255, 0, 0)
    LIGHTRED = ssd.rgb(140, 0, 0)
    BLUE = ssd.rgb(0, 0, 255)
    YELLOW = ssd.rgb(255, 255, 0)
    GREY = ssd.rgb(100, 100, 100)
    MAGENTA = ssd.rgb(255, 0, 255)
    CYAN = ssd.rgb(0, 255, 255)
    LIGHTGREEN = ssd.rgb(0, 100, 0)
    DARKGREEN = ssd.rgb(0, 80, 0)
    DARKBLUE = ssd.rgb(0, 0, 90)
    WHITE = ssd.rgb(255, 255, 255)
