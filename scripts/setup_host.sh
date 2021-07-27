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

# Install host-side dependencies.
#
# Author: Helio Perroni Filho

# Show commands as they're executed, exit on error.
set -x -e

# Install basic utilities.
sudo apt update
sudo apt install -y \
  curl \
  git-lfs \
  gnupg-agent \
  software-properties-common

# Setup access to the Docker package repository.
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo apt-key fingerprint 0EBFCD88
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update the system package index.
sudo apt update

# Install Docker.
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Add the current user to the docker group.
sudo usermod -aG docker $USER

echo "Reboot to bring changes into effect."
