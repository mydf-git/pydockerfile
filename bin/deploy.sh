#!/bin/bash -e
cd $(git rev-parse --show-toplevel)

VERSION=`cat VERSION`
export DOCKER_BUILDKIT=1

./bin/build.sh
./bin/test.sh

docker push mydf/pydockerfile:1
