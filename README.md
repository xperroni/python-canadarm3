# python-canadarm3

Python utilities to manipulate the MDA TRaining AI Laboratory (TRAIL) Canadarm3 Collision Avoidance dataset.

[Canadarm3](https://www.asc-csa.gc.ca/eng/canadarm3/about.asp) "will be Canada's contribution to the US-led Gateway, a lunar outpost that will enable sustainable human exploration of the Moon". It is under development by [MDA](https://mda.space/), building upon its experience with the Canadarm2 currently aboard the International Space Station (ISS).

One important requirement in the Canadarm3 project is [autonomous operation](https://www.nasaspaceflight.com/2021/06/canadarm3-ai-sought/). The Gateway space station it will service is expected to be crewed for only one month per year, with as little as 8 hours per week of communication with Earth. In particular, the system must be able to automatically identify and avoid ostacles while performing its tasks.

In order to enable independent researchers to investigate the problem of obstacle avoidance in the context of the Canadarm3 project, MDA released the [TRaining AI Laboratory (TRAIL) Canadarm3 Collision Avoidance dataset](https://www.kaggle.com/mdaspace/datasets) on Kaggle. The dataset covers five test sessions, each divided in two or more archives due to size constraints:

* Session 1 (2020-10-05)
    * [Part 1](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-1-part-1)
    * [Part 2](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-1-part-2)
* Session 2 (2020-10-06)
    * [Part 1](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-2-part-1-c)
    * [Part 2](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-2-part-2)
* Session 3 (2020-10-07)
    * [Part 1](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-1)
    * [Part 2](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-2-b)
    * [Part 3](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-3-part-3)
* Session 4 (2020-10-08)
    * [Part 1](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-1)
    * [Part 2](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-2)
    * [Part 3](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-4-part-3)
* Session 5 (2020-10-09)
    * [Part 1](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-5-part-1-d)
    * [Part 2](https://www.kaggle.com/mdaspace/canadarm3-collision-avoidance-day-5-part-2)

The original archives include pre-processing Matlab scripts to help parse the data. However, nowadays the AI community at large is more familiar with Python, and would benefit from the availability of tools in that language. This repository aims to provide those tools.

## Contents

This repository contains:

* Bash scripts for setting up a development environment in Docker;
* A Python API for dataset access and visualization;
* An IPython notebook demonstrating how the API can be used to perform various dataset manipulation tasks.

All features are in various stages of early work. [Let me know](https://github.com/xperroni/python-canadarm3/issues) if you run into any issues.

## Installation

Make sure you have both `git` and `git-lfs` installed.

Clone the repository to your local environment, e.g.:

    $ git clone https://github.com/xperroni/python-canadarm3.git

If Docker isn't installed yet, install it with:

    $ ./scripts/setup_host.sh

Restart your system afterwards to enable changes.

To create the development environment inside a Docker container, enter:

    $ ./scripts/docker/build.sh

To start the Docker environment, enter:

    $ ./scripts/docker/start.sh

The Docker container will launch [JupyterLab](https://jupyter.org/) on startup. Access the web interface on your browser through `http://localhost:8888/` or the URL printed in the console. The interface includes a terminal emulator running Bash.

The start script maps the host `$HOME` directory as `$HOME/host` inside the container. Assuming the path to the local repository is `$HOME/Projects/python-canadarm3`, it's possible to `cd` into it from the container with:

    $ cd $HOME/host/Projects/python-canadarm3

The file system can also be navigated through JupyterLab's file manager.

## Usage

Open notebook `src/tutorial.ipynb` for a self-explanatory tutorial.

## References

* [MDA - Canadarm3 collision avoidance datasets](https://www.kaggle.com/mdaspace/datasets)
* [MDA - May 13 2021 - TRAIL Dataset Webinar](https://youtu.be/il8gf4H-jFE)
* [TRAIL Dataset Webinar – Collision Avoidance Dataset](https://www.amii.ca/events/trail-webinar-collision-avoidance-dataset/)
* [AI & the Canadarm3: TRAIL Collision Avoidance Dataset Webinar Recap](https://www.amii.ca/latest-from-amii/trail-collision-avoidance-dataset-webinar-recap/)
