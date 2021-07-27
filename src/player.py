#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Helio Perroni Filho
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

r'''Multiple video player.

    Author: Helio Perroni Filho
'''


import av
import cv2
import numpy as np

import logging
from argparse import ArgumentParser
from math import ceil
from multiprocessing import Process, Queue
from time import time


def parseArguments():
    r'''Parse command-line arguments.
    '''
    parser = ArgumentParser(description='Video player that can reproduce multiple files simultaneoulsy')
    parser.add_argument('paths', nargs='+', help='Paths to the video files to be played')
    parser.add_argument('--resolution', type=int, nargs=2, default=[1920, 1080], help='Resolution of the combined video')
    parser.add_argument('--fps', type=int, default=15, help='Frame rate used when playing video contents')

    return parser.parse_args()


def decode(path, width, height, queue):
    r'''Decode a video and return its frames through a process queue.

        Frames are resized to `(width, height)` before returning.
    '''
    container = av.open(path)
    for frame in container.decode(video=0):
        # TODO: Keep image ratio when resizing.
        image = frame.to_rgb(width=width, height=height).to_ndarray()
        queue.put(image)

    queue.put(None)


class GridViewer(object):
    r'''Interface for displaung video frames in a grid pattern.
    '''
    def __init__(self, args):
        r'''Create a new grid viewer.
        '''
        size = float(len(args.paths))
        self.cols = ceil(size ** 0.5)
        self.rows = ceil(size / self.cols)

        (width, height) = args.resolution
        self.shape = (height, width, 3)

        self.cell_width = width // self.cols
        self.cell_height = height // self.rows

        cv2.namedWindow('Video', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
        cv2.resizeWindow('Video', width, height)

    def update(self, queues):
        r'''Query the frame queues and update the viewer.

            Return whether all decoders are still active.
        '''
        grid = np.zeros(self.shape, dtype=np.uint8)
        for (k, queue) in enumerate(queues):
            image = queue.get()
            if image is None:
                return False

            (i, j) = (k // self.cols, k % self.cols)
            (m, n) = image.shape[:2]

            a = i * self.cell_height
            b = a + m

            c = j * self.cell_width
            d = c + n

            grid[a:b, c:d] = image

        grid = cv2.cvtColor(grid, cv2.COLOR_RGB2BGR)
        cv2.imshow('Video', grid)
        cv2.waitKey(1)

        return True


def play(args):
    r'''Play multiple video files in a grid interface.
    '''
    grid = GridViewer(args)

    queues = []
    processes = []
    for path in args.paths:
        queues.append(Queue(1))
        processes.append(Process(target=decode, args=(path, grid.cell_width, grid.cell_height, queues[-1]), daemon=True))
        processes[-1].start()

    period = 1.0 / args.fps
    t_start = time()
    t_frame = 0

    while grid.update(queues):
        # Spin-lock the thread as necessary to maintain the frame rate.
        while t_frame > time() - t_start:
            pass

        t_frame += period

    # Terminate any lingering processes, just in case.
    for process in processes:
        process.terminate()


def main():
    logging.disable(logging.WARNING)

    play(parseArguments())


if __name__ == '__main__':
    main()
