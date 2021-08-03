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

r'''Utility classes for downloading and manipulating datasets.

    Author: Helio Perroni Filho
'''


import av
import numpy as np
from scipy.io import loadmat

import opendatasets as od
from opendatasets.utils.kaggle_direct import get_kaggle_dataset_id

import csv
import logging
import os
from glob import glob
from math import isnan
from re import search
from shutil import copy, move, rmtree


def mkdir(path):
    r'''Create the given path if it doesn't exist yet.

        Do nothing otherwise.
    '''
    if not os.path.exists(path):
        os.makedirs(path)


def find(path, *entries):
    r'''Search recursively the given path for the given entries, returning found paths.
    '''
    for entry in entries:
        for path_found in glob(os.path.join(path, '**', entry), recursive=True):
            yield path_found


class Video(object):
    r'''Video file access utilities.
    '''
    def __init__(self, path):
        r'''Create a new video file interface object.
        '''
        self.path = path
        self.container = av.open(path)
        self.frame_period = 1.0 / round(self.container.streams.video[0].guessed_rate)

    def __repr__(self):
        r'''Return a string representation of the video file.
        '''
        return "'%s'" % self.path

    def __getitem__(self, index):
        r'''Return the frame of given index from the video file.

            See: https://gitter.im/PyAV-Org/User-Help?at=5db7d634e886fb5aa214c3b3
        '''
        self.seek(index)
        for frame in container.decode(video=0):
            if frame.pts >= offset:
                return np.array(frame.to_image())

        raise Exception('Frame #%d not found in video "%s" (frame count = %d)' % (index, self.path, self.frame_count))

    def seek(self, index):
        r'''Set the current video frame to the given index.

            See: https://gitter.im/PyAV-Org/User-Help?at=5db7d634e886fb5aa214c3b3
        '''
        container = self.container
        video_stream = container.streams.video[0]
        offset = int(index * self.frame_period / video_stream.time_base)
        container.seek(offset=offset, stream=video_stream)

    def save(self, path, frame_start, frame_end):
        r'''Save a segment of the video file to disk.

            See: https://pyav.org/docs/stable/cookbook/basics.html#remuxing
        '''
        if frame_end is None:
            frame_end = self.frame_count

        input_container = self.container
        input_stream = input_container.streams.video[0]
        n = int(frame_end * self.frame_period / input_stream.time_base)

        output_container = av.open(path, mode='w')
        output_stream = output_container.add_stream(template=input_stream)

        dts_0 = None
        pts_0 = None
        self.seek(frame_start)
        for packet in input_container.demux(input_stream):
            # We need to skip the "flushing" packets that demux() generates.
            if packet.dts is None:
                continue

            if packet.pts > n:
                break

            packet.stream = output_stream

            if dts_0 is None:
                dts_0 = packet.dts
                pts_0 = packet.pts
                packet.dts = 0
                packet.pts = 0
            else:
                packet.dts -= dts_0
                packet.pts -= pts_0

            output_container.mux(packet)

        output_container.close()

    @property
    def frame_count(self):
        r'''Return the total frame count of the video file.
        '''
        return self.container.streams.video[0].frames


class Attributes(dict):
    r'''Dictionary that allows entries to be accessed as attributes.
    '''
    def __getattr__(self, name):
        r'''Return the given entry as an attribute.
        '''
        return self[name]


class Samples(Attributes):
    r'''Sample data.
    '''
    def __init__(self, id, time_start, path, frame_start, frame_end):
        r'''Create a new sample data object.
        '''
        video = Video(path)

        frame_start = int(frame_start) if not isnan(frame_start) else 0
        frame_end = int(frame_end) if not isnan(frame_end) else video.frame_count

        time_end = time_start + (frame_end - frame_start) * video.frame_period

        self['id'] = id
        self['video'] = video
        self['frames'] = (frame_start, frame_end)
        self['times'] = (time_start, time_end)


class Trial(object):
    r'''Camera data collected over the course of a trial.
    '''
    def __init__(self, id):
        r'''Create a new trial data object.
        '''
        self.id = id
        self.samples = {}
        self.collisions = []


class Dataset(object):
    r'''Dataset metadata and content interface.
    '''
    def __init__(self, id):
        r'''Create a new dataset object.
        '''
        self.id = id
        self.trials = {}
        self.__path = '../data'

    @property
    def path(self):
        r'''Return the path to the base directory of the pre-processed dataset.
        '''
        return os.path.join(self.__path, 'sessions', self.id)

    def __copy(self, src, dst):
        try:
            copy(src, dst)
        except Exception as e:
            print(e)

    def save(self, path=None):
        r'''Save dataset data to the file system.
        '''
        if path is not None:
            self.__path = path

        path_raw = os.path.join(self.__path, 'raw', self.id)
        path_trials = self.path
        mkdir(path_trials)

        self.__copy(os.path.join(path_raw, 'Robot_Input', 'start_data.txt'), path_trials)

        for trial in self.trials.values():
            print('Saving trial #%d...' % trial.id)

            id = trial.id
            path_trial = os.path.join(path_trials, '%02d' % id)
            os.mkdir(path_trial)

            with open(os.path.join(path_trial, 'collisions.csv'), 'w') as collision_data:
                writer = csv.writer(collision_data)
                for collision in trial.collisions:
                    writer.writerow(collision)

            #self.__copy(os.path.join(path_raw, 'Collision_Data', 'Trial%d.csv' % id), os.path.join(path_trial, 'collisions.csv'))
            self.__copy(os.path.join(path_raw, 'Robot_Input', 'Parsed_Logs', 'Parsed_Logs%d.csv' % id), os.path.join(path_trial, 'logs.csv'))
            self.__copy(os.path.join(path_raw, 'Robot_Input', 'Parsed_PoseUpdates', 'Parsed_PoseUpdates%d.csv' % id), os.path.join(path_trial, 'poses.csv'))
            self.__copy(os.path.join(path_raw, 'Robot_Input', 'Parsed_Telem', 'Parsed_Telem%d.csv' % id), os.path.join(path_trial, 'telemetry.csv'))

            for sample in trial.samples.values():
                (frame_start, frame_end) = sample.frames
                sample.video.save(os.path.join(path_trial, 'camera_%02d.mp4' % sample.id), frame_start, frame_end)

        print('Done.')

    def trial(self, id):
        r'''Return a trial of given ID, creating it if not found.
        '''
        trials = self.trials
        if id not in trials:
            trials[id] = Trial(id)

        return trials[id]


class Robot(object):
    r'''data about the robot.
    '''
    def __init__(self, path):
        r'''Create a new robot data object.
        '''
        with open(os.path.join(path, 'start_data.txt'), 'r') as start_data:
            self.start_times = [float(row['Start Times:']) for row in csv.DictReader(start_data)]


def sortMetadata(path):
    r'''Sorting function used to retrieve metadata files in the right order.
    '''
    return int(search(r'(\d+)\.mat', path).group(1))


class Download(object):
    r'''Logic for downloading raw datasets.
    '''
    def __init__(self, id, *links):
        r'''Create a new download object for the given session.
        '''
        self.id = id
        self.links = links
        self.__path = '../data'

    @property
    def path(self):
        r'''Return the path to the base directory of the downloaded dataset.
        '''
        return os.path.join(self.__path, 'raw', self.id)

    def parts(self):
        r'''Return the ID's and URL's of dataset parts in Kaggle.
        '''
        for part_url in self.links:
            part_id = get_kaggle_dataset_id(part_url).split('/')[1]
            yield (part_id, part_url)

    def download(self, path=None):
        r'''Download a raw dataset session.
        '''
        if path is not None:
            self.__path = path

        if os.path.exists(self.path):
            return

        path_download = os.path.join(self.__path, 'download')
        mkdir(path_download)
        mkdir(self.path)

        for (part_id, part_url) in self.parts():
            part_path = os.path.join(path_download, part_id)
            if not os.path.exists(part_path):
                od.download(part_url, data_dir=path_download)

            for path_data in find(part_path, 'Camera*', 'Collision_Data', 'Processing_Data', 'Robot_Input'):
                if os.path.isdir(path_data):
                    move(path_data, self.path)

        rmtree(path_download)

    def load(self, path=None):
        r'''Load a new dataset object from downloaded data.
        '''
        if path is not None:
            self.__path = path

        path = os.path.abspath(self.path)
        robot = Robot(os.path.join(path, 'Robot_Input'))

        dataset = Dataset(self.id)

        paths_metadata = sorted(glob(os.path.join(path, 'Processing_Data', '*')), key=sortMetadata)
        for path_metadata in paths_metadata:
            print('Loading "%s"...' % path_metadata)

            # TODO: What about totNumFrames?
            metadata = loadmat(path_metadata)
            trials = metadata['totNumTrials'].flat
            cameras = metadata['totCamNum'].flat
            videos = metadata['totVidNum'].flat
            frames_start = metadata['totStartTimes'].flat
            frames_end = metadata['totEndTimes'].flat

            robot_offset = 0.0

            frame_rate = None

            for j in range(len(trials)):
                trial = dataset.trial(trials[j])
                camera = cameras[j]
                video = videos[j]

                # print('Parsing camera #%d into trial #%d' % (camera, trial.id))

                video_paths = sorted(glob(os.path.join(path, 'Camera%d' % camera, 'Renamed_Raw_Data', '*.mp4')))

                robot_start = robot.start_times[trial.id - 1]
                frame_start = frames_start[j]
                frame_end = frames_end[j]

                samples = Samples(camera, robot_start + robot_offset, video_paths[videos[j] - 1], frame_start, frame_end)
                trial.samples[camera] = samples

                frame_rate = 1.0 / samples.video.frame_period

                if isnan(frame_end) and isnan(frame_start):
                    robot_offset += samples.video.frame_period * samples.video.frame_count
                elif isnan(frame_end):
                    robot_offset = samples.video.frame_period * (samples.video.frame_count - frame_start)
                elif isnan(frame_start):
                    robot_offset = 0.0

            for trial in dataset.trials.values():
                robot_start = robot.start_times[trial.id - 1]
                collisions_path = os.path.join(path, 'Collision_Data', 'Trial%d.csv' % trial.id)
                with open(collisions_path, 'r') as collisions_data:
                    for row in csv.reader(collisions_data):
                        frame = round((float(row[0]) - robot_start) * frame_rate)
                        collides = (row[1] == '1')
                        trial.collisions.append((frame, collides))

        return dataset


# URL's for the original raw datasets.
Download.SESSIONS = [
    # Session 1 (2020-10-05)
    Download(
        '2020-10-05',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-1-part-1',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-1-part-2'
    ),
    # Session 2 (2020-10-06)
    Download(
        '2020-10-06',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-2-part-1-c',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-2-part-2'
    ),
    # Session 3 (2020-10-07)
    Download(
        '2020-10-07',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-1',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-2-b',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-3'
    ),
    # Session 4 (2020-10-08)
    Download(
        '2020-10-08',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-1',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-2',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-3'
    ),
    # Session 5 (2020-10-09)
    Download(
        '2020-10-09',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-5-part-1-d',
        'https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-5-part-2'
    )
]
