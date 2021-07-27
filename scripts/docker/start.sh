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

# Start the Docker container.
#
# Author: Helio Perroni Filho

SCRIPT_PATH=$(readlink -f "$0")
export SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

IMAGE='python/canadarm3:cpu'
INTERACTIVE='true'
RESET='false'

# See: https://stackoverflow.com/a/14203146/476920
for i in "$@"
do
  case $i in
    --image=*)
      IMAGE="${i#*=}"
    ;;
    --detached)
      INTERACTIVE='false'
    ;;
    --reset)
      RESET='true'
    ;;
    *)
      echo "Unkwnown option: \""$i'"'
      exit 1
    ;;
  esac
done

NAME=${IMAGE//[:\/]/_}

if [ $RESET == 'true' ]
then
  docker rm $NAME
fi

if [ "$(docker ps -aq -f name=$NAME -f status=exited)" ]
then
  echo "Restarting container..."
  docker restart $NAME
elif [ "$(docker ps -aq -f name=$NAME)" == "" ]
then
  echo "Starting container..."
  docker run -id \
      -e DISPLAY \
      --net=host \
      --privileged \
      --cap-add=ALL \
      --volume="$HOME:/home/user/host" \
      --volume="/dev:/dev" \
      --volume="/lib/modules:/lib/modules" \
      --volume="/media:/media" \
      --volume="/var/run/dbus:/var/run/dbus" \
      --name="$NAME" \
      $IMAGE
fi

if [ $INTERACTIVE == 'false' ]
then
  exit
fi

echo "Connecting to container..."

docker exec -it $NAME /bin/bash

echo "Stopping container..."

docker kill $NAME
