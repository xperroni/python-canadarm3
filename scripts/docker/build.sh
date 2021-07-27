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

# Build a Docker image containing base software for running Python scripts.
#
# Author: Helio Perroni Filho

VARIANT='cpu'

# See: https://stackoverflow.com/a/14203146/476920
for i in "$@"
do
  case $i in
    --name=*)
      NAME="${i#*=}"
    ;;
    --email=*)
      EMAIL="${i#*=}"
    ;;
    --variant=*)
      VARIANT="${i#*=}"
    ;;
    *)
      echo "Unkwnown option: \""$i'"'
      exit
    ;;
  esac
done

SCRIPT_PATH=$(readlink -f "$0")
export SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

cd "$SCRIPT_DIR/$VARIANT"
docker build -t python/canadarm3:$VARIANT .
