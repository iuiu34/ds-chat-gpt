FROM python:3.9-slim

RUN pip install --upgrade pip

COPY container/pip_conf.conf /etc/pip.conf

COPY MANIFEST.in model/MANIFEST.in
COPY pyproject.toml model/pyproject.toml
RUN mkdir -p model/tmp

COPY requirements.txt model/requirements.txt
RUN pip install -r model/requirements.txt
#RUN pip install kfp==2.0.1

COPY README.md model/README.md
COPY setup.cfg model/setup.cfg
COPY src/ model/src/

RUN cd model && pip install . && cd ..

# ENTRYPOINT ["bash"]