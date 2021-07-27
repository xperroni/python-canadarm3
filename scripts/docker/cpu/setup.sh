#!/bin/bash

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

# Setup the system-wide environment.
#
# Author: Helio Perroni Filho

# Update system and install basic utilities.
apt update && apt upgrade -y
apt install -y \
  nano \
  sudo

# Create default user with passwordless sudo permission.
useradd -ms /bin/bash user
chown user -R /home/user
echo "user"' ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Install Python pacckages.
apt install -y \
  python3-numpy \
  python3-opencv \
  python3-scipy \
  python3-pip

python3 -m pip install --upgrade pip
python3 -m pip install av
