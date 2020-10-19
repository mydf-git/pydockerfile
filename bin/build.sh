#!/bin/bash
cd $(git rev-parse --show-toplevel)

VERSION=1

docker build . -t mydf/pydockerfile:$VERSION
