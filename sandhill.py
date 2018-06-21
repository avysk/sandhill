"""
Sandhill emulation
"""
import math
import os.path
from random import randint

import numpy as np
import pygame as pg
import pygame.freetype as ft
import pygame.locals as lcls

from pygame import surfarray as sf

SIZE = 300
ZOOM = 1900 // SIZE
HILL = 20

WAIT = True

EVERY = 12000
FOR = 240


def _interesting(num):
    return num % EVERY <= FOR


def _update(field, border, colors):
    added = False
    if (not WAIT) or (field < 4).all():
        max_val = field.shape[0] - 1 - border
        # add one more
        rand_x = randint(border, max_val)
        rand_y = randint(border, max_val)
        field[rand_x, rand_y] += 1
        added = True
    # which ones are exploding
    explode = field >= 4
    explode = explode * 1
    field[field >= 4] -= 4
    # now do the explosion
    field[1:, :] += explode[:-1, :]
    field[:-1, :] += explode[1:, :]
    field[:, 1:] += explode[:, :-1]
    field[:, :-1] += explode[:, 1:]

    colors[:, :, 0] = (field == 3) * 255 + (field >= 4) * 255
    colors[:, :, 1] = (field == 1) * 255 + (field >= 4) * 255
    colors[:, :, 2] = (field == 2) * 255 + (field >= 4) * 255

    return added


# pylint:disable=too-many-locals
def main(size, border, zoom):
    """Entry point."""
    # pylint:disable=no-member
    pg.init()

    font = ft.Font("iosevka-regular.ttf")

    field = np.zeros((size, size), dtype=int)
    colors = np.zeros((size, size, 3), dtype=int)
    screen = pg.display.set_mode((size * zoom, size * zoom), 0, 24)
    # pylint:disable=too-many-function-args
    surface = pg.Surface((size, size))
    idx = 1
    frame = 1
    grains = 0
    while True:
        evt = pg.event.poll()
        # pylint:disable=no-member
        # if evt.type == lcls.KEYDOWN and evt.key == lcls.K_SPACE:
        # pylint:disable=no-member
        if evt.type == lcls.QUIT:
            raise SystemExit()
        if _update(field, border, colors):
            grains += 1
        idx += 1
        if idx % 1000 == 0:
            size2 = size * size
            filled = np.count_nonzero(colors) * 100 / size2
            red = np.count_nonzero(colors[:, :, 0]) * 100 / size2
            green = np.count_nonzero(colors[:, :, 1]) * 100 / size2
            blue = np.count_nonzero(colors[:, :, 2]) * 100 / size2
            print("{} ({}): {:.2f}% -> "
                  "{:.2f}% / {:.2f}% / {:.2f}%".format(idx, grains,
                                                       filled,
                                                       red, blue, green))
        if _interesting(grains):
            sf.blit_array(surface, colors)
            font.render_to(surface, (10, 10), "{}".format(grains),
                           fgcolor=(0, 255, 255),
                           size=12)
            pg.image.save(surface,
                          os.path.join("out", "out-{:09d}.png").format(frame))
            frame += 1
            # pg.transform.smoothscale(surface,
            #                         (size * zoom, size * zoom), screen)
            pg.transform.scale(surface, (size * zoom, size * zoom), screen)
            pg.display.flip()


if __name__ == '__main__':
    main(SIZE, (SIZE - HILL) // 2, ZOOM)
