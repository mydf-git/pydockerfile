FROM mydf/mydockerfile:1 AS mydockerfile

FROM python:alpine
ENTRYPOINT /dockerfile-frontend
COPY --from=mydockerfile /bin/dockerfile-frontend /dockerfile-frontend
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY ./preprocessor.py /preprocessor
