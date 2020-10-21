#!/bin/bash -e
cd $(git rev-parse --show-toplevel)

VERSION=`cat VERSION`

docker build . -t mydf/pydockerfile:$VERSION --squash
