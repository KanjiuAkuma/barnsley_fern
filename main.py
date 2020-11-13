"""
Created by Joscha Vack on 10/13/2020.
"""

from tkinter import Tk, Canvas, mainloop
from PIL import Image, ImageTk
import numpy as np

# canvas size
c_width = 1000
c_height = 1000

# number of iterations
n = 100000
draw_n = 100

# render settings
render_offset = np.array([0, c_height / 2 - 100])
render_scale = 80


class Affine:
    def __init__(self, mat: np.array, offset: np.array):
        self._m = mat
        self._o = offset

    def __call__(self, v: np.array):
        return np.dot(self._m, v) + self._o


class BarnsleyFern:
    def __init__(self, affines: list, probabilities: np.array):
        self._affines = affines
        self._probabilities = probabilities

    def next_point(self, previous: np.array):
        ndx = np.random.choice([0, 1, 2, 3], p=self._probabilities)
        return self._affines[ndx](previous), ndx


class Img:
    def __init__(self, width: int, height: int):
        self._data = np.zeros((width, height, 3), dtype=np.uint8)

    def fill(self, pos, alpha, fill=np.array([0, 255, 247], dtype=np.uint8)):
        add = np.array(np.round(alpha * fill), dtype=np.uint8)
        old = self._data[int(pos[1])][int(pos[0])]
        self._data[int(pos[1])][int(pos[0])] = np.min([[255, 255, 255], old + add], axis=0)

    def to_tk(self, root):
        _img = Image.fromarray(self._data)
        return ImageTk.PhotoImage(image=_img, master=root)


if __name__ == '__main__':
    master = Tk()
    canvas = Canvas(master, width=c_width, height=c_height)
    canvas.pack()

    render_at = np.array([c_width, c_height]) / 2 + render_offset

    img = Img(width=c_width, height=c_height)


    def ctx(pos):
        pos = render_at + np.array([pos[0], -pos[1]]) * render_scale
        img.fill(pos=pos, alpha=.3)

    def repaint(raw_img):
        canvas.delete('all')
        render_img = raw_img.to_tk(master)
        canvas.create_image(0, 0, image=render_img, anchor='nw')

        master.update_idletasks()
        master.update()

    affines = [
        Affine(
            mat=np.array([
                [00.00, 00.00],
                [00.00, 00.16]
            ]),
            offset=np.array([00.00, 00.00])
        ),
        Affine(
            mat=np.array([
                [00.85, 00.04],
                [-0.40, 00.85]
            ]),
            offset=np.array([00.00, 01.60])
        ),
        Affine(
            mat=np.array([
                [00.20, -0.26],
                [00.23, 00.22]
            ]),
            offset=np.array([00.00, 01.60])
        ),
        Affine(
            mat=np.array([
                [-0.15, 00.28],
                [00.26, 00.24]
            ]),
            offset=np.array([00.00, 00.44])
        ),
    ]
    probabilities = [
        0.01,
        0.85,
        0.07,
        0.07,
    ]
    fern = BarnsleyFern(affines=affines, probabilities=probabilities)

    max_dist = np.linalg.norm(np.array([c_width, c_height]) / 2.)
    p, ndx = np.array([0, 0]), 0
    for i in range(n):
        ctx(p)
        p, ndx = fern.next_point(previous=p)
        if i % draw_n == 0:
            repaint(img)

    print('finished drawing')
    canvas.delete('all')
    render_img = img.to_tk(master)
    canvas.create_image(0, 0, image=render_img, anchor='nw')
    # keep window open
    mainloop()
