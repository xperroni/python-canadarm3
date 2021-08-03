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

import csv
import logging
import os
from glob import glob
from itertools import chain, product, repeat
from math import ceil
from multiprocessing import Process, Queue
from time import time


def decode(path, width, height, queue):
    r'''Decode a video and return its frames through a process queue.

        Frames are resized to `(width, height)` before returning.
    '''
    container = av.open(path)
    for frame in container.decode(video=0):
        image = frame.to_ndarray(width=width, height=height, format='bgr24')
        queue.put(image, timeout=1.0)

    queue.put(None, timeout=1.0)


class VideoGrid(object):
    r'''Interface for retrieving trial video frames in a grid pattern.
    '''
    def __init__(self, path_trial):
        r'''Create a new trial player.
        '''
        with open(os.path.join(path_trial, 'collisions.csv'), 'r') as collisions_data:
            self.collisions = [(int(row[0]), row[1] == 'True') for row in csv.reader(collisions_data)]

        self.paths = sorted(glob(os.path.join(path_trial, '*.mp4')))

        # Extract resolution and FPS from first video in the sequence.
        container = av.open(self.paths[0])
        video = container.streams.video[0]
        self.fps = round(video.guessed_rate)
        self.width = video.width
        self.height = video.height
        container.close()

        size = float(len(self.paths))
        self.cols = ceil(size ** 0.5)
        self.rows = ceil(size / self.cols)

        self.shape = (self.height, self.width, 3)

        canvas_width = self.width - self.cols - 1
        canvas_height = self.height - self.rows - 1

        scale = max(self.rows, self.cols)
        self.scaled_width = canvas_width // scale
        self.scaled_height = canvas_height // scale

        self.cell_width = canvas_width // self.cols
        self.cell_height = canvas_height // self.rows

    def play(self):
        r'''Iterate over the trial videos, returning their frames collated in a grid pattern.
        '''
        queues = []
        processes = []
        for path in self.paths:
            queues.append(Queue(1))
            decode_args = (path, self.scaled_width, self.scaled_height, queues[-1])
            processes.append(Process(target=decode, args=decode_args, daemon=True))
            processes[-1].start()

        for (frame_index, collides) in chain(self.collisions, repeat((-1, False))):
            grid = np.zeros(self.shape, dtype=np.uint8)
            if frame_index < 0:
                pass
            elif collides:
                grid[:, :] = (0, 0, 255)
            else:
                grid[:, :] = (255, 0, 0)

            done = True

            for (i, j) in product(range(self.rows), range(self.cols)):
                cell_i = 1 + i * (1 + self.cell_height)
                cell_j = 1 + j * (1 + self.cell_width)

                cell_u = cell_i + self.cell_height
                cell_v = cell_j + self.cell_width

                grid[cell_i:cell_u, cell_j:cell_v] = (0, 0, 0)

                k = i * self.cols + j
                if k >= len(queues):
                    continue

                queue = queues[k]
                if queue is None:
                    continue

                image = queue.get(timeout=1.0)
                if image is None:
                    queues[k] = None
                    continue

                (m, n) = image.shape[:2]
                cell_m = cell_i + m
                cell_n = cell_j + n

                grid[cell_i:cell_m, cell_j:cell_n] = image

                done = False

            if done:
                return

            yield grid

    def save(self, path):
        r'''Create a new video out of the collated frames.
        '''
        output = av.open(path, 'w')
        stream = output.add_stream('h264', 15)
        stream.bit_rate = 2 ** 9 * 1000
        stream.pix_fmt = 'yuv420p'
        stream.width = self.width
        stream.height = self.height

        for image in self.play():
            frame = av.VideoFrame.from_ndarray(image, format='bgr24')
            packet = stream.encode(frame)
            output.mux(packet)

        output.close()

    def show(self):
        r'''Play multiple video files in a grid interface.
        '''
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO | cv2.WINDOW_GUI_EXPANDED)
        cv2.resizeWindow('Video', self.width, self.height)

        period = 1.0 / self.fps
        t_start = time()
        t_frame = 0

        for frame in self.play():
            cv2.imshow('Video', frame)
            cv2.waitKey(1)

            # Spin-lock the thread as necessary to maintain the frame rate.
            t_k = t_start + t_frame
            while time() < t_k:
                pass

            t_frame += period


def main():
    from sys import argv

    logging.disable(logging.WARNING)

    player = VideoGrid(argv[1])
    player.show()


if __name__ == '__main__':
    main()
