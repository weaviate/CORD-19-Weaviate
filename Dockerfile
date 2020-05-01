FROM python:3

ARG WEAVIATE_URL

COPY . ./
# COPY ./CORD-19-research-challenge ./CORD-19-research-challenge

RUN git clone https://github.com/semi-technologies/weaviate-cli && \
    cd weaviate-cli && \
    pip3 install -r requirements.txt && \
    cd ..

RUN pip3 install -r requirements.txt

RUN ./weaviate-cli/bin/weaviate-cli schema-import --location=schema.json

CMD [ "python", "./import", "${WEAVIATE_URL}", "./CORD-19-research-challenge" ]