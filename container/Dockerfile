FROM python:3.9-slim

RUN pip install --upgrade pip
RUN pip install --no-input keyrings.google-artifactregistry-auth
COPY container/pip_conf.conf /etc/pip.conf

COPY MANIFEST.in model/MANIFEST.in
COPY pyproject.toml model/pyproject.toml
RUN mkdir -p tmp

COPY requirements.txt model/requirements.txt
RUN pip install -r model/requirements.txt

COPY README.md model/README.md
COPY setup.cfg model/setup.cfg
COPY src/ model/src/

RUN cd model && pip install . && cd ..

# ENTRYPOINT ["bash"]

# app
COPY src/edo/chat_gpt/app app/
RUN mkdir -p app/tmp

WORKDIR app
EXPOSE 8080
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
