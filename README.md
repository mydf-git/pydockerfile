# mydf/pydockerfile

mydf/pydockerfile is an add on to the Dockerfile syntax focused on building small and fast python images.

Through some simple macros we take care of a lot of Dockerfile boilerplate and help you to be concise and precise.

## Example

    # syntax=mydf/pydockerfile:1
    FROM python
    PYENVS
    APT curl
    PIP requests

is a valid and concise Dockerfile that demonstrates all our features! To test it just copy it to a `Dockerfile` and run `DOCKER_BUILDKIT=1 docker build .`

It will build something equivalent to:

    # syntax=mydf/pydockerfile:1

    FROM python
    ENV PIP_NO_PYTHON_VERSION_WARNING=1 PYTHONDONTWRITEBYTECODE=1
    RUN --mount=type=cache,target=/var/lib/apt,id=apt_lists \
      --mount=type=cache,target=/var/cache/apt,id=apt_archives \
      apt-get update && apt-get install -y curl
    RUN --mount=type=cache,target=/root/.cache/pip/,id=pip pip install \
      requests


## Features

All normal dockerfile syntax apply, but you can also use the following commands (case insensitive):

### `PIP [args]...`

The `PIP` command triggers a `RUN pip install [args]...` but using `--mount=type=cache` flag to
automatically reuse pip cache between builds while also keeping cache files out of your docker image.
It is also shorter to type than `RUN pip install`

### `PIPENVS`

`PIPENVS` is just a fast way to set common python env variables. Now it is equivalent to:

    ENV PIP_NO_PYTHON_VERSION_WARNING=1 PYTHONDONTWRITEBYTECODE=1

### `APT [args]...`

The `APT` command triggers a `RUN apt-get update && apt-get install -y [args]...` but using `--mount=type=cache` flag to
automatically reuse apt cache between builds. It also keeps the cache out of your docker image, reducing its size.
Finally, its also shorter to type. You will never forget that `-y` again :)

## Installing

Custom synaxes are supported in **all docker installations** since 18.09, you just need to
`export DOCKER_BUILDKIT=1` before running your `docker build` commands.

If you use docker-compose then you also need to `export COMPOSE_DOCKER_CLI_BUILD=1`.
I suggest you add these exports to your `~/.bashrc`.

Then, you must add this as the FIRST LINE of your Dockerfile:

    # syntax=mydf/pydockerfile:1

Thats it! Now go on and write some *DRY* Dockerfiles :)

## Debugging

pydockerfile works by preprocessing your Dockerfile into a longer, ["dockerfile:experimental"](https://github.com/moby/buildkit/blob/dockerfile/1.1.7-experimental/frontend/dockerfile/docs/experimental.md)
valid version. If you want to see the intermediary dockerfile that is being generated just run

    docker run --rm -i --entrypoint= mydf:pydockerfile:1 /preprocessor < ./Dockerfile

## Colaboration

I'm very open to suggestions, please leave an issue to open discussions or bug reports!

## Links

Powered by [mydf/mydockerfile](https://github.com/mydf-git/mydockerfile)! A simple way to make a Dockerfile syntax!
