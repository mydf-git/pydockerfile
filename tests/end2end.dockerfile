# syntax=mydf/pydockerfile:1
FROM python
PYENVS
APT ncdu
PIP requests
