FROM python:3.9-slim AS builder

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

COPY src/edo/chat_gpt/app app/
RUN mkdir -p app/tmp

FROM nginx:alpine

COPY --from=builder /app /app
COPY --from=builder /etc/pip.conf /etc/pip.conf

COPY container/nginx.conf /etc/nginx/conf.d/default.conf

WORKDIR /app
EXPOSE 8080
CMD ["sh", "-c", "streamlit run app.py --server.port=8501 --server.address=0.0.0.0 & nginx -g 'daemon off;'"]