# use this image for Windows and Linux
# FROM python:3.11.7-alpine3.18
# use this image for macOS
FROM python:3.11.7-slim

LABEL authors="OleksiyM"

ENV APP_HOME /app

# ENV POETRY_HOME=$APP_HOME/.poetry

WORKDIR $APP_HOME

# COPY pyproject.toml $APP/pyproject.toml
# COPY poetry.lock $APP/poetry.lock

COPY . .

# COPY . $APP_HOME

RUN pip install poetry

#RUN poetry install

RUN poetry config virtualenvs.create false && poetry install --only main

EXPOSE 3000

#CMD ["poetry", "shell"]
#ENTRYPOINT ["python", "main.py"]
CMD poetry shell && python main.py