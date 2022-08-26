FROM python:3.10

# Install Chrome
RUN apt-get install -y wget
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install ./google-chrome-stable_current_amd64.deb

# Intall Poetry
RUN pip install "poetry==1.1.13"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-dev --no-interaction --no-ansi

COPY . /code

CMD [ "python", "./code/app/main.py" ]
