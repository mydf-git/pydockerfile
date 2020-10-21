#!/bin/bash -e
cd $(git rev-parse --show-toplevel)

export DOCKER_BUILDKIT=1

docker build -f tests/end2end.dockerfile . -t test
docker run --rm test bash -c "python -c 'import requests' && which ncdu && echo ALL OK!"
