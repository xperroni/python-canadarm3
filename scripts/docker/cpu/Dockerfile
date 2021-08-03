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

# Build script for the Python environment.
#
# Author: Helio Perroni Filho

FROM ubuntu:18.04

USER root
WORKDIR /
SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Build settings.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=America/Toronto

# Setup the system-wide environment.
ADD setup.sh .
RUN /bin/bash -e -x setup.sh && rm setup.sh

USER user
WORKDIR /home/user
CMD ["jupyter-lab"]

# Enable Bash as the default shell in Jupyter.
ENV SHELL=/bin/bash
