# Use the official lightweight Python image.
# https://hub.docker.com/_/python
# See:  https://stackoverflow.com/questions/59052104/how-do-you-deploy-a-streamlit-app-on-app-engine-gcp
FROM python:3.7-slim

ENV APP_HOME /app

# Download 
RUN apt-get update && apt-get install -y \
    curl \
    gcc

# TODO: Replace by Docker volume?
RUN mkdir -p ${APP_HOME}/data/bert-large-cased-whole-word-masking-finetuned-squad
RUN curl \
        -o ${APP_HOME}/data/bert-large-cased-whole-word-masking-finetuned-squad/config.json \
        https://s3.amazonaws.com/models.huggingface.co/bert/bert-large-cased-whole-word-masking-config.json

RUN curl \
        -o ${APP_HOME}/data/bert-large-cased-whole-word-masking-finetuned-squad/vocab.txt \
        https://s3.amazonaws.com/models.huggingface.co/bert/bert-large-cased-whole-word-masking-vocab.txt

RUN curl \
        -o ${APP_HOME}/data/bert-large-cased-whole-word-masking-finetuned-squad/tf_model.h5 \
        https://cdn.huggingface.co/bert-large-cased-whole-word-masking-finetuned-squad-tf_model.h5

RUN mkdir -p ${APP_HOME}/data/wietsedv/bert-base-dutch-cased
RUN curl \
        -o ${APP_HOME}/data/wietsedv/bert-base-dutch-cased/config.json \
        https://s3.amazonaws.com/models.huggingface.co/bert/wietsedv/bert-base-dutch-cased/config.json

RUN curl \
        -o ${APP_HOME}/data/wietsedv/bert-base-dutch-cased/vocab.txt \
        https://s3.amazonaws.com/models.huggingface.co/bert/wietsedv/bert-base-dutch-cased/vocab.txt

RUN curl \
        -o ${APP_HOME}/data/wietsedv/bert-base-dutch-cased/tf_model.h5 \
        https://cdn.huggingface.co/wietsedv/bert-base-dutch-cased/tf_model.h5

# Pin python-dateutil for boto errors maybe?
RUN pip install tensorflow transformers streamlit numpy requests gazpacho python-dateutil==2.8.0

ADD . ${APP_HOME}
RUN pip install ${APP_HOME}

# No idea why we need this
ENV PYTHONPATH=/app/src
WORKDIR ${APP_HOME}

# Run the web service on container startup. 
# TODO: Add argument to specify data dir, allowing us to be more dynamic with data/
# TODO: /app/app/app.py is confusing
EXPOSE 8080
CMD streamlit run \
    --server.port 8080 \
    --server.enableCORS false \
    app/app.py
